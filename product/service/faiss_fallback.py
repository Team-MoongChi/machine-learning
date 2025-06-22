import pandas as pd
from typing import Dict, List, Set

from processor.recommendation_data import RecommendationDataBuilder

class FaissFallbackRecommender:
    """
    FAISS 벡터 기반 유사도 추천 담당 클래스
    - pool/카테고리 기반 추천만으로 충분하지 않을 때, 
    사용자 임베딩과 상품 벡터 간 유사도(최근접 이웃)를 기반으로 추가 추천 후보를 보충하는 역할
    """
    def __init__(self, products_df, faiss_manager, embedding_generator):
        self.products_df = products_df
        self.faiss_manager = faiss_manager
        self.embedding_generator = embedding_generator
    
    def recommend(self, user_profile: Dict, count: int, used_product_ids: Set) -> List:
        """
        FAISS를 이용해 유사도 기반 추천 후보를 반환

        Args:
            user_profile: 추천 대상 사용자의 프로필
            count: 추천할 상품 개수
            used_product_ids: 이미 추천된 상품 ID 집합

        Returns:
            list: 추천 후보 상품의 딕셔너리 리스트
        """

        # 추천 개수가 0 이하이면 빈 리스트 반환
        if count <= 0:
            return []