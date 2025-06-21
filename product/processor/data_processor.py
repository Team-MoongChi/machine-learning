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