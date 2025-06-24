import asyncio
from prefect.blocks.system import Secret

from prefect.blocks.system import Secret

async def load_opensearch_config():
    host = await Secret.load("opensearch-host")
    port = await Secret.load("opensearch-port")
    username = await Secret.load("opensearch-username")
    password = await Secret.load("opensearch-password")

    return {
        "host": host.get(),
        "port": port.get(),
        "username": username.get(),
        "password": password.get()
    }

OPENSEARCH_CONFIG = asyncio.run(load_opensearch_config())