import os
from dotenv import load_dotenv

load_dotenv()

EDGE_DRIVER_PATH = os.getenv("EDGE_DRIVER_PATH")
CONTAINER_NAME = os.getenv("CONTAINER_NAME")
ACC_NAME = os.getenv("ACC_NAME")
ACC_KEY = os.getenv("ACC_KEY")
SP_APP_ID = os.getenv("SP_APP_ID")
SP_TENANT_ID = os.getenv("SP_TENANT_ID")
SP_SECRET_ID = os.getenv("SP_SECRET_ID")