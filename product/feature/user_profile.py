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

    def __init__(self, products: pd.DataFrame, search_logs: pd.DataFrame, click_logs: pd.DataFrame, favorite_products: pd.DataFrame):
        self.products = products  # 이전에 전처리된 데이터프레임 받아야함
        self.search_logs = search_logs
        self.click_logs = click_logs
        self.favorite_products = favorite_products
    
    @staticmethod
    def create_new_user_profile(user_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        신규 사용자의 기본 정보 기반 프로필 생성
        """
        
        age = UserProfiler.calculate_age(user_info["birth"])
        age_group = UserProfiler.get_age_group(age)

        profile = {
            "user_id": user_info["user_id"],
            "base_interest_category": user_info.get("interestCategory", None),
            "age_group": age_group,
            "gender": user_info.get("gender", None),
            "user_type": "new_user",

            # 행동 데이터 없음
            "search_keywords": [],
            "clicked_product_ids": [],
            "favorite_product_ids": [],
            "favorite_categories": [],
            "clicked_categories": [],

            # 통계 기본값
            "total_actions": 0,
            "search_count": 0,
            "click_count": 0,
            "favorite_count": 0
        }

        return profile
    
    def create_user_profiles(self, users_df: pd.DataFrame) -> Dict[Any, Dict]:
        """
        모든 유저에 대해 행동 로그과 기본 정보를 종합해 프로필을 만들어 반환
        """
        profiles = {}

        for _, user in users_df.iterrows():
            user_id = user['user_id']

            # 기본 정보 추출
            base_interest = user.get('interest_category', None)
            age = UserProfiler.calculate_age(user.get('birth', None))
            gender = user.get('gender', None)

            # 행동 로그 추출
            user_searches = self.filter_by_user(self.search_logs, user_id)
            user_clicks = self.filter_by_user(self.click_logs, user_id)
            user_favorites = self.filter_by_user(self.favorite_products, user_id)

            # 최근 N개 행동데이터 추출 
            search_keywords = user_searches['keyword'].dropna().tolist()[:10]
            clicked_product_ids = user_clicks['product_id'].dropna().tolist()[:20]
            favorite_product_ids = user_favorites['product_id'].dropna().astype(int).tolist()[:10]

            # 선호 카테고리 추출
            favorite_categories = self.extract_categories_from_products(favorite_product_ids)
            clicked_categories = self.extract_categories_from_clicks(user_clicks)

            # 활동량 기반 사용자 타입 분류
            total_actions = len(search_keywords) + len(clicked_product_ids) + len(favorite_product_ids)
            user_type = self.get_user_type(total_actions)

            # 프로필 딕셔너리 생성
            profiles[user_id] = {
                'user_id': user_id,
                'base_interest_category': base_interest,
                'age_group': UserProfiler.get_age_group(age),
                'gender': gender,
                'user_type': user_type,

                # 행동 데이터
                'search_keywords': search_keywords,
                'clicked_product_ids': clicked_product_ids,
                'favorite_product_ids': favorite_product_ids,
                'favorite_categories': favorite_categories,
                'clicked_categories': clicked_categories,

                # 통계
                'total_actions': total_actions,
                'search_count': len(search_keywords),
                'click_count': len(clicked_product_ids),
                'favorite_count': len(favorite_product_ids)
            }

        return profiles

    def filter_by_user(self, df: pd.DataFrame, user_id: Any) -> pd.DataFrame:
        """
        특정 사용자의 데이터만 필터링해서 반환
        """
        if df is not None and not df.empty:
            return df[df['user_id'] == user_id]
        return pd.DataFrame()

    @staticmethod
    def calculate_age(birth_str: str) -> int:
        """
        현재 년도를 가져와서 생년월일에서 나이를 계산 
        """
        try:
            birth_year = int(str(birth_str)[:4])
            current_year = datetime.now().year  # 현재 연도 자동 추출
            return current_year - birth_year
        except Exception:
            return 0
    
    @staticmethod
    def get_age_group(age: int) -> str:
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
    
    def extract_categories_from_products(self, product_ids: List[int]) -> List[str]:
        """
        찜한 상품 ID 리스트에서 대분류 카테고리 추출
        """
        categories = []
        for pid in product_ids:
            product = self.products[self.products['product_id'] == pid]
            if not product.empty:
                category = product.iloc[0].get('large_category', '')
                if category:
                    categories.append(category)
        return categories
    
    def extract_categories_from_clicks(self, user_clicks: pd.DataFrame) -> List[str]:
        """
        클릭 로그에서 이전에 추가한 item_category 컬럼에서 대분류만 추출
        """
        categories = []
        for _, click in user_clicks.iterrows():
            category_path = click.get('item_category', '')
            if category_path and '>' in category_path:
                large_category = category_path.split('>')[0].strip()
                categories.append(large_category)
        return categories