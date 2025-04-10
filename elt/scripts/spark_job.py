import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, round, sha2, concat_ws
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, LongType, TimestampType


ACC_NAME = os.getenv("ACC_NAME")
CONTAINER_NAME = os.getenv("CONTAINER_NAME")

schema = StructType([
    StructField("Datetime", TimestampType(), False),
    StructField("Open", DoubleType(), True),
    StructField("High", DoubleType(), True),
    StructField("Low", DoubleType(), True),
    StructField("Close", DoubleType(), True),
    StructField("Volume", LongType(), True),
    StructField("Dividends", DoubleType(), True),
    StructField("Stock Splits", DoubleType(), True),
    StructField("symbol", StringType(), True), 
    StructField("name", StringType(), True)
])

spark = SparkSession.builder \
    .appName("Azure Data Lake Storage") \
    .getOrCreate() 

file_path = f"abfss://{CONTAINER_NAME}@{ACC_NAME}.dfs.core.windows.net/raw/company_data/*.csv"

try:
    df = spark.read.csv(file_path, header=True, schema=schema)
    df.printSchema()
    
    df = df.withColumn(
            "unique_id",
            sha2(
                concat_ws(
                    "",
                    col("Datetime"),
                    col("symbol"),
                    col("Open"),
                    col("Close")),
                256,    
                )
        )
    
    transformed_df = df.select(
        col("unique_id"),
        col("Datetime"),
        col("symbol"),
        col("name"),
        round(col("Open"), 2).alias("Open"),
        round(col("High"), 2).alias("High"),
        round(col("Low"), 2).alias("Low"),
        round(col("Close"), 2).alias("Close"),
        col("Volume")
    ).drop("Dividends", "Stock Splits")

    transformed_df.show(15)

except Exception as e:
    print(f"Error occured: {e}")

spark.stop()
