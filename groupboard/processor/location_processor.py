import pandas as pd
import re
from typing import Optional

class LocationProcessor:
    """지역 정보 처리 담당 클래스"""
    
    @staticmethod
    def extract_district(address: str) -> Optional[str]:
        """주소에서 구 정보 추출"""
        if pd.isna(address) or not isinstance(address, str):
            return None
        
        district_match = re.search(r'([가-힣]+구)', address)
        return district_match.group(1) if district_match else None
    
    @staticmethod
    def add_district_info(data: pd.DataFrame) -> pd.DataFrame:
        """데이터에 구 정보 컬럼 추가"""
        data_copy = data.copy()
        data_copy['user_district'] = data_copy['address'].apply(
            LocationProcessor.extract_district
        )
        data_copy['group_district'] = data_copy['location'].apply(
            LocationProcessor.extract_district
        )
        return data_copy

    @staticmethod
    def get_user_district(user_id: int, users_df: pd.DataFrame) -> Optional[str]:
        """사용자 ID로 구 정보 조회"""
        user_info = users_df[users_df['id'] == user_id]
        if len(user_info) == 0:
            return None

        user_address = user_info['address'].iloc[0]
        return LocationProcessor.extract_district(user_address)

    @staticmethod
    def get_groups_in_district(district: str, group_board_df: pd.DataFrame) -> pd.DataFrame:
        """특정 구의 공구방들 조회"""
        group_board_df = group_board_df.copy()
        group_board_df['district'] = group_board_df['location'].apply(
            LocationProcessor.extract_district)
        return group_board_df[group_board_df['district'] == district]
