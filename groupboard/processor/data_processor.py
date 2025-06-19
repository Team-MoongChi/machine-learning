import pandas as pd
from datetime import datetime, timedelta
from typing import Tuple
from config.group_board_config import ANALYSIS_DAYS

class DataProcessor:
    """데이터 로드 및 전처리 담당 클래스"""
    
    def __init__(self, data_path: str):
        self.data_path = data_path
        self.users = None
        self.group_boards = None
        self.recent_activities = None
        
    def load_data(self) -> bool:
        """데이터 파일들을 로드하여 반환"""
        try:
            favorites_path = f"{self.data_path}/favorite_products_dummy_3000.csv"
            users_path = f"{self.data_path}/users_dummy_200.csv"
            groups_path = f"{self.data_path}/group_boards_dummy_366.csv"
            
            favorite_products = pd.read_csv(favorites_path)
            self.users = pd.read_csv(users_path)
            self.group_boards = pd.read_csv(groups_path)
            self.recent_activities = self.filter_recent_group_favorites(favorite_products)
            
            return True
            
        except Exception as e:
            raise Exception(f"데이터 로드 실패: {e}")
    
    def filter_recent_group_favorites(self, favorite_products: pd.DataFrame, 
                                    days: int = ANALYSIS_DAYS) -> pd.DataFrame:
        """최근 N일간 공구방 찜하기 데이터 필터링"""
        
        # 공구방 찜하기만 필터링
        group_favorites = favorite_products[
            favorite_products['product_type'] == 'G'
        ].copy()
        
        # 날짜 변환 및 유효성 검사
        group_favorites['created_at'] = pd.to_datetime(group_favorites['created_at'])
        group_favorites = group_favorites.dropna(subset=['group_board_id'])
        group_favorites['group_board_id'] = group_favorites['group_board_id'].astype(int)
        
        # 최근 N일간 데이터 필터링
        latest_date = group_favorites['created_at'].max()
        cutoff_date = latest_date - timedelta(days=days)
        recent_favorites = group_favorites[group_favorites['created_at'] >= cutoff_date]
        
        return recent_favorites