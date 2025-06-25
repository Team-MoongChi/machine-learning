import pandas as pd
from typing import Dict, Optional, List
from groupboard.processor.data_processor import DataProcessor
from groupboard.processor.location_processor import LocationProcessor
from groupboard.core.popularity_engine import PopularityEngine
from config.group_board_config import TOP_N_GROUPS
import logging

logger = logging.getLogger(__name__)

class RecommendationEngine:
    """공구방 추천 엔진 클래스"""
    
    def __init__(self, data_loader: DataProcessor):
        self.data_loader = data_loader
        self.popularity_engine = PopularityEngine()
        
    def get_new_user_recommendations(self, user_id: int, address: str, top_n: int = TOP_N_GROUPS) -> Optional[Dict]:
        """새로운 사용자의 지역 기반 공구방 추천"""
        
        # 사용자 지역 확인
        user_district = LocationProcessor.extract_district(address)
        print(f"User {user_id} - District: {user_district}")
        if not user_district:
            return None
        
        # 해당 지역의 공구방 추출
        group_boards_df = self.data_loader.group_boards

        group_by_district = LocationProcessor.get_groups_in_district(user_district, group_boards_df).head(6)
        print(group_by_district.head())
        
        # 인기순 정렬 후 상위 6개 그룹 추출 (total_users 기준)
        top_groups = group_by_district.sort_values(by="total_users", ascending=False).head(6)

        return {
            'user_id': user_id,
            'user_district': user_district,
            'total_local_groups': len(group_by_district),
            'groups': top_groups.to_dict('records')
        }

    def get_user_recommendations(self, user_id: int, top_n: int = TOP_N_GROUPS) -> Optional[Dict]:
        """특정 사용자의 지역 기반 공구방 추천"""
        
        # 1. 사용자 지역 확인
        users_df = self.data_loader.users
        user_district = LocationProcessor.get_user_district(user_id, users_df)
        
        if not user_district:
            return None
        
        # 2. 해당 지역의 공구방 인기도 계산
        group_boards_df = self.data_loader.group_boards
        recent_activities_df = self.data_loader.recent_activities
        
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
    
    
    def get_all_user_recommendations(self, top_n: int = TOP_N_GROUPS) -> List[Dict]:
        """모든 사용자의 추천 결과 생성"""
        
        users_df = self.data_loader.users
        all_user_ids = users_df['user_id'].tolist()
        logger.info(len(all_user_ids))
        
        recommendations = []
        
        for user_id in all_user_ids:
            result = self.get_user_recommendations(user_id, top_n)
            if result:
                recommendations.append(result)
        
        logger.info(f"Total recommendations generated: {len(recommendations)}")
        return recommendations