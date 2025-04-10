import os
import asyncio
import yfinance as yf
import pandas as pd
from typing import List

def get_data_file_path(datestamp: str, file_name: str):
    root_dir = os.path.dirname(os.path.abspath(os.getcwd()))
    data_dir = os.path.join(root_dir, 'data')
    os.makedirs(data_dir, exist_ok=True)
    file_path = os.path.join(data_dir, f"{file_name}_{datestamp}.parquet")

    return file_path

async def fetch_stock_data(ticker, name) -> pd.DataFrame:
    '''Fetch data for a ticker and returns a DataFrame'''
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period='1d', interval='60m')
        if data.empty:
            print(f"{ticker}: No data found")
            return None
        
        data = data.reset_index()
        data["symbol"] = ticker
        data["name"] = name
        return data
    
    except Exception as e:
        print(f"An error occured while pulling data for {ticker}: {e}")
        return None
    
async def fetch_all_stocks(tickers: pd.DataFrame) -> List[pd.DataFrame]:
    '''Fetch data for all tickers and return as a list of DataFrames'''

    # Use Semaphore to limit rate-limiting/IP blocking
    semaphore = asyncio.Semaphore(5)
    async def fetch_with_semaphore(ticker, name):
        async with semaphore: 
            return await fetch_stock_data(ticker, name)
    
    tasks = [
        asyncio.create_task(fetch_with_semaphore(ticker["symbol"], ticker["name"]))
        for _, ticker in tickers.iterrows()
    ]

    results = []
    for stock in asyncio.as_completed(tasks):
        result = await stock
        if result is not None:
            ticker = result["symbol"].iloc[0]
            print(f"Fetched {ticker}: {len(result)} rows")
            results.append(result)
            
        else:
            print(f"Skipped ticker, no valid data retrieved.")

    return results