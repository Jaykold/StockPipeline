/* This SQL file creates a staging table for stock data in Azure SQL Server.
   The staging table is used to temporarily hold data before it is loaded into the final table. */

-- Create staging table if it does not exist
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'StockData_Staging')
BEGIN
    CREATE TABLE StockData_Staging (
        UniqueID CHAR(64), -- SHA-256 hash of relevant columns
        Datetime DATETIME, -- Date and time of the stock data
        symbol VARCHAR(10) NOT NULL, -- Stock symbol
        name VARCHAR(255) NOT NULL, -- Stock name
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