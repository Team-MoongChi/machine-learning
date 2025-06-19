import pandas as pd
from datetime import datetime
from typing import Dict, Optional
from config.group_board_config import STATUS_WEIGHTS, get_time_weight
from groupboard.processor.location_processor import LocationProcessor

class PopularityEngine:
    """공구방 인기도 계산 클래스"""
    
    def extract_regional_groups(
            self, district: str, group_board_df: pd.DataFrame
    ) -> pd.DataFrame:
        """특정 구의 공구방만 추출"""
        return LocationProcessor.get_groups_in_district(district, group_board_df)
    
    def filter_regional_activities(
            self, regional_groups: pd.DataFrame, recent_activities_df: pd.DataFrame
    ) -> pd.DataFrame:
        """해당 지역 공구방들의 최근 활동만 필터링"""
        regional_group_ids = regional_groups['id'].tolist()
        return recent_activities_df[recent_activities_df['group_board_id'].isin(regional_group_ids)]

    
    