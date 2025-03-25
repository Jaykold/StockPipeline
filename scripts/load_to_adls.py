from azure.storage.filedatalake import DataLakeServiceClient
from typing import List
import pandas as pd
from datetime import datetime

def auth_datalake(acc_name: str, acc_key: str):
    '''Initialize Service Client'''
    try:
        service_client = DataLakeServiceClient(
            account_url = f"https://{acc_name}.dfs.core.windows.net",
            credential = acc_key
        )
        print('Authenticating with Azure Data Lake')
    
        return service_client
    
    except Exception as e:
        print(f"Authentication failed: {e}")
        raise

def upload_file_to_datalake(
        dataframes: List[pd.DataFrame],
        service_client,
        container_name: str
        ):
    '''Gets the service client and loads raw data into Azure Datalake'''
    current_time = datetime.now().strftime("%Y%m%d")
    
    # Get container
    file_system_client = service_client.get_file_system_client(container_name)
    
    try:
        for df in dataframes:
            ticker = df["symbol"].iloc[0] # AAPL, AAPL, AAPL | based on the logic for pulling hourly stock data from yahoo finance
            blob_path = f"raw/company_data/{ticker}_{current_time}.parquet"
            parquet_buffer = df.to_parquet(index=False)
    
            # Upload to ADLS
            file_client = file_system_client.get_file_client(blob_path)
            file_client.upload_data(parquet_buffer, overwrite=True)
            print(f"File uploaded successfully to {blob_path}")

    except Exception as e:
        print(f"Error occurred while uploading: {e}")