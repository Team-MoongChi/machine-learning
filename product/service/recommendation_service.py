from utils.storage.s3_manager import S3Manager
from utils.storage.opensearch_manager import OpenSearchManager
from product.transformer.recommendation_transformer import RecommendationTransformer
from config.opensearch_config import OPENSEARCH_CONFIG

class RecommendationService:
    def __init__(self, s3_bucket: str, opensearch_index: str):
        self.s3 = S3Manager(s3_bucket)
        self.opensearch = OpenSearchManager(opensearch_index)
        self.transformer = RecommendationTransformer()
    
    def save_recommendation(self, s3_key: str, doc_id: str, recommendation_data: dict) -> None:
        """추천 결과를 S3와 OpenSearch에 저장"""
        self.s3.upload(s3_key, recommendation_data)
        core_data = self.transformer.to_core_data(recommendation_data)
        self.opensearch.upload(doc_id, core_data)
    
    def get_recommendation(self, doc_id: str) -> dict:
        """OpenSearch에서 추천 결과를 조회하고 백엔드 형식으로 변환"""
        core_data = self.opensearch.get(doc_id)
        if core_data:
            return self.transformer.to_backend_format(core_data)
        return None