/* This script creates a table in Azure SQL Server with partitioning based on the Datetime column.
   The table is designed to store stock data with various attributes. */

-- Create table with partitioning or check if it exists
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'StockData')
BEGIN
    CREATE TABLE StockData (
        UniqueID CHAR(64), -- SHA-256 hash of relevant columns
        Datetime DATETIME, -- Date and time of the stock data
        symbol VARCHAR(10), -- Stock symbol
        name VARCHAR(255), -- Stock name
        [Open] FLOAT, -- Opening price
        [Close] FLOAT, -- Closing price
        High FLOAT, -- Highest price of the day
        Low FLOAT, -- Lowest price of the day
        Volume BIGINT, -- Trading volume
        CONSTRAINT PK_StockData PRIMARY KEY (Datetime, UniqueID) -- Primary key on UniqueID
    ) ON ps_StockDataByDate(Datetime); -- Partitioning on the Datetime column
END
ELSE
BEGIN
    PRINT 'Table StockData already exists.';
END;
