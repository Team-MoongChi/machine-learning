import pandas as pd
from typing import Dict, List, Any
from datetime import datetime

from product.processor.data_processor import DataProcessor

class UserProfiler:
    """
    사용자 행동 로그(검색, 로그, 찜)을 바탕으로
    유저별 관심사, 나이대, 활동량, 선호 카테고리 등 
    다양한 정보를 추출하여 프로필 딕셔너리로 만드는 클래스
    """

    def __init__(self, data_processor: DataProcessor):
        self.products = data_processor.products
        self.search_logs = data_processor.search_logs
        self.click_logs = data_processor.click_logs
        self.favorite_products = data_processor.favorite_products

    def calculate_age(self, birth_str: str) -> int:
        """
        현재 년도를 가져와서 생년월일에서 나이를 계산 
        """
        try:
            birth_year = int(str(birth_str)[:4])
            current_year = datetime.now().year  # 현재 연도 자동 추출
            return current_year - birth_year
        except Exception:
            return Exception("생년월일이 제대로 계산되지 않았습니다.")
    
    def get_age_group(self, age: int) -> str:
        """
        나이를 연령대로 변환
        """
        if age < 30:
            return '20대'
        elif age < 40:
            return '30대'
        else:
            return '40대+'
    
    def get_user_type(self, total_actions: int) -> str:
        """
        행동량(검색 + 클릭 + 찜)에 따라 사용자 분류
        """
        if total_actions <= 5:
            return 'new'
        elif total_actions <= 20:
            return 'active'
        else:
            return 'power'