import os
import sys
from airflow.decorators import task, dag
from airflow.hooks.base import BaseHook
from airflow.operators.email import EmailOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from datetime import datetime, timedelta
import asyncio
import pandas as pd
from pendulum import timezone

sys.path.append(os.path.dirname(os.path.dirname((os.path.abspath(__file__)))))
                
from scripts import fetch_all_stocks, auth_datalake, upload_file_to_datalake


# Retrieve connection strings
conn = BaseHook.get_connection('az_datalake_connection')
ACC_NAME = conn.host
ACC_KEY = conn.password
CONTAINER_NAME = conn.extra_dejson.get('container_name')

conn_2 = BaseHook.get_connection('service_principal_connection') 
APP_ID = conn_2.extra_dejson.get('SP_APP_ID')
SECRET_ID = conn_2.extra_dejson.get('SP_SECRET_ID')
TENANT_ID = conn_2.extra_dejson.get('SP_TENANT_ID')

# Set timezone to Eastern Time to match the stock market hours
# Note: This is important for scheduling the DAG
dag_timezone = timezone("America/New_York")

# retrieve the tickers from the CSV file
tickers_df = pd.read_csv("../data/companies.csv")

default_args = {
    "owner": "Christian",
    "start_date": datetime(2025, 3, 26, tzinfo=dag_timezone),
    "email_on_failure": True,
    "retries": 3,
    "retry_delay": timedelta(minutes=2),
}

@dag(
    dag_id="ELT",
    default_args=default_args,
    schedule_interval="0 18 * * Mon-Fri",
    description=("Extract stock data from Yahoo Finance,"
    "load to Azure DataLake, Transform with PySpark and push to Azure SQL Server"),
    catchup=False,
    tags=["MuadDib"]
)

def elt_dag():
    
    @task
    def extract()-> list[pd.DataFrame]:
        '''Extract stock data from Yahoo Finance'''
        return asyncio.run(fetch_all_stocks(tickers_df))
    
    @task
    def load(dataframes: list[pd.DataFrame]):
        '''Authenticate and upload data to Azure DataLake'''
        service_client = auth_datalake(ACC_NAME, ACC_KEY)
        upload_file_to_datalake(dataframes, service_client, CONTAINER_NAME)
    

    spark_job = SparkSubmitOperator(
        task_id="spark_job",
        application="dags/scripts/spark_job.py",
        conn_id="spark-conn",
        verbose=True,
        packages="org.apache.hadoop:hadoop-azure:3.3.4,com.microsoft.sqlserver:mssql-jdbc:12.10.0.jre11,com.microsoft.azure:azure-storage:8.6.6",
        conf={
            # Azure Data Lake Storage Gen2 authentication (Service Princial)
            f"spark.hadoop.fs.azure.account.auth.type.{ACC_NAME}.dfs.core.windows.net": "OAuth",
            f"spark.hadoop.fs.azure.account.oauth.provider.type.{ACC_NAME}.dfs.core.windows.net": "org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider",
            f"spark.hadoop.fs.azure.account.oauth2.client.id.{ACC_NAME}.dfs.core.windows.net": APP_ID,
            f"spark.hadoop.fs.azure.account.oauth2.client.secret.{ACC_NAME}.dfs.core.windows.net": SECRET_ID,
            f"spark.hadoop.fs.azure.account.oauth2.client.endpoint.{ACC_NAME}.dfs.core.windows.net": f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/token",
        },
        env_vars={
            "ACC_NAME": ACC_NAME,
            "CONTAINER_NAME": CONTAINER_NAME,
        }
    )

    create_partition = SQLExecuteQueryOperator(
        task_id="create_partition",
        conn_id="azure_sql_conn",
        sql="create_partition.sql",
        autocommit=True,
    )

    create_partition_scheme = SQLExecuteQueryOperator(
        task_id="create_partition_scheme",
        conn_id="azure_sql_conn",
        sql="create_partition_scheme.sql",
        autocommit=True,
    )

    create_table = SQLExecuteQueryOperator(
        task_id="create_table",
        conn_id="azure_sql_conn",
        sql="create_table.sql",
        autocommit=True,
    )

    create_staging_table = SQLExecuteQueryOperator(
        task_id="create_staging_table",
        conn_id="azure_sql_conn",
        sql="create_staging_table.sql",
        autocommit=True,
    )

    upsert_job = SQLExecuteQueryOperator(
        task_id="uspert_stock_data",
        conn_id="azure_sql_conn",
        sql="upsert_stock_data.sql",
        autocommit=True,
    )

    send_email_task = EmailOperator(
    task_id='send_email',
    to='jaykold@outlook.com',
    subject='Data loaded to Azure Data Lake',
    html_content='<h3>Data loaded successfully to Azure Data Lake</h3>'
    )

    dataframes = extract()
    load_task = load(dataframes)

    load_task >> create_partition >> create_partition_scheme >> create_table \
        >> create_staging_table >> spark_job >> upsert_job >> send_email_task

elt_dag()