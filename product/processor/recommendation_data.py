import pandas as pd
from typing import Dict


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