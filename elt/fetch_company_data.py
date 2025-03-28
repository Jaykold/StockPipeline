'''This file fetches company data from Yahoo Finance and saves it to a CSV file.
It uses Selenium to automate the web browser and extract the required information.
The script is designed to work with Microsoft Edge WebDriver.
It is important to ensure that the WebDriver version matches the installed version of Microsoft Edge.'''

import os
from dags.utils import EDGE_DRIVER_PATH
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.options import Options
import csv
import time

def fetch_company_data():    
    try:
        edge_options = Options()
        edge_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        service = Service(EDGE_DRIVER_PATH)

        # Initialize the Edge WebDriver with the updated syntax
        driver = webdriver.Edge(options=edge_options, service=service)

        driver.get("https://finance.yahoo.com/research-hub/screener/equity/")

        # Wait for the toggle button to be clickable
        toggle_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.tertiary-btn.fin-size-small.menuBtn.rounded.rightAlign"))
        )
        # Click the toggle button
        toggle_button.click()

        try:
            # Wait for the option to be clickable
            option_50 = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "div[data-value='50']"))
            )
            # Click the option
            option_50.click()
            time.sleep(2)

        except Exception as e:
            print("Error:", e)
            driver.quit()

        # Get the rows of the table
        rows = driver.find_elements(By.CSS_SELECTOR, "tr.row.yf-umfm46")
        print(f"Found {len(rows)} rows")

        data = []

        for row in rows:
            try:
                symbol = row.find_element(By.CSS_SELECTOR, "span.symbol.yf-1fqyif7").text.strip()
                name = row.find_element(By.CSS_SELECTOR, "div.tw-text-left.tw-max-w-32.yf-362rys").text.strip()

                data.append({
                    "symbol": symbol,
                    "name": name
                })
                time.sleep(0.5)
            except Exception as e:
                print(f"Error extracting data from row: {e}")
                continue
        return data
    
    except Exception as e:
        print(f"An error occurred: {e}")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    data = fetch_company_data()
    if data:
        print(f"Found {len(data)} company symbols and names")
    else:
        print("No symbols found. The website structure might have changed.")

    root_dir = os.path.dirname(os.path.abspath(os.getcwd()))
    data_dir = os.path.join(root_dir, 'data')
    os.makedirs(data_dir, exist_ok=True)
    file_path = os.path.join(data_dir, 'companies.csv')

    with open(file_path, 'w', newline='', encoding='utf-8') as file_in:
        writer = csv.DictWriter(file_in, fieldnames=['symbol', 'name'])
        writer.writeheader()
        for row in data:
            writer.writerow(row)