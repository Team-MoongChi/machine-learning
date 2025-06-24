from prefect import flow, task
from groupboard.service.group_recommendation_service import GroupRecommendationService
from typing import Optional, Dict, List
from datetime import datetime

S3_BUCKET = "team6-mlops-bucket"
OPENSEARCH_INDEX = "group-recommendations"

@task
def initialize_service() -> GroupRecommendationService:
    service = GroupRecommendationService(
        s3_bucket=S3_BUCKET,
        opensearch_index=OPENSEARCH_INDEX
    )
    if not service.initialize():
        raise ValueError("서비스 초기화 실패")
    return service

@task
def get_all_user_ids(service: GroupRecommendationService) -> List[int]:
    return service.data_processor.users["user_id"].tolist()

@task(retries=2, retry_delay_seconds=3)
def generate_and_store_user_recommendation(
    service: GroupRecommendationService,
    user_id: int,
    s3_key: str,
    top_n: int = 6
) -> Optional[Dict]:
    user_info = service.data_processor.users.set_index("user_id").loc[user_id]
    address = user_info["address"]

    rec = service.upload_new_recommendation(s3_key=s3_key, user_id=user_id, address=address, top_n=top_n)
    return rec if rec else None

@flow(name="group_board_flow")
def group_board_flow(top_n: int = 6):
    service = initialize_service()
    user_ids = get_all_user_ids(service)

    recommendations = []
    for user_id in user_ids:
        rec = generate_and_store_user_recommendation(service, user_id, OPENSEARCH_INDEX, top_n)
        if rec:
            recommendations.append(rec)

    print(f"전체 사용자 추천 생성 완료: {len(recommendations)}명")
    return recommendations

if __name__ == "__main__":
    group_board_flow()
