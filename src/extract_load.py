import os
import asyncio
import yfinance as yf
from time import perf_counter
import pandas as pd
from datetime import datetime

def get_data_file_path(datestamp: str, file_name: str):
    root_dir = os.path.dirname(os.path.abspath(os.getcwd()))
    data_dir = os.path.join(root_dir, 'data')
    os.makedirs(data_dir, exist_ok=True)
    file_path = os.path.join(data_dir, f"{file_name}_{datestamp}.parquet")

    return file_path

async def fetch_stock_data(ticker, name):
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
    
async def fetch_all_stocks(tickers: pd.DataFrame):
    current_date = datetime.now().strftime("%Y%m%d")
    
    tasks = [
        asyncio.create_task(fetch_stock_data(ticker["symbol"], ticker["name"]))
        for _, ticker in tickers.iterrows()
    ]

    for stock in asyncio.as_completed(tasks):
        result = await stock
        if result is not None:
            ticker = result["symbol"].iloc[0]
            file_path = get_data_file_path(current_date, ticker)
            result.to_parquet(file_path, index=False)
            print(f"Saved {ticker} to {file_path}: {len(result)} rows")
        else:
            print(f"Skipped saving data for ticker, no valid data retrieved.")
    
async def main():
    start_time = perf_counter()
    print(f"Starting fetch at {start_time}")
    
    ticker_df = pd.read_csv("../data/companies.csv")
    
    await fetch_all_stocks(ticker_df)

    end_time = perf_counter()
    print(f"Completed at {end_time}, Took {end_time - start_time}")

if __name__=="__main__":
    asyncio.run(main())
    