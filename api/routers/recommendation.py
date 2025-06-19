from fastapi import APIRouter, HTTPException
from recommendation.service.recommendation_repository import RecommendationRepository
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# RecommendationService 인스턴스 생성
service = RecommendationRepository(
        s3_bucket="team6-mlops-bucket",
        opensearch_index="recommendations"
    )

@router.get("/recommendations/{user_id}")
def get_recommendations(user_id: str):
    """
    사용자별 추천 결과를 조회
    """
    try:
        doc_id = f"user_{user_id}"
        recommendations = service.get_from_opensearch(doc_id)
        
        if not recommendations:
            raise HTTPException(
                status_code=404, 
                detail=f"Recommendations not found for user {user_id}"
            )
            
        return recommendations
        
    except Exception as e:
        logger.error(f"Error getting recommendations for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while fetching recommendations"
        )
