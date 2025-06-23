from fastapi import APIRouter, HTTPException, status
from groupboard.service.group_recommendation_service import GroupRecommendationService
from fastapi.responses import JSONResponse
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
router = APIRouter()

recommendation_service = GroupRecommendationService(
    s3_bucket="team6-mlops-bucket", 
    opensearch_index="group-recommendations"  
)

@router.get("/groups/popular/{user_id}")
def get_popular_groups(user_id: int, top_n: int = 6) -> JSONResponse:
    """사용자별 인기 공구방 추천"""
    try:
        logger.info(f"사용자 {user_id} 추천 요청")
        
        # OpenSearch에서 기존 추천 결과 조회
        cached_result = recommendation_service.get_recommendation_from_opensearch(str(user_id))
        
        if cached_result["status"] == "success":
            logger.info(f"캐시된 추천 결과 반환 ({cached_result['timestamp']})")
            return JSONResponse(content=cached_result)
        
        logger.info(f"추천 결과 없음: user_id={user_id}")
        return JSONResponse(
            content={
                "status": "error",
                "message": f"사용자 {user_id}의 추천 결과가 없습니다.",
                "data": None
            }
    )
        
    except Exception as e:
        logger.error(f"추천 처리 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="추천 처리 중 오류가 발생했습니다"
        )