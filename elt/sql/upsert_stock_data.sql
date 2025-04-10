INSERT INTO StockData (UniqueID, Datetime, symbol, name, [Open], High, Low, [Close], Volume)
SELECT source.UniqueID, source.Datetime, source.symbol, source.name, source.[Open], 
       source.High, source.Low, source.[Close], source.Volume
FROM StockData_Staging source
WHERE NOT EXISTS (
    SELECT 1 
    FROM StockData target 
    WHERE target.UniqueID = source.UniqueID 
    AND target.Datetime = source.Datetime
);