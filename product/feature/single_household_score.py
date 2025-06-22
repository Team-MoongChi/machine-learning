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

        # 가격대별 추가 점수
        price = product.get('price', 0)
        if price <= 5000:
            score += 10.0  # 5천원 이하: 가성비 최우수
        elif price <= 15000:
            score += 7.0   # 1.5만원 이하: 적정 가격
        elif price <= 30000:
            score += 4.0   # 3만원 이하: 수용 가능

        # 카테고리별 특화 키워드 보너스
        category = product.get('large_category', '')

        # 가공식품이면서 즉석/간편/밀키트가 상품명에 포함되면 5점 추가
        if '가공식품' in category and any(w in name_lower for w in ['즉석', '간편', '밀키트']):
            score += 5.0

        # 주방용품이면서 실리콘/미니/소형이 상품명에 포함되면 5점 추가
        elif '주방용품' in category and any(w in name_lower for w in ['실리콘', '미니', '소형']):
            score += 5.0

        # 최대 점수 25점으로 제한
        return min(score, 25.0)