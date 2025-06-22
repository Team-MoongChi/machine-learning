import pandas as pd
import random
from typing import Dict, List

from product.processor.recommendation_history import RecommendationHistoryManager
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
        
        user_profile = self.user_profiles[user_id]

        previous_recs = self.history_manager.get(user_id)  # 이전 추천 상품 ID 집합
        used_product_ids = set()                        
        preferred_category = user_profile.get('base_interest_category', '가공식품')
        recommendations = []

        # 선호 카테고리에서 2개 추천
        recommendations += self.category_recommender.recommend(
            preferred_category, 2, previous_recs, used_product_ids, user_profile, True
        )
        used_product_ids.update([rec['product_id'] for rec in recommendations])

        # 나머지 카테고리에서 1개씩 추천
        other_categories = [c for c in ['신선식품', '가공식품', '주방용품', '생활용품'] if c != preferred_category]
        random.seed(user_id)  # 사용자별 고정 시드
        random.shuffle(other_categories)
        for category in other_categories:
            if len(recommendations) >= top_k:
                break
            recs = self.category_recommender.recommend(
                category, 1, previous_recs, used_product_ids, user_profile, False
            )
            recommendations += recs
            used_product_ids.update([rec['product_id'] for rec in recs])

        # 부족하면 FAISS fallback(유사도 기반 추천)으로 보충
        if len(recommendations) < top_k:
            fallback = self.faiss_fallback.recommend(
                user_profile, top_k - len(recommendations), used_product_ids
            )
            recommendations += fallback
            used_product_ids.update([rec['product_id'] for rec in fallback])

        # 그래도 부족하면 emergency 추천으로 보충
        if len(recommendations) < top_k:
            emergency = self.emergency_recommender.recommend(
                top_k - len(recommendations), used_product_ids, user_id
            )
            recommendations += emergency

        # 최종 추천 결과 DataFrame 변환 및 중복 제거
        final_df = pd.DataFrame(recommendations[:top_k]).drop_duplicates(subset=['product_id']).head(top_k)
        self.history_manager.update(user_id, final_df)  # 추천 히스토리 업데이트
        return final_df

