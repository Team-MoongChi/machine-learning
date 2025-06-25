from prefect.blocks.system import Secret

MYSQL_URL = Secret.load("mysql-url",  _sync=True)
MYSQL_DATABASE = Secret.load("mysql-database",  _sync=True)
MYSQL_PORT = Secret.load("mysql-port",  _sync=True)
MYSQL_USERNAME = Secret.load("mysql-username",  _sync=True)
MYSQL_PASSWORD = Secret.load("mysql-password",  _sync=True)

MYSQL_CONFIG = {
    "url": MYSQL_URL.get(),
    "database": MYSQL_DATABASE.get(),
    "port": MYSQL_PORT.get(),
    "username": MYSQL_USERNAME.get(),
    "password": MYSQL_PASSWORD.get(),
    "charset": "utf8mb4",
    "timezone": "Asia/Seoul",
}