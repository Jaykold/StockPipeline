from scripts import fetch_all_stocks, auth_datalake, upload_file_to_datalake
import asyncio
from utils import ACC_NAME, ACC_KEY, CONTAINER_NAME 
from time import perf_counter
import pandas as pd

async def main():
    start_time = perf_counter()
    print(f"Starting fetch at {start_time}")
    
    tickers_df = pd.read_csv("data/companies.csv")
    
    results = await fetch_all_stocks(tickers_df)
    service_client = auth_datalake(acc_name=ACC_NAME, acc_key=ACC_KEY)
    upload_file_to_datalake(results, service_client, CONTAINER_NAME)

    end_time = perf_counter()
    print(f"Completed at {end_time}, Took {end_time - start_time}")

if __name__=="__main__":
    asyncio.run(main())