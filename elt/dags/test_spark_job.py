from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator # type: ignore
from airflow.decorators import dag, task
from airflow.hooks.base import BaseHook
from airflow.operators.email import EmailOperator
from airflow.providers.microsoft.mssql.operators.mssql import MsSqlOperator
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
conn_1 = BaseHook.get_connection('az_datalake_connection')
acc_name = conn_1.host
container_name = conn_1.extra_dejson.get('container_name')

conn_2 = BaseHook.get_connection('service_principal_connection') 
app_id = conn_2.extra_dejson.get('SP_APP_ID')
secret_id = conn_2.extra_dejson.get('SP_SECRET_ID')
tenant_id = conn_2.extra_dejson.get('SP_TENANT_ID')

@dag(
    dag_id="spark_job_dag",
    default_args=default_args,
    schedule_interval="0 13 * * Mon-Fri",
    description="Run a Spark job using Airflow",
    tags=["MuadDib"]\
)
#com.microsoft.azure:azure-storage:8.6.6
def spark_job_dag():
    '''Run a Spark job using Airflow'''
    python_job = SparkSubmitOperator(
        task_id="spark_job",
        application="dags/scripts/spark_job.py",
        conn_id="spark-conn",
        verbose=True,
        packages="org.apache.hadoop:hadoop-azure:3.3.4,com.microsoft.sqlserver:mssql-jdbc:12.10.0.jre11",
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
    create_table = MsSqlOperator(
        task_id="create_table",
        mssql_conn_id="azure_sql_conn",
        sql="sql/create_table.sql",
        autocommit=True,
    )

    send_email_task = EmailOperator(
    task_id='send_email',
    to='jaykold@outlook.com',
    subject='Data loaded to Azure Data Lake',
    html_content='<h3>Successfully ran the Spark Job </h3>'
    )

    python_job >> create_table >> send_email_task

spark_job_dag()