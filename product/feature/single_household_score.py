import pandas as pd

class SingleHouseHoldScoreCalculator:
    """
    상품의 1인가구 적합도 점수를 계산하는 클래스
    - Processor에 있는 1인 가구 적합도 계산 함수는 간단한 feature를 산출하는 용도로 사용
    - 현재 클래스는 더 정교하게 적합도를 계산하여 반영
    - 이후 추천 시스템 고도화 시, Processor로 적합도가 일정 기준 이상인 항목만 1차적으로 추출할 수 있음 
    """
    # 1인가구에 매우 적합한 핵심 키워드 목록 
    LEGENDARY_KEYWORDS = ['1인용', '혼밥', '미니', '소포장', '개별포장', '1인분']

    # 1인가구에 적합한 보조 키워드 목록 
    GOOD_KEYWORDS = ['간편', '소량', '작은', '컴팩트', '휴대용', '간단', '즉석', '소형']

    @classmethod
    def calculate(cls, product: pd.Series) -> float:
        """
        Args:
            product (pd.Series): 상품 정보

        Returns:
            float: 계산된 1인가구 적합도 점수 (0~25점)
        """
        score = 0.0

        # 상품명을 소문자로 변환하여 키워드 검색의 일관성 확보
        name_lower = str(product['name']).lower()

        # 핵심 키워드 포함 시 15점씩 가산
        for keyword in cls.LEGENDARY_KEYWORDS:
            if keyword in name_lower:
                score += 15.0

        # 보조 키워드 포함 시 8점씩 가산
        for keyword in cls.GOOD_KEYWORDS:
            if keyword in name_lower:
                score += 8.0
