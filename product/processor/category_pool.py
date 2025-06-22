import pandas as pd

class CategoryPoolBuilder:
    """
    카테고리별 1인가구 특화 상품 pool을 미리 구축하는 클래스
    - 각 카테고리별로 1인가구 적합도 점수가 높은 상품만 선별하여 pool 생성
    - 추천 엔진이 빠르게 카테고리별 후보군을 선택할 수 있도록 미리 pool 생성
    """
    @staticmethod
    def build(products_df: pd.DataFrame) -> pd.DataFrame:
        """
        Args:
            전체 상품 데이터프레임

        Returns:
            {카테고리명: pool DataFrame} 구조의 카테고리별 상품 pool 딕셔너리
        """
        category_pools = {}
        target_categories = ['신선식품', '가공식품', '주방용품', '생활용품']
        
