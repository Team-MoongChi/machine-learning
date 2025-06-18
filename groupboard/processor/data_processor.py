import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import re
from typing import Optional, Tuple

class DataProcessor:
    """데이터 로드 및 전처리 담당 클래스"""
    
    def __init__(self, data_path: str):
        self.data_path = data_path
        
    def load_data(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """데이터 파일들을 로드하여 반환"""
        try:
            favorites_path = f"{self.data_path}/favorite_products_dummy_3000.csv"
            users_path = f"{self.data_path}/users_dummy_200.csv"
            groups_path = f"{self.data_path}/group_boards_dummy_366.csv"
            
            favorite_products = pd.read_csv(favorites_path)
            users = pd.read_csv(users_path)
            group_boards = pd.read_csv(groups_path)
            
            return favorite_products, users, group_boards
            
        except Exception as e:
            raise Exception(f"데이터 로드 실패: {e}")