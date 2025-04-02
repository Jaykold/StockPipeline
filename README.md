# Stock Data Pipeline

An end-to-end data engineering project that extracts stock data from Yahoo Finance, loads it to Azure Data Lake Storage (ADLS), transforms it with PySpark, and loads it to Azure SQL Server.

## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Technologies Used](#technologies-used)
- [Setup and Installation](#setup-and-installation)
- [Usage](#usage)
- [Pipeline Details](#pipeline-details)
- [License](#license)

## Overview

This project implements a complete ETL (Extract, Transform, Load) pipeline for stock market data. It extracts hourly stock data for major companies, processes it, and stores it in a structured format for analysis.

## Preprequisite
- Docker desktop, docker compose
- Active azure subscription
- Terraform installed
 - [Download your OS version here](https://developer.hashicorp.com/terraform/install)
- Create a terraform.tfvars for sensitive information

```
client_ip_address = <YOUR_IP_ADDRESS> # https://whatismyipaddress.com/
sql_admin_username = <YOUR_MSSQL_USERNAME>
sql_admin_password = <YOUR_MSSQL_PASSWORD>
resource_group_location = <YOUR_LOCATION> # "East US", "UK West", "North Europe"
```

- Insert these with your details into your .env file for docker-compose
```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_actual_email@gmail.com
SMTP_PASSWORD=your_actual_password
SMTP_MAIL_FROM=your_actual_email@gmail.com
SMTP_STARTTLS=True
SMTP_SSL=False
```

## Architecture

![Architecture Diagram](https://via.placeholder.com/800x400?text=Stock+Data+Pipeline+Architecture)

The pipeline follows this workflow:
1. **Extract** - Fetch company data and stock prices from Yahoo Finance
2. **Load** - Store raw data in Azure Data Lake Storage
3. **Transform** - Process data using PySpark
4. **Load** - Store transformed data in Azure SQL Server with appropriate partitioning

## Technologies Used

- **Python 3.10** - Core programming language
- **Apache Airflow** - Workflow orchestration
- **Selenium** - Web scraping
- **yfinance** - Yahoo Finance API
- **Azure Data Lake Storage** - Cloud storage for raw and processed data
- **Azure Identity** - Authentication with Azure services
- **PySpark** - Distributed data processing
- **Azure SQL Server** - Data warehouse
- **Pandas & PyArrow** - Data manipulation and storage

## Setup and Installation

1. Clone the repository
2. Set up a Python 3.10 virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
3. pip install -r requirements.txt

## Create a .env file with the following variables
```
EDGE_DRIVER_PATH=<path_to_edge_driver>
ADLS_CONTAINER=<container_name>
ADLS_ACCNAME=<account_name>
ADLS_ACCKEY=<account_key>
SP_APP_ID=<service_principal_app_id>
SP_TENANT_ID=<service_principal_tenant_id>
SP_SECRET_ID=<service_principal_secret_id>
```
