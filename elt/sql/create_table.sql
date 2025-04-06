/* This script creates a table in Azure SQL Server with partitioning based on the Datetime column.
   The table is designed to store stock data with various attributes. */

-- Create a partition function and scheme for the StockData table
IF NOT EXISTS (SELECT * FROM sys.partition_functions WHERE name = 'pf_StockDataByDate')
BEGIN
    CREATE PARTITION FUNCTION pf_StockDataByDate (DATETIME)
    AS RANGE RIGHT FOR VALUES (
        '2025-01-01', '2025-04-01', '2025-07-01', '2025-10-01'
    );
END
ELSE
BEGIN
    PRINT 'Partition function pf_StockDataByDate already exists.';
END;

IF NOT EXISTS (SELECT * FROM sys.partition_schemes WHERE name = 'ps_StockDataByDate')
BEGIN
    CREATE PARTITION SCHEME ps_StockDataByDate
    AS PARTITION pf_StockDataByDate ALL TO ([PRIMARY]);
END
ELSE
BEGIN
    PRINT 'Partition scheme ps_StockDataByDate already exists.';
END;

-- Create table with partitioning or check if it exists
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