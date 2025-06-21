from opensearchpy import OpenSearch
from config.opensearch_config import OPENSEARCH_CONFIG
from config.opensearch_mappings import GROUP_RECOMMENDATION_MAPPING
import logging
import json

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
        self.mapping = GROUP_RECOMMENDATION_MAPPING
    
    def create_index(self) -> bool:
        """인덱스가 없을 경우에만 생성"""
        try:
            print(f"Creating index {self.index} if it does not exist...")
            # 인덱스 존재 여부 확인
            if self.client.indices.exists(index=self.index):
                logging.info(f"Index {self.index} already exists")
                return True
                
            response = self.client.indices.create(index=self.index, body=self.mapping)
            logging.info(f"Created new index {self.index}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to create index {self.index}: {str(e)}")
            return False
    
    # 인덱스 타입 자동 추론돼서 에러 발생 
    def upload(self, doc_id: str, data: dict) -> None:
        self.create_index()  # 인덱스가 없으면 생성
        data = json.dumps(data, ensure_ascii=False, indent=2)
        response = self.client.index(
            index=self.index,
            id=doc_id,
            body=data,
            headers={"Content-Type": "application/json"}
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
    
    def delete_all(self) -> int:
        """인덱스의 모든 문서 삭제"""
        query = {
            "query": {
                "match_all": {}
            }
        }
        
        response = self.client.delete_by_query(
            index=self.index,
            body=query
        )
        
        return response['deleted']

    def delete_index(self) -> bool:
        """인덱스 전체 삭제"""
        try:
            response = self.client.indices.delete(index=self.index)
            return True
        except Exception as e:
            return False