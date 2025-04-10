IF NOT EXISTS (SELECT * FROM sys.partition_schemes WHERE name = 'ps_StockDataByDate')
BEGIN
    CREATE PARTITION SCHEME ps_StockDataByDate
    AS PARTITION pf_StockDataByDate ALL TO ([PRIMARY]);
END
ELSE
BEGIN
    PRINT 'Partition scheme ps_StockDataByDate already exists.';
END;