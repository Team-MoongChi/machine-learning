import pandas as pd
from typing import Dict, Optional, List
from processor.data_processor import DataProcessor
from processor.location_processor import LocationProcessor
from core.popularity_engine import PopularityEngine
from config.group_board_config import TOP_N_GROUPS

class RecommendationEngine:
    """공구방 추천 엔진 클래스"""
    
    def __init__(self, data_loader: DataProcessor):
        self.data_loader = data_loader
        self.popularity_engine = PopularityEngine()
        
    def get_user_recommendations(self, user_id: int, top_n: int = TOP_N_GROUPS) -> Optional[Dict]:
        """특정 사용자의 지역 기반 공구방 추천"""
        
        # 1. 사용자 지역 확인
        users_df = self.data_loader.get_users()
        user_district = LocationProcessor.get_user_district(user_id, users_df)
        
        if not user_district:
            return None
        
        # 2. 해당 지역의 공구방 인기도 계산
        group_boards_df = self.data_loader.get_group_boards()
        recent_activities_df = self.data_loader.get_recent_activities()
        
        popularity_result = self.popularity_engine.calculate_regional_popularity(
            user_district, group_boards_df, recent_activities_df
        )
        
        if len(popularity_result) == 0:
            return None
        
        # 3. 상위 N개 선택
        top_groups = popularity_result.head(top_n)
        
        return {
            'user_id': user_id,
            'user_district': user_district,
            'total_local_groups': len(popularity_result),
            'groups': top_groups.to_dict('records')
        }