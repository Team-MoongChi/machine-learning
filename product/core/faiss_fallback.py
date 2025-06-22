import pandas as pd
from typing import Dict, List, Set

from product.processor.recommendation_data import RecommendationDataBuilder

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

        try:
            # 사용자 프로필로부터 쿼리 임베딩(벡터) 생성
            query_embedding, _ = self.embedding_generator.generate_user_embedding(user_profile)

            # FAISS 인덱스에서 쿼리 임베딩과 유사한 상품 인덱스 top-100 검색
            _, indices = self.faiss_manager.search(query_embedding, k=100)

            fallback_recs = []
            # 유사도 순으로 상품을 순회, 이미 추천된 상품은 제외하고 추천 후보로 추가
            for idx in indices:

                if len(fallback_recs) >= count:
                    break
                product = self.products_df.iloc[idx]

                if product['id'] not in used_product_ids:
                    # 추천 데이터 구조화 - 부스팅 포함 
                    rec_data = RecommendationDataBuilder.build(product, user_profile, False, self.products_df)
                    fallback_recs.append(rec_data)
                    used_product_ids.add(product['id'])
            return fallback_recs

        except Exception:
            return []