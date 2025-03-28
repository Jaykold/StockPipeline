import os
import sys
from pyspark.sql import SparkSession
from pyspark.conf import SparkConf

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import ACC_NAME, SP_APP_ID, SP_SECRET_ID, SP_TENANT_ID, CONTAINER_NAME

conf = SparkConf() \
    .setAppName('adls-job') \
    .setMaster("local[*]") \
    .set("spark.jars", "/opt/spark/jars/hadoop-azure-3.3.4.jar,/opt/spark/jars/mssql-jdbc-12.10.0.jrell.jar") \
    .set("fs.azure.account.auth.type.{}.dfs.core.windows.net".format(ACC_NAME), "OAuth") \
    .set("fs.azure.account.oauth.provider.type.{}.dfs.core.windows.net".format(ACC_NAME), "org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider") \
    .set("fs.azure.account.oauth2.client.id.{}.dfs.core.windows.net".format(ACC_NAME), SP_APP_ID) \
    .set("fs.azure.account.oauth2.client.secret.{}.dfs.core.windows.net".format(ACC_NAME), SP_SECRET_ID) \
    .set("fs.azure.account.oauth2.client.endpoint.{}.dfs.core.windows.net".format(ACC_NAME), "https://login.microsoftonline.com/{}/oauth2/token".format(SP_TENANT_ID)) \
    .set("spark.hadoop.fs.azurebfs.logging.enabled", "true") \
    .set("spark.hadoop.fs.azurebfs.logging.level", "ERROR")

spark = SparkSession.builder.config(conf=conf).getOrCreate()

file_path = f"abfss://{CONTAINER_NAME}@{ACC_NAME}.dfs.core.windows.net/raw/company_data/*.csv"

try:
    df = spark.read.csv(file_path)
    df.printSchema()
    df.show(15)

except Exception as e:
    print(f"Error occured: {e}")

spark.stop()
