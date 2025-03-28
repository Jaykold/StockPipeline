import os
from dotenv import load_dotenv

load_dotenv()

EDGE_DRIVER_PATH = os.getenv("EDGE_DRIVER_PATH")
CONTAINER_NAME = os.getenv("ADLS_CONTAINER")
ACC_NAME = os.getenv("ADLS_ACCNAME")
ACC_KEY = os.getenv("ADLS_ACCKEY")
SP_APP_ID = os.getenv("SP_APP_ID")
SP_TENANT_ID = os.getenv("SP_TENANT_ID")
SP_SECRET_ID = os.getenv("SP_SECRET_ID")