from utils.storage.s3_manager import S3Manager
from utils.storage.opensearch_manager import OpenSearchManager
from product.transformer.recommendation_transformer import RecommendationTransformer
from config.opensearch_config import OPENSEARCH_CONFIG
from typing import Dict, Any, Optional
import logging
from datetime import datetime, timedelta
logger = logging.getLogger(__name__)

class RecommendationRepository:
    def __init__(self, s3_bucket: str, opensearch_index: str, mapping: dict):
        self.s3 = S3Manager(s3_bucket)
        self.opensearch = OpenSearchManager(opensearch_index, mapping)
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

    def save_to_s3(self, s3_key: str, recommendation_data: Dict[str, Any]) -> bool:
        """S3에 추천 데이터 저장"""
        try:
            # S3에 저장 (원본 데이터 저장)
            self.s3.upload(key=s3_key, data=recommendation_data)
            logger.info(f"Successfully saved recommendation to S3: {s3_key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save recommendation to S3: {str(e)}")
            return False

    
    def get_recommendation_from_opensearch(self, user_id: str) -> Dict:
            """최근 14일 이내에 생성된 추천 결과 중 가장 최근 문서를 OpenSearch에서 조회"""
            try:
                query = {
                    "query": {
                        "prefix": {
                            "doc_id": f"user_{user_id}_"
                        }
                    },
                    "sort": [{"doc_id": "desc"}],
                    "size": 1
                }

                result = self.opensearch.search(query)
                print(result)
                hits = result.get("hits", {}).get("hits", [])

                if hits:
                    source = hits[0]["_source"]
                    doc_id = source.get("doc_id", "")
                    parts = doc_id.split("_")

                    if len(parts) >= 4:
                        date_str = parts[2]
                        try:
                            doc_date = datetime.strptime(date_str, "%Y%m%d")
                            if doc_date >= datetime.now() - timedelta(days=14):
                                return {
                                    "status": "success",
                                    "data": source,
                                    "timestamp": "_".join(parts[2:])  # '20250619_170604'
                                }
                        except ValueError:
                            logging.warning(f"Invalid timestamp format in doc_id: {doc_id}")

                return {
                    "status": "error",
                    "message": f"사용자 {user_id}의 최근 14일 추천 결과가 없습니다.",
                    "data": None
                }

            except Exception as e:
                logging.error(f"OpenSearch search error: {str(e)}")
                return {
                    "status": "error",
                    "message": f"추천 결과 조회 실패: {str(e)}",
                    "data": None
                }