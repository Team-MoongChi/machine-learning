import asyncio
from prefect.blocks.system import Secret

async def load_mysql_config():
    url = await Secret.load("mysql-url")
    database = await Secret.load("mysql-database")
    port = await Secret.load("mysql-port")
    username = await Secret.load("mysql-username")
    password = await Secret.load("mysql-password")  # 오타 주의

    return {
        "url": url.get(),
        "database": database.get(),
        "port": port.get(),
        "username": username.get(),
        "password": password.get(),
        "charset": "utf8mb4",
        "timezone": "Asia/Seoul",
    }

MYSQL_CONFIG = asyncio.run(load_mysql_config())