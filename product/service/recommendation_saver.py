from typing import List, Dict, Any
import pandas as pd
import datetime
import logging

from product.repository.recommendation_repository import RecommendationRepository

logger = logging.getLogger(__name__)

class RecommendationSaver:
    """
    추천 결과를 S3와 OpenSearch에 저장
    """

    def recommend_for_new_user(
            new_user_info: Dict,
            products_df: pd.DataFrame,
            faiss_manager,
            embedding_generator,
            repository,  # RecommendationRepository 인스턴스
            top_k: int = 4
        ) -> List[Dict[str, Any]]:
        """
        신규 사용자 추천: 실시간 임베딩 생성 + FAISS 유사도 기반 Top-K 추천 + 저장
        """
        
