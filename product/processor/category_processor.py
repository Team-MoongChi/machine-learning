import pandas as pd
from typing import Optional

class CategoryProcessor:
    """카테고리 전처리 담당 클래스"""

    @staticmethod
    def make_category_text(categories_df: pd.DataFrame) -> pd.DataFrame:
        """
        대, 중, 소 카테고리를 결합해 읽기 쉬운 텍스트 필드 생성
        ex. 식품 > 음료 > 펩시콜라
        """
        df = categories_df.copy()
        df['category_path'] = (
            df['large_category'].astype(str) + ' > ' +
            df['medium_category'].fillna('').astype(str) + ' > ' +
            df['small_category'].fillna('').astype(str)
        )
        df['category_text'] = (
            df['large_category'].astype(str) + ' ' +
            df['medium_category'].fillna('').astype(str) + ' ' +
            df['small_category'].fillna('').astype(str)
        )
        return df