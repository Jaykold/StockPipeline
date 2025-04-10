MERGE INTO StockData AS target
USING StockData_Staging AS source
ON target.RecordHash = source.RecordHash
WHEN NOT MATCHED THEN
    INSERT (RecordHash, Datetime, symbol, name, [Open], High, Low, [Close], Volume)
    VALUES (source.RecordHash, source.Datetime, source.symbol, source.name, source.[Open], source.High, source.Low, source.[Close], source.Volume);