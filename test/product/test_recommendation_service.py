from recommendation.service.recommendation_repository import RecommendationRepository

def test_recommendation_service():
    # 서비스 인스턴스 생성
    service = RecommendationRepository(
        s3_bucket="team6-mlops-bucket",
        opensearch_index="test_recommendations"
    )

    # 테스트 데이터 준비
    test_data = {
        "user_id": 5,
        "experiment_id": 12,
        "run_id": "test_run",
        "recommendations": [
            {"item_id": 5, "score": 0.951},
            {"item_id": 40, "score": 0.894},
            {"item_id": 8, "score": 0.863},
            {"item_id": 3, "score": 0.845}
        ]
    }
    
    # 저장 테스트
    s3_key = f"recommendations/user_{test_data['user_id']}/test.json"
    doc_id = f"user_{test_data['user_id']}"
    service.save_recommendation(s3_key, doc_id, test_data)
    print("\n1. Saved recommendation data")

    # 조회 테스트
    retrieved_data = service.get_recommendation(doc_id)
    print("\n2. Retrieved data:", retrieved_data)

    # 데이터 검증
    expected_backend_data = {
        "user_id": 5,
        "recommended_item_ids": [5, 40, 8, 3],
        "experiment_id": 12,
        "run_id": "test_run"
    }
    assert retrieved_data == expected_backend_data, "Retrieved data doesn't match expected format"
    print("\n3. Data verification successful!")

if __name__ == "__main__":
    test_recommendation_service()