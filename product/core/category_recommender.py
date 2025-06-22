import pandas as pd
from typing import Dict, List

from product.processor.category_pool import CategoryPoolBuilder
from product.processor.recommendation_data import RecommendationDataBuilder

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

        selected = []           # 최종 추천 후보 리스트
        price_ranges_used = set()  # 가격대 다양성 확보용

        # pool에서 count만큼 상품을 선택
        for _, product in pool.iterrows():
            if len(selected) >= count:
                break

            price = product.get('price', 0)

            # 가격대별로 구간을 나눠 다양성 확보
            price_range = 'low' if price < 8000 else 'mid' if price < 20000 else 'high'

            # 선호 카테고리가 아닌 경우, 이미 선택한 가격대는 중복 피하기
            if not is_preferred and price_range in price_ranges_used and len(selected) > 0:
                continue

            # 추천 데이터 구조화 - 부스팅 포함
            rec_data = RecommendationDataBuilder.build(product, user_profile, is_preferred, self.products_df)
            selected.append(rec_data)
            price_ranges_used.add(price_range)

        # 만약 count만큼 못 뽑았으면, 가격대 중복 허용하고 추가로 선택
        if len(selected) < count:
            remaining_pool = pool[~pool['id'].isin([rec['product_id'] for rec in selected])]
            
            for _, product in remaining_pool.head(count - len(selected)).iterrows():
                rec_data = RecommendationDataBuilder.build(product, user_profile, is_preferred, self.products_df)
                selected.append(rec_data)

        return selected