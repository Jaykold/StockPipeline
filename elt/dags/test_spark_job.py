from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator # type: ignore
from airflow.decorators import dag, task
from airflow.hooks.base import BaseHook
from airflow.operators.email import EmailOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from datetime import datetime, timedelta
from pendulum import timezone

dag_timezone = timezone("America/New_York")

default_args = {
    "owner": "Christian",
    "start_date": datetime(2025, 4, 4, tzinfo=dag_timezone),
    "catchup": False,
    "email_on_failure": True,
    "retries": 3,
    "retry_delay": timedelta(minutes=2)
}

# Retrieve connection strings
conn_1 = BaseHook.get_connection('az_datalake_conn')
acc_name = conn_1.host
container_name = conn_1.extra_dejson.get('container_name')

conn_2 = BaseHook.get_connection('service_principal_conn') 
app_id = conn_2.extra_dejson.get('SP_APP_ID')
secret_id = conn_2.extra_dejson.get('SP_SECRET_ID')
tenant_id = conn_2.extra_dejson.get('SP_TENANT_ID')

@dag(
    dag_id="spark_job_dag",
    default_args=default_args,
    schedule_interval="0 13 * * Mon-Fri",
    description="Run a Spark job using Airflow",
    template_searchpath=['/opt/airflow/sql'],
    tags=["MuadDib"]
)

def spark_job_dag():
    '''Run a Spark job using Airflow'''
    python_job = SparkSubmitOperator(
        task_id="spark_job",
        application="/opt/airflow/scripts/spark_job.py",
        conn_id="spark-conn",
        verbose=True,
        packages="org.apache.hadoop:hadoop-azure:3.3.4,com.microsoft.sqlserver:mssql-jdbc:12.10.0.jre11,com.microsoft.azure:azure-storage:8.6.6",
        conf={
            # Azure Data Lake Storage Gen2 authentication (Service Princial)
            f"spark.hadoop.fs.azure.account.auth.type.{acc_name}.dfs.core.windows.net": "OAuth",
            f"spark.hadoop.fs.azure.account.oauth.provider.type.{acc_name}.dfs.core.windows.net": "org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider",
            f"spark.hadoop.fs.azure.account.oauth2.client.id.{acc_name}.dfs.core.windows.net": app_id,
            f"spark.hadoop.fs.azure.account.oauth2.client.secret.{acc_name}.dfs.core.windows.net": secret_id,
            f"spark.hadoop.fs.azure.account.oauth2.client.endpoint.{acc_name}.dfs.core.windows.net": f"https://login.microsoftonline.com/{tenant_id}/oauth2/token",
        },
        env_vars={
            "ACC_NAME": acc_name,
            "CONTAINER_NAME": container_name,
        }
    )

    # SQL Server connection
    create_partition = SQLExecuteQueryOperator(
        task_id="create_partition",
        conn_id="az_sql_conn",
        sql=r"""
            CREATE PARTITION FUNCTION pf_StockDataByDate (DATETIME)
            AS RANGE RIGHT FOR VALUES (
                '2025-01-01', '2025-04-01', '2025-07-01', '2025-10-01'
            );
        """,
        autocommit=True
    )

    create_partition_scheme = SQLExecuteQueryOperator(
        task_id = "create_partition_scheme",
        conn_id="az_sql_conn",
        sql=r"""
            IF NOT EXISTS (SELECT * FROM sys.partition_schemes WHERE name = 'ps_StockDataByDate')
            BEGIN
                CREATE PARTITION SCHEME ps_StockDataByDate
                AS PARTITION pf_StockDataByDate ALL TO ([PRIMARY]);
            END
            ELSE
            BEGIN
                PRINT 'Partition scheme ps_StockDataByDate already exists.';
            END;
        """,
        autocommit=True
    )

    create_table = SQLExecuteQueryOperator(
        task_id="create_table",
        conn_id="az_sql_conn",
        sql=r"""
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'StockData')
            BEGIN
                CREATE TABLE StockData (
                    UniqueID CHAR(64), -- SHA-256 hash of relevant columns
                    Datetime DATETIME, -- Date and time of the stock data
                    symbol VARCHAR(10), -- Stock symbol
                    name VARCHAR(255), -- Stock name
                    Open FLOAT, -- Opening price
                    Close FLOAT, -- Closing price
                    High FLOAT, -- Highest price of the day
                    Low FLOAT, -- Lowest price of the day
                    Volume BIGINT, -- Trading volume
                    CONSTRAINT PK_StockData PRIMARY KEY (UniqueID) -- Primary key on UniqueID
                ) ON ps_StockDataByDate(Datetime); -- Partitioning on the Datetime column
            END
            ELSE
            BEGIN
                PRINT 'Table StockData already exists.';
            END;
        """,
        autocommit=True
    )

    send_email_task = EmailOperator(
    task_id='send_email',
    to='jaykold@outlook.com',
    subject='Data loaded to Azure Data Lake',
    html_content='<h3>Successfully ran the Spark Job </h3>'
    )

    python_job >> create_partition >> create_partition_scheme >> create_table >> send_email_task

spark_job_dag()