import pandas as pd
from typing import Dict, List, Any

class BehaviorBooster:
    """
    사용자 행동(찜, 검색, 클릭) 기반 부스팅 배수를 계산하는 클래스
    추천 점수에 곱해질 부스팅 배수 산출
    """
    
    @staticmethod
    def apply(product: pd.Series, user_profile: Dict, products_df: pd.DataFrame) -> float:
        """
        상품과 사용자의 행동 이력을 비교하여 해당 상품이 그 사용자에게
        더 매력적으로 보일 이유가 있다면 부스팅 배수를 곱해서 반환

        Args:
            product (pd.Series): 평가할 상품 정보
            user_profile (dict): 사용자 프로필(찜, 검색, 클릭 이력 등)
            products_df (pd.DataFrame): 전체 상품 데이터

        Returns:
            float: 최종 부스팅 배수 (최대 3.5)
        """

        behavior_boost = 1.0  # 기본 배수
        product_name_lower = str(product['name']).lower()
        product_category = product.get('large_category', '')

        # 찜 이력 부스팅
        # 사용자가 최근 찜한 상품(최대 3개) 중 현재 상품과 같은 카테고리가 있으면 1.5배 곱함
        favorite_products = user_profile.get('favorite_product_ids', [])
        for fav_id in favorite_products[:3]:
            fav_product = products_df[products_df['id'] == fav_id]
            if not fav_product.empty and fav_product.iloc[0].get('large_category', '') == product_category:
                behavior_boost *= 1.5
                break  # 한 번만 부스팅