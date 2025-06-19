import pandas as pd
from typing import Dict, Optional

class ResponseTransformer:
    """응답 데이터 변환 및 정제 담당 클래스"""
    
    @staticmethod
    def to_opensearch_doc(doc_id: str, result: Dict, days: int = 14) -> Dict:
        """OpenSearch 저장용으로 필드 정제 및 형 변환"""
        return {
            "doc_id": doc_id,
            "user_id": str(result['user_id']),
            "user_district": str(result['user_district']),
            "analysis_period": f"최근 {days}일",
            "total_local_groups": int(result['total_local_groups']),
            "returned_groups": int(len(result['groups'])),
            "popular_groups": [
                {
                    "group_id": str(group['group_board_id']),
                    "title": str(group['title']),
                    "location": str(group['location']),
                    "recent_favorites": int(group['recent_favorites']),
                    "latest_favorite": str(group['latest_favorite'].isoformat()),  # ISO8601 string
                }
                for group in result['groups']
            ]
        }

    @staticmethod
    def to_s3_doc(result: Dict, days: int = 14) -> Dict:
        """S3 저장용으로 필드 정제 및 형 변환"""
        return {
            "user_id": int(result['user_id']),
            "user_district": str(result['user_district']),
            "analysis_period": f"최근 {days}일 ({days // 7}주)",
            "total_local_groups": int(result['total_local_groups']),
            "returned_groups": int(len(result['groups'])),
            "popular_groups": [
                {
                    "group_id": int(group['group_board_id']),
                    "title": str(group['title']),
                    "location": str(group['location']),
                    "status": str(group['status']),
                    "recent_favorites": int(group['recent_favorites']),
                    "popularity_score": round(float(group['popularity_score']), 2),
                    "latest_favorite": str(group['latest_favorite']),
                    "days_since_latest": int(group['days_since_latest']),
                    "time_weight": round(float(group['time_weight']), 2),
                }
                for group in result['groups']
            ]
        }