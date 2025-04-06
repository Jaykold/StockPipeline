from airflow.decorators import task, dag
from airflow.hooks.base import BaseHook
from airflow.operators.email import EmailOperator
from datetime import datetime, timedelta
import asyncio
import pandas as pd
from pendulum import timezone

from scripts import fetch_all_stocks, auth_datalake, upload_file_to_datalake


# Retrieve connection strings
conn = BaseHook.get_connection('az_datalake_connection')
ACC_NAME = conn.host
ACC_KEY = conn.password
CONTAINER_NAME = conn.extra_dejson.get('container_name')

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
    "load to Azure DataLake, Transform with PySpark and push to Azure SQL Server")
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
    
    send_email_task = EmailOperator(
    task_id='send_email',
    to='jaykold@outlook.com',
    subject='Data loaded to Azure Data Lake',
    html_content='<h3>Data loaded successfully to Azure Data Lake</h3>'
    )

    dataframes = extract()
    load_task = load(dataframes)

    load_task >> send_email_task

elt_dag()