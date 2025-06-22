import pandas as pd
from typing import Dict, List

from processor.category_pool import CategoryPoolBuilder
from processor.recommendation_data import RecommendationDataBuilder

class CategoryRecommender:
    """
    카테고리별 추천 후보 추출 담당 클래스
    - 카테고리별로 미리 구축된 상품 pool에서 추천 후보 추출
    """

    def __init__(self, products_df: pd.DataFrame):
        self.products_df = products_df

        # 카테고리별로 적합도 상위 상품 pool을 미리 생성
        self.category_pools = CategoryPoolBuilder.build(products_df)

    def recommend(self, category: str, count: int, previous_recs : set, used_product_ids: set, user_profile: Dict, is_preferred: bool) -> List:
        """
        특정 카테고리에서 추천 후보 상품을 추출

        Args:
            category: 추천할 카테고리명
            count: 추천할 상품 개수
            previous_recs: 이전에 추천된 상품 ID 집합 - 중복 방지
            used_product_ids: 이번 추천에서 이미 선택된 상품 ID 집합
            user_profile: 사용자 프로필
            is_preferred: 선호 카테고리 여부 - True면 부스팅 적용

        Returns:
            추천 후보 상품 딕셔너리 리스트
        """

        # 카테고리 pool이 없거나, 추천 개수가 0 이하이면 빈 리스트 반환
        if category not in self.category_pools or count <= 0:
            return []

        # pool에서 이미 추천된 상품, 이전에 추천된 상품 제외
        pool = self.category_pools[category].copy()
        pool = pool[~pool['id'].isin(used_product_ids | previous_recs)]

        # 1인가구 적합도 점수 기준으로 내림차순 정렬
        pool = pool.sort_values('flexible_single_score', ascending=False)