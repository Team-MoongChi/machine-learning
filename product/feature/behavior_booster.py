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