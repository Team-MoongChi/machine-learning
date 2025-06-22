import pandas as pd
from typing import Dict

from product.feature.behavior_booster import BehaviorBooster


class RecommendationDataBuilder:
    """
    추천 결과 데이터(딕셔너리)를 생성하는 클래스.
    추천 엔진의 각 단계에서 산출된 다양한 점수와 정보를 하나의 추천 결과 데이터로 구조화합니다.
    """

    @staticmethod
    def build(product: pd.Series, user_profile: Dict, is_preferred: bool, products_df: pd.DataFrame) -> Dict:
        """
        추천 결과 데이터(딕셔너리) 생성.

        Args:
            product: 추천할 상품의 정보 (이름, 가격, 카테고리, 점수 등)
            user_profile: 사용자 행동 이력 등 개인화 정보
            is_preferred: 선호 카테고리 상품 여부
            products_df: 전체 상품 데이터

        Returns:
            추천 결과로 사용할 구조화된 데이터
        """

        # 1. 1인가구 적합도 점수(0~25)를 10점 만점으로 정규화
        flexible_score = product.get('flexible_single_score', 5.0)
        normalized_score = min((flexible_score / 25.0) * 10.0, 10.0)

        # 2. 기본 유사도 및 부스팅 배수 초기화
        base_similarity = 0.75
        boost_multiplier = 2.0

        # 3. 선호 카테고리 상품이면 추가 부스팅
        if is_preferred:
            boost_multiplier *= 3.0

        # 4. 1인가구 적합도 점수에 따라 추가 부스팅
        if flexible_score >= 20.0:
            boost_multiplier *= 4.0
        elif flexible_score >= 15.0:
            boost_multiplier *= 3.0
        elif flexible_score >= 10.0:
            boost_multiplier *= 2.0

        # 5. 사용자 행동(찜, 검색, 클릭 등) 기반 부스팅 적용
        behavior_boost = BehaviorBooster.apply(product, user_profile, products_df)
        boost_multiplier *= behavior_boost

        # 6. 최종 추천 점수 산출
        final_score = base_similarity * boost_multiplier

        # 7. 추천 결과를 하나의 딕셔너리로 구조화하여 반환
        return {
            'product_id': product['product_id'],                         # 상품 고유 ID
            'name': product['name'],                             # 상품명
            'price': product.get('price', 0),                    # 가격
            'category_path': product.get('category_path', ''),   # 카테고리 경로
            'large_category': product.get('large_category', '기타'), # 대분류
            'single_household_score': normalized_score,          # 1인가구 적합도(정규화)
            'base_similarity': base_similarity,                  # 기본 유사도 점수
            'final_score': final_score,                          # 최종 추천 점수
            'boost_ratio': boost_multiplier,                     # 전체 부스팅 배수
            'behavior_boost': behavior_boost,                    # 행동 기반 부스팅 배수
            'user_type': 'single_household_optimized',           # 추천 사용자 유형
            'recommendation_reason': '선호/다양성/유사도/행동 반영', # 추천 사유 요약
            'premium_score': flexible_score,                     # 정규화 전 1인가구 점수
            'appeal_score': 10.0                                 # 어필 점수(고정)
        }