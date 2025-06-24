from prefect.blocks.system import Secret

OPENSEARCH_HOST = Secret.load("opensearch-host")
OPENSEARCH_PORT = Secret.load("opensearch-port")
OPENSEARCH_USERNAME = Secret.load("opensearch-username")
OPENSEARCH_PASSWORD = Secret.load("opensearch-password")

OPENSEARCH_CONFIG = {
    "host": OPENSEARCH_HOST,
    "port": OPENSEARCH_PORT,
    "username": OPENSEARCH_USERNAME,
    "password": OPENSEARCH_PASSWORD
}