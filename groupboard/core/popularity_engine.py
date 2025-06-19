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
    
    def fill_missing_activity(self, result: pd.DataFrame) -> pd.DataFrame:
        """활동 없는 공구방의 기본값 보정 - 모든 공구방에 대해 인기도 점수 계산 필요"""
        result['recent_favorites'] = result['recent_favorites'].fillna(0).astype(int)
        result['latest_favorite'] = result['latest_favorite'].fillna(pd.Timestamp.now() - pd.Timedelta(days=999))
        return result

    def calculate_weights(self, result: pd.DataFrame) -> pd.DataFrame:
        """
        상태, 시간 가중치 계산 및 days_since_latest 컬럼 추가
        
        - status_weight: 공구방 상태별로 미리 정한 가중치
        - days_since_latest: 최근 찜 이후 며칠이 지났는지
        - time_weight: 최근일수록 높게, 오래됐을수록 낮게 주는 시간 가중치
        """
        result['status_weight'] = result['status'].map(lambda x: STATUS_WEIGHTS.get(x, 0.5))
        now = pd.Timestamp.now()
        result['days_since_latest'] = (now - result['latest_favorite']).dt.days
        result['time_weight'] = result['days_since_latest'].apply(get_time_weight)
        return result

    def calculate_popularity_score(self, result: pd.DataFrame) -> pd.DataFrame:
        """최종 인기도 점수 계산"""
        result['popularity_score'] = (
            result['recent_favorites'] *
            result['status_weight'] *
            result['time_weight']
        )
        return result
