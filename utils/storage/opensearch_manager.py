from opensearchpy import OpenSearch
from config.recommendation_config import OPENSEARCH_CONFIG
import logging

class OpenSearchManager:
    def __init__(self, index: str):
        self.client = OpenSearch(
            hosts=[{'host': OPENSEARCH_CONFIG["host"], 'port': OPENSEARCH_CONFIG["port"]}],
            http_auth=(OPENSEARCH_CONFIG["username"], OPENSEARCH_CONFIG["password"]),
            use_ssl=True,
            verify_certs=False,  # 인증서 검증 무시
            ssl_show_warn=False,
            timeout=30,
            max_retries=3,
            retry_on_timeout=True
            )
        self.index = index
    
    def upload(self, doc_id: str, data: dict) -> None:
        response = self.client.index(
            index=self.index,
            id=doc_id,
            body=data
        )
        logging.info(f"Uploaded recommendation data to OpenSearch index {self.index} with ID {doc_id}: {response}")

    def get(self, doc_id: str) -> dict:
        try:
            response = self.client.get(index=self.index, id=doc_id)
            return response['_source']
        except Exception as e:
            logging.error(f"Error retrieving from OpenSearch: {e}")
            return None
    
    def search(self, body: dict, size: int = 10) -> dict:
        """
        OpenSearch에서 쿼리로 여러 문서를 검색

        Args:
            body (dict): OpenSearch 쿼리 DSL (예: {"query": {...}})
            size (int): 반환할 최대 문서 수

        Returns:
            dict: 검색 결과 전체(JSON)
        """
        try:
            response = self.client.search(
                index=self.index,
                body=body,
                size=size
            )
            logging.info(f"OpenSearch search executed on index {self.index} with body {body}")
            return response
        except Exception as e:
            logging.error(f"OpenSearch search error: {e}")
            return {}