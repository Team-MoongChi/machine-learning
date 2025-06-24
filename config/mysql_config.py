from prefect.blocks.system import Secret

MYSQL_URL = Secret.load("mysql-url")
MYSQL_DATABASE = Secret.load("mysql-database")
MYSQL_PORT = Secret.load("mysql-port")
MYSQL_USERNAME = Secret.load("mysql-username")
MYSQL_PASSWORD = Secret.load("mysql-passowrd")

MYSQL_CONFIG = {
    "url": MYSQL_URL.get,
    "database": MYSQL_DATABASE,
    "port": MYSQL_PORT,
    "username": MYSQL_USERNAME,
    "password": MYSQL_PASSWORD,
    "charset": "utf8mb4",
    "timezone": "Asia/Seoul",
}