from fastapi import APIRouter, HTTPException
import logging
import datetime
import traceback

from config.opensearch_mappings import PRODUCT_MAPPING, GROUP_RECOMMENDATION_MAPPING
from api.dto.request.NewUserRequest import NewUserRequest
from api.dto.response.NewUserResponse import NewUserResponse
from product.service.new_user_recommendation_service import NewUserRecommendationService
from groupboard.service.group_recommendation_service import GroupRecommendationService

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# RecommendationService 인스턴스 생성
product_service = NewUserRecommendationService()

groupboard_service = GroupRecommendationService(
    s3_bucket="team6-mlops-bucket", 
    opensearch_index="group-recommendations",
    mapping=GROUP_RECOMMENDATION_MAPPING
)

@router.post("/new-user", response_model=NewUserResponse)
def recommend_for_new_user(request: NewUserRequest):
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    doc_id = f"user_{request.user_id}_{timestamp}"

    # 주소에서 구 추출 및 인기 공구방 추천
    try:
        groupboard_service.initialize()
        group_rec = groupboard_service.upload_new_recommendation("group-recommendations", request.user_id, request.address, top_n=6)
        if group_rec is None:
            raise ValueError("해당 지역의 인기 공구방 정보가 없습니다.")
        
    except Exception as e:
        traceback.print_exc()

        raise HTTPException(status_code=500, detail=f"공구방 추천 실패: {e}")

    # 신규 사용자 상품 추천
    try:
        new_user_info = {
            "user_id": request.user_id,
            "gender": request.gender,
            "birth": request.birth,
            "interestCategory": request.interestCategory
        }

        product_rec = product_service.recommend(new_user_info=new_user_info, top_k=4)
     
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"상품 추천 실패: {e}")

    # 결과 포맷팅 및 반환
    response_data = {
        "doc_id": doc_id,
        "user_id": str(request.user_id),
        "user_district": group_rec.get("user_district"),
        "analysis_period": "최근 14일",
        "total_local_groups": group_rec.get("total_local_groups"),
        "returned_groups": len(group_rec.get("groups", [])),
        "popular_groups": group_rec.get("groups", [])
    }

    return NewUserResponse(
        status="success",
        data=response_data,
        timestamp=timestamp
    )