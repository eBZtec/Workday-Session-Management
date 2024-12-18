import os
import logging
from dotenv import load_dotenv


load_dotenv()

AUDIT_DB_URL = os.getenv("AUDIT_DB_URL")
QUEUE_NAME = os.getenv("QUEUE_NAME")
QUEUE_HOST = os.getenv("QUEUE_HOST")