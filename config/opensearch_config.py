from prefect.blocks.system import Secret

OPENSEARCH_HOST = Secret.load("opensearch-host")
OPENSEARCH_PORT = Secret.load("opensearch-port")
OPENSEARCH_USERNAME = Secret.load("opensearch-username")
OPENSEARCH_PASSWORD = Secret.load("opensearch-password")

OPENSEARCH_CONFIG = {
    "host": OPENSEARCH_HOST.get(),
    "port": OPENSEARCH_PORT.get(),
    "username": OPENSEARCH_USERNAME.get(),
    "password": OPENSEARCH_PASSWORD.get()
}