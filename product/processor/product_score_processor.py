import pandas as pd

class ProductSingleScoreProcessor:
    """상품/카테고리 조인 및 1인 가구 적합도 점수 계산 """

    PRIMARY_KEYWORDS = ['1인용', '혼밥', '소포장', '미니', '원룸', '소량']
    SECONDARY_KEYWORDS = ['간편', '간단', '즉석', '개별', '포션', '1개입']

    @staticmethod
    def join(products_df: pd.DataFrame, categories_df: pd.DataFrame) -> pd.DataFrame:
        """상품/카테고리 조인"""
        
        # 컬럼명 같음 
        merged = products_df.merge(
            categories_df,
            on='category_id',
            how='left'
        )

        # None 카테고리는 '기타'로 채움 
        merged['large_category'] = merged['large_category'].fillna('기타')
        merged['medium_category'] = merged['medium_category'].fillna('기타')
        merged['small_category'] = merged['small_category'].fillna('기타')
        return merged