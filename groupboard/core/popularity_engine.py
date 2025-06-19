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
        # group_board_id가 NaN인 것 = 해당 공구방에 최근 활동이 없는 것 
        result = regional_groups.merge(
            activity_stats,
            left_on='id',
            right_on='group_board_id',
            how='left'
        )

        return result
    
    def fill_missing_activity(self, result: pd.DataFrame) -> pd.DataFrame:
        """활동 없는 공구방의 기본값 보정 - 모든 공구방에 대해 인기도 점수 계산 필요"""
        result['group_board_id'] = result['group_board_id'].fillna(result['id']).astype(int)
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
    
    def calculate_regional_popularity(
        self, district: str, group_boards_df: pd.DataFrame, recent_activities_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        특정 지역(구)의 공구방 인기도 계산 전체 플로우
        1. 해당 구의 공구방 추출
        2. 해당 구 공구방의 최근 활동 필터링
        3. 활동 통계 계산
        4. 공구방 정보와 통계 병합
        5. 결측값 보정
        6. 가중치 계산
        7. 인기도 점수 계산 및 정렬
        """
        # 1. 해당 구의 공구방 추출
        regional_groups = self.extract_regional_groups(district, group_boards_df)
        if len(regional_groups) == 0:
            return pd.DataFrame()

        # 2. 해당 구 공구방의 최근 활동 필터링
        regional_activities = self.filter_regional_activities(regional_groups, recent_activities_df)

        # 3. 활동이 없는 경우 기본값 반환
        if len(regional_activities) == 0:
            result = regional_groups.copy()
            result['recent_favorites'] = 0
            result['popularity_score'] = 0.0
            result['latest_favorite'] = None
            result['days_since_latest'] = 999
            result['time_weight'] = 0.1
            result['status_weight'] = result['status'].map(lambda x: STATUS_WEIGHTS.get(x, 0.5))
            return result.sort_values('id')

        # 4. 활동 통계 계산
        activity_stats = self.calculate_activity_stats(regional_activities)
        # 5. 공구방 정보와 통계 병합
        result = self.merge_group_activity(regional_groups, activity_stats)
        # 6. 결측값 보정
        result = self.fill_missing_activity(result)
        # 7. 가중치 계산
        result = self.calculate_weights(result)
        # 8. 인기도 점수 계산
        result = self.calculate_popularity_score(result)

        # 9. 인기도 순 정렬
        return result.sort_values(['popularity_score', 'latest_favorite'], ascending=[False, False])
