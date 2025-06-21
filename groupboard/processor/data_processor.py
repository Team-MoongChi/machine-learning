import pandas as pd
from datetime import datetime, timedelta
from typing import Tuple
from config.group_board_config import ANALYSIS_DAYS
from utils.storage.mysql_manager import MySQLManager

class DataProcessor:
    """데이터 로드 및 전처리 담당 클래스"""
    
    def __init__(self):
        self.mysql = MySQLManager()
        self.users = None
        self.group_boards = None
        self.recent_activities = None
        
    def load_data(self) -> bool:
        """백엔드 MySQL에서 데이터 추출해서 반환"""
        try:
            favorite_products = self.mysql.read_table('favorite_products')
            self.users = self.mysql.read_table('users')
            self.group_boards = self.mysql.read_table('group_boards')
            self.recent_activities = self.filter_recent_group_favorites(favorite_products)
            
            return True
            
        except Exception as e:
            raise Exception(f"데이터 로드 실패: {e}")
    
    def filter_recent_group_favorites(self, favorite_products: pd.DataFrame, 
                                    days: int = ANALYSIS_DAYS) -> pd.DataFrame:
        """최근 N일간 공구방 찜하기 데이터 필터링"""
        
        # 공구방 찜하기만 필터링
        print(favorite_products['product_type'].unique())
        
        group_favorites = favorite_products[
            favorite_products['product_type'] == 'GROUP'
        ].copy()

        print(f"공구방 찜하기 데이터 수: {len(group_favorites)}")
        
        # 날짜 변환 및 유효성 검사
        group_favorites['created_at'] = pd.to_datetime(group_favorites['created_at'])
        group_favorites = group_favorites.dropna(subset=['group_board_id'])
        group_favorites['group_board_id'] = group_favorites['group_board_id'].astype(int)
        
        # 최근 N일간 데이터 필터링
        print(group_favorites['created_at'].dtype)
        latest_date = group_favorites['created_at'].max()

        cutoff_date = latest_date - timedelta(days=days)
        print(f"최신 날짜: {latest_date}, 컷오프 날짜: {cutoff_date}")

        sorted_df = group_favorites.sort_values(by='created_at', ascending=False)
        print(sorted_df['created_at'].head().unique())

        recent_favorites = group_favorites[group_favorites['created_at'] >= cutoff_date]
        print(len(recent_favorites))
        return recent_favorites