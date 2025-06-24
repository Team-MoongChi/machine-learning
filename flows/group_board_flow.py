from prefect import flow, task
from groupboard.service.group_recommendation_service import GroupRecommendationService
from typing import Optional, Dict, List
from datetime import datetime

S3_BUCKET = "team6-mlops-bucket"
OPENSEARCH_INDEX = "group-recommendations"

@flow(name="group_board_flow")
def group_board_flow(top_n: int = 6):
    service = GroupRecommendationService(
        s3_bucket=S3_BUCKET,
        opensearch_index=OPENSEARCH_INDEX
    )
    if not service.initialize():
        raise ValueError("서비스 초기화 실패")

    result = service.upload_all_recommendations(s3_key=OPENSEARCH_INDEX, top_n=top_n)
    print(f"전체 추천 결과 {len(result)}건 업로드 완료")
    return result

if __name__ == "__main__":
    group_board_flow()
