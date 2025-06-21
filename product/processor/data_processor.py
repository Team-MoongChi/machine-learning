import os
import json
import pandas as pd
from typing import Tuple, List, Optional
from utils.storage.mysql_manager import MySQLManager

class DataProcessor:
    """데이터 로드 및 전처리 담당 클래스"""
    def __init__(self):
        self.mysql = MySQLManager()
        self.products = None
        self.categories = None
        self.users = None
        self.favorite_products = None
        self.search_logs = None
        self.click_logs = None
        
    def load_data(self) -> bool:
        """백엔드 MySQL에서 데이터 추출해서 반환"""
        try:
            self.products= self.mysql.read_table('products')
            self.categories = self.mysql.read_table('categories')
            self.users = self.mysql.read_table('users')
            favorite_products = self.mysql.read_table('favorite_products')
            
            # 상품 찜 데이터만 필터링 
            self.favorite_products = favorite_products[
                (favorite_products ['product_type'] == 'SHOPPING') &
                (favorite_products['product_id'].notna())
            ]
            return True
            
        except Exception as e:
            raise Exception(f"데이터 로드 실패: {e}")
    
    def clean_search_logs(self) -> pd.DataFrame:
        """검색 로그 데이터 정제 및 데이터프레임 변환"""
        rows = []
        for log in self.click_logs:
            try:
                user_id = int(log['user_id'])
                keyword = str(log['search_keyword']).strip()
                if not keyword:
                    continue
                rows.append({
                    'user_id': user_id,
                    'keyword': keyword,
                    'searched_at': log.get('searched_at', ''),
                    'search_result_count': int(log.get('search_result_count', 0))
                })
            except Exception:
                continue
        return pd.DataFrame(rows)

    def clean_click_logs(self, logs):
        """클릭 로그 데이터 정제 및 데이터프레임 변환"""
        rows = []
        for log in logs:
            try:
                user_id = int(log['user_id'])
                product_id = int(log['item_id'])
                rows.append({
                    'user_id': user_id,
                    'product_id': product_id,
                    'item_name': str(log.get('item_name', '')),
                    'clicked_at': log.get('clicked_at', ''),
                    'item_category': str(log.get('item_category', '')),
                    'item_price': int(log.get('item_price', 0))
                })
            except Exception:
                continue
        return pd.DataFrame(rows)
