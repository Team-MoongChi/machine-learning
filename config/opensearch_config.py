from prefect.blocks.system import Secret

OPENSEARCH_HOST = Secret.load("opensearch-host",  _sync=True)
OPENSEARCH_PORT = Secret.load("opensearch-port",  _sync=True)
OPENSEARCH_USERNAME = Secret.load("opensearch-username",  _sync=True)
OPENSEARCH_PASSWORD = Secret.load("opensearch-password",  _sync=True)

OPENSEARCH_CONFIG = {
    "host": OPENSEARCH_HOST.get(),
    "port": OPENSEARCH_PORT.get(),
    "username": OPENSEARCH_USERNAME.get(),
    "password": OPENSEARCH_PASSWORD.get()
}