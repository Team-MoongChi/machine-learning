import pandas as pd
from typing import Dict, List, Any
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
    