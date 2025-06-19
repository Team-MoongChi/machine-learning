from groupboard.service.group_recommendation_service import GroupRecommendationService

def test_initialize():
    # 서비스 인스턴스 생성
    service = GroupRecommendationService(
        data_path="data",
        s3_bucket="team6-mlops-bucket",
        opensearch_index="group-recommendations"
    )
    
    # 초기화 테스트
    result = service.initialize()
    assert result == True, "서비스 초기화에 실패했습니다"
    assert service.recommendation_engine is not None, "추천 엔진이 생성되지 않았습니다"
    print("초기화 테스트 성공")

def test_upload_recommendations():
    # 서비스 인스턴스 생성
    service = GroupRecommendationService(
        data_path="data",
        s3_bucket="team6-mlops-bucket",
        opensearch_index="group-recommendations"
    )
    
    # 초기화
    service.initialize()
    
    # 추천 결과 업로드 테스트
    results = service.upload_all_recommendations("group-recommendations")
    assert results is not None, "추천 결과 업로드에 실패했습니다"
    print(f"업로드된 추천 결과: {results}")

def test_get_recommendation():
    # 서비스 인스턴스 생성
    service = GroupRecommendationService(
        data_path="data",
        s3_bucket="team6-mlops-bucket",
        opensearch_index="group-recommendations"
    )
    
    # OpenSearch에서 추천 결과 조회 테스트
    user_id = "5"
    result = service.get_recommendation_from_opensearch(user_id)
    
    assert result is not None, "추천 결과 조회에 실패했습니다"
    print(f"사용자 {user_id}의 추천 결과: {result}")

def test_delete_storage_data(s3_prefix: str) -> None:
    """S3와 OpenSearch의 기존 데이터 삭제"""
    service = GroupRecommendationService(
        data_path="data",
        s3_bucket="team6-mlops-bucket",
        opensearch_index="group-recommendations"
    )
    print("\n기존 데이터 삭제 중...")
    
    # S3 데이터 삭제
    deleted_s3 = service.s3_manager.delete_prefix(s3_prefix)
    print(f"S3 삭제된 객체 수: {deleted_s3}")
    
    # OpenSearch 데이터 삭제
    deleted_os = service.opensearch.delete_all()
    print(f"OpenSearch 삭제된 문서 수: {deleted_os}")

def delete_index():
    """OpenSearch 인덱스 삭제"""
    service = GroupRecommendationService(
        data_path="data",
        s3_bucket="team6-mlops-bucket",
        opensearch_index="group-recommendations"
    )
    print("\nOpenSearch 인덱스 삭제 중...")
    
    deleted_index = service.opensearch.delete_index()
    print(f"OpenSearch 인덱스 삭제 결과: {deleted_index}")

def run_all_tests():
    print("===== 테스트 시작 =====")
    
    print("\n1. 초기화 테스트")
    test_initialize()

    print("\n1. 기존 데이터 삭제 테스트")
    test_delete_storage_data("group-recommendations")
    
    print("\n2. 추천 결과 업로드 테스트")
    test_upload_recommendations()
    
    print("\n3. 추천 결과 조회 테스트")
    test_get_recommendation()
    
    print("\n===== 모든 테스트 완료 =====")

if __name__ == "__main__":
    run_all_tests()