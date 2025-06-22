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

    # 클래스 변수에 접근 
    @classmethod
    def calc_score(cls, products_df: pd.DataFrame) -> pd.DataFrame:
        """
        상품명과 가격을 바탕으로 1인 가구 적합도 점수(0~10점) 계산
        Args:
            row (pd.Series): 상품 데이터의 한 행

        Returns:
            float: 계산된 적합도 점수(0~10)
        """
        def score(row):
            name = str(row.get('name', '')).lower()
            price = float(row.get('price', 0))
            s = 0

            # 주요 키워드가 상품명에 포함되어 있으면 3점씩 추가 
            for kw in cls.PRIMARY_KEYWORDS:
                if kw in name:
                    s += 3
            
            # 보조 키워드가 상품명에 포함되어 있으면 1.5점씩 추가 
            for kw in cls.SECONDARY_KEYWORDS:
                if kw in name:
                    s += 1.5

            # 가격 기반 추가 점수         
            if price < 10000:
                s += 1
            elif price < 30000:
                s += 0.5
            
            # 최대 10점으로 제한 
            return min(s, 10)

        df = products_df.copy()
        df['single_household_score'] = df.apply(score, axis=1)
        return df