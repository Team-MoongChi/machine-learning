from utils.storage.s3_manager import S3Manager
from utils.storage.opensearch_manager import OpenSearchManager
from recommendation.transformer.recommendation_transformer import RecommendationTransformer
from config.recommendation_config import OPENSEARCH_CONFIG
from typing import Dict, Any, Optional
import logging
logger = logging.getLogger(__name__)

class RecommendationRepository:
    def __init__(self, s3_bucket: str, opensearch_index: str):
        self.s3 = S3Manager(s3_bucket)
        self.opensearch = OpenSearchManager(opensearch_index)
        self.transformer = RecommendationTransformer()

    def save_to_opensearch(self, doc_id: str, recommendation_data: Dict[str, Any]) -> bool:
        """OpenSearch에 추천 데이터 저장"""
        try:
            # 데이터 변환
            core_data = self.transformer.to_core_data(doc_id, recommendation_data)
            
            # OpenSearch에 저장
            self.opensearch.upload(doc_id=doc_id, data=core_data)
            logger.info(f"Successfully saved recommendation to OpenSearch: {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save recommendation to OpenSearch: {str(e)}")
            return False

    def save_to_s3(self, user_id: str, recommendation_data: Dict[str, Any]) -> bool:
        """S3에 추천 데이터 저장"""
        try:
            # S3 키 생성
            s3_key = f"recommendations/user_{user_id}.json"
            
            # S3에 저장 (원본 데이터 저장)
            self.s3.upload(key=s3_key, data=recommendation_data)
            logger.info(f"Successfully saved recommendation to S3: {s3_key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save recommendation to S3: {str(e)}")
            return False

    def get_from_opensearch(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """OpenSearch에서 추천 데이터 조회"""
        try:
            # OpenSearch에서 조회
            core_data = self.opensearch.get(doc_id=doc_id)
            
            if not core_data:
                logger.warning(f"No recommendation found in OpenSearch: {doc_id}")
                return None
            
            print(f"Retrieved recommendation from OpenSearch: {doc_id}")
            # 백엔드 포맷으로 변환
            return self.transformer.to_backend_format(core_data)
            
        except Exception as e:
            logger.error(f"Error retrieving recommendation from OpenSearch: {str(e)}")
            return None