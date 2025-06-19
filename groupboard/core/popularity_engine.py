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

    def calculate_activity_stats(
        self, regional_activities: pd.DataFrame
    ) -> pd.DataFrame:
        """공구방별 활동 통계(찜 수, 최근/최초 활동일) 계산"""
        activity_stats = regional_activities.groupby('group_board_id').agg({
            'user_id': 'count',
            'created_at': ['max', 'min']
        }).reset_index()
        activity_stats.columns = [
            'group_board_id', 'recent_favorites', 'latest_favorite', 'earliest_favorite'
        ]
        return activity_stats

    def merge_group_activity(
        self, regional_groups: pd.DataFrame, activity_stats: pd.DataFrame
    ) -> pd.DataFrame:
        """공구방 정보와 활동 통계 병합"""
        return regional_groups.merge(
            activity_stats,
            left_on='id',
            right_on='group_board_id',
            how='left'
        )
    