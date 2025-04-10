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