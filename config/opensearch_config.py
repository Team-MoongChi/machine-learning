import os
from dotenv import load_dotenv

load_dotenv()

OPENSEARCH_CONFIG = {
    "host": os.getenv("OPENSEARCH_HOST"),
    "port": os.getenv("OPENSEARCH_PORT", 9200),
    "username": os.getenv("OPENSEARCH_USERNAME", "admin"),
    "password": os.getenv("OPENSEARCH_PASSWORD")
}