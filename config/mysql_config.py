import os
from dotenv import load_dotenv

load_dotenv()

MYSQL_CONFIG = {
    "url": os.getenv("MYSQL_URL"),
    "database": os.getenv("MYSQL_DATABASE"),
    "port": int(os.getenv("MYSQL_PORT", 3306)),
    "username": os.getenv("MYSQL_USERNAME"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "charset": "utf8mb4",
    "timezone": "Asia/Seoul",
}