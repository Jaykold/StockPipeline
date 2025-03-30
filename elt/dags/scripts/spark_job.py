import os
import sys
from pyspark.sql import SparkSession
from pyspark.conf import SparkConf
from pyspark.sql.functions import col, round, sha2, concat_ws
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, LongType, TimestampType

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import ACC_NAME, SP_APP_ID, SP_SECRET_ID, SP_TENANT_ID, CONTAINER_NAME, ACC_KEY

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

conf = SparkConf() \
    .setAppName('StockDataTransformation') \
    .setMaster("local[*]") \
    .set("spark.hadoop.fs.azure.account.key.{}.dfs.core.windows.net".format(ACC_NAME), ACC_KEY) \
    .set("spark.hadoop.fs.azurebfs.logging.enabled", "true") \
    .set("spark.hadoop.fs.azurebfs.logging.level", "ERROR")

spark = SparkSession.builder.config(conf=conf).getOrCreate()

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
