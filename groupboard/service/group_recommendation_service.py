import logging
from typing import Dict
from groupboard.processor.data_processor import DataProcessor
from groupboard.core.recommendation_engine import RecommendationEngine
from groupboard.transformer.response_transformer import ResponseTransformer
from config.group_board_config import ANALYSIS_DAYS, TOP_N_GROUPS
from datetime import datetime, timedelta
from utils.storage.s3_manager import S3Manager
from utils.storage.opensearch_manager import OpenSearchManager
import json

class GroupRecommendationService:
    """공구방 추천 서비스 메인 클래스"""
    
    def __init__(self, data_path: str, s3_bucket: str, opensearch_index: str):
        self.data_processor = DataProcessor(data_path)
        self.recommendation_engine = None
        self.response_formatter = ResponseTransformer()
        

        # 저장소 매니저 초기화
        self.s3_manager = S3Manager(s3_bucket)
        self.opensearch = OpenSearchManager(opensearch_index)
        
    def initialize(self) -> bool:
        """데이터 로드 및 서비스 초기화"""
        if not self.data_processor.load_data():
            logging.error("데이터 로드 실패")
            return False
        self.recommendation_engine = RecommendationEngine(self.data_processor)
        logging.info("공구방 추천 서비스 초기화 완료")
        return True
    
    def upload_all_recommendations(self, s3_key: str, top_n: int = 6) -> list:
        """
        모든 사용자 추천 결과 생성 및 S3/Opensearch에 저장.
        S3: {s3_key}/user_{user_id}/group_{timestamp}.json
        OpenSearch: doc_id = user_{user_id}_{timestamp}
        """
        if not self.recommendation_engine:
            print("서비스가 초기화되지 않았습니다.")
            return []

        all_recommendations = self.recommendation_engine.get_all_user_recommendations(top_n)
        formatted_recommendations = []
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        for rec in all_recommendations:
            if rec is None:
                continue
            user_id = rec.get("user_id")
            doc_id = f"user_{user_id}_{timestamp}"

            formatted_result = self.response_formatter.to_s3_doc(rec)
            formatted_op_result = self.response_formatter.to_opensearch_doc(doc_id, rec)
            
            # S3 저장
            user_s3_key = f"{s3_key}/user_{user_id}/group_{timestamp}.json"
            self.s3_manager.upload(user_s3_key, formatted_result)

            # OpenSearch 저장
            self.opensearch.upload(doc_id, formatted_op_result)

            formatted_recommendations.append(formatted_result)

        return formatted_result

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