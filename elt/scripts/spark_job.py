import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, round, sha2, concat_ws
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, LongType, TimestampType
from datetime import datetime


ACC_NAME = os.getenv("ACC_NAME")
CONTAINER_NAME = os.getenv("CONTAINER_NAME")
SQL_SERVER = os.getenv("SQL_SERVER")
SQL_DB = os.getenv("SQL_DB")
SQL_USER = os.getenv("SQL_USER")
SQL_PASSWORD = os.getenv("SQL_PASSWORD")

current_date = datetime.now().strftime("%Y-%m-%d")

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

file_path = f"abfss://{CONTAINER_NAME}@{ACC_NAME}.dfs.core.windows.net/raw/company_data/{current_date}.csv"

try:
    df = spark.read.csv(file_path, header=True, schema=schema)
    df.printSchema()
    
    df = df.withColumn(
            "UniqueID",
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
        col("UniqueID"),
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

    # Load to SQL Server
    transformed_df.write \
        .format("jdbc") \
        .option("url", f"jdbc:sqlserver://{SQL_SERVER}:1433;database={SQL_DB}") \
        .option("dbtable", "StockData_Staging") \
        .option("user", SQL_USER) \
        .option("password", SQL_PASSWORD) \
        .option("driver", "com.microsoft.sqlserver.jdbc.SQLServerDriver") \
        .mode("overwrite") \
        .save()

    print("Data transformed and loaded into SQL Server successfully.")

except Exception as e:
    print(f"Error occured: {e}")

spark.stop()
