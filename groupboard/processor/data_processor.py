import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import re
from typing import Optional, Tuple
from config.group_board_config import ANALYSIS_DAYS

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

    def join_all_data(self, recent_favorites: pd.DataFrame, 
                     users: pd.DataFrame, group_boards: pd.DataFrame) -> pd.DataFrame:
        """찜하기, 사용자, 공구방 데이터를 조인"""
        
        # 사용자 정보 조인
        user_cols = ['id', 'name', 'address']
        joined_data = recent_favorites.merge(
            users[user_cols],
            left_on='user_id',
            right_on='id',
            how='left',
            suffixes=('', '_user')
        )
        
        # 공구방 정보 조인
        group_cols = ['id', 'title', 'location', 'status', 'total_users']
        final_data = joined_data.merge(
            group_boards[group_cols],
            left_on='group_board_id',
            right_on='id',
            how='left',
            suffixes=('', '_group')
        )
        
        # 컬럼 정리
        final_data = self._clean_columns(final_data)
        
        return final_data

    def _clean_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """중복 컬럼 제거 및 정리"""
        columns_to_drop = []
        for col in ['id_user', 'id_group', 'id_y']:
            if col in df.columns:
                columns_to_drop.append(col)
        
        if columns_to_drop:
            df = df.drop(columns=columns_to_drop)
        
        if 'id_x' in df.columns:
            df = df.rename(columns={'id_x': 'favorite_id'})
        elif 'id' in df.columns and 'favorite_id' not in df.columns:
            df = df.rename(columns={'id': 'favorite_id'})
            
        return df