import pandas as pd
import random
from typing import Dict, List

from processor.recommendation_history import RecommendationHistoryManager
from product.core.category_recommender import CategoryRecommender
from product.core.faiss_fallback import FaissFallbackRecommender
from product.core.emergency_recommender import EmergencyRecommender

class RecommendationEngine:
    """
    1인가구 특화 추천 시스템 엔진
    """
    def __init__(self, products_df, faiss_manager, embedding_generator, user_profiles: Dict):
        self.products_df = products_df
        self.user_profiles = user_profiles

        self.history_manager = RecommendationHistoryManager()
        self.category_recommender = CategoryRecommender(products_df)
        self.faiss_fallback = FaissFallbackRecommender(products_df, faiss_manager, embedding_generator)
        self.emergency_recommender = EmergencyRecommender(products_df)
    
    def recommend(self, user_id: int, top_k: int = 4) -> pd.DataFrame:
        """
        사용자별 맞춤 추천 생성

        Args:
            user_id: 추천 대상 사용자 ID
            top_k: 추천할 상품 개수 - 기본 4개

        Returns:
            pd.DataFrame: 추천 결과
        """
        # 사용자 프로필이 없으면 빈 결과 반환
        if user_id not in self.user_profiles:
            return pd.DataFrame()

