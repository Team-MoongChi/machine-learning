from product.service.recommendation_service import RecommendationService
from product.service.new_user_recommendation_service import NewUserRecommendationService
import datetime

def test_delete_storage_data(service, s3_prefix: str):
    """S3와 OpenSearch의 기존 데이터 삭제"""

    print("\n기존 데이터 삭제 중...")
    # S3 데이터 삭제
    deleted_s3 = service.repository.s3.delete_prefix(s3_prefix)
    print(f"S3 삭제된 객체 수: {deleted_s3}")
    # OpenSearch 데이터 삭제
    deleted_os = service.repository.opensearch.delete_all()
    print(f"OpenSearch 삭제된 문서 수: {deleted_os}")

def test_run_full_pipeline(service):
    """추천 파이프라인 전체 실행 (업로드)"""

    service.run_full_pipeline()
    print("run_full_pipeline 정상 동작 테스트 통과")

def test_get_recommendation(service, user_id):
    """추천 결과 조회 테스트"""
    result = service.repository.get_recommendation_from_opensearch(user_id)
    assert result is not None, f"추천 결과 조회 실패: user_id={user_id}"
    print(f"사용자 {user_id}의 추천 결과: {result}")

def run_all_tests():
    print("===== RecommendationService 통합 테스트 시작 =====")
    service = RecommendationService()

    # 1. 기존 데이터 삭제
    print("\n1. 기존 데이터 삭제 테스트")
    test_delete_storage_data(service, s3_prefix="recommendations/")

    # 2. 파이프라인 실행(추천 결과 업로드)
    print("\n2. 추천 결과 업로드(파이프라인 실행) 테스트")
    test_run_full_pipeline(service)

    # 3. 추천 결과 조회 테스트 (예: user_id=5)
    print("\n3. 추천 결과 조회 테스트")
    test_get_recommendation(service, user_id=180)

    print("\n===== 모든 RecommendationService 테스트 완료 =====")

if __name__ == "__main__":
    run_all_tests()

    new_user_info = {
        'user_id' : 250,
        'gender': 'FEMALE',
        'birth': '2000-12-11',
        'interestCategory': '신선식품'
    }
    service = NewUserRecommendationService()
    recommendations = service.recommend(new_user_info)

    # assert문으로 결과 검증
    assert isinstance(recommendations, list), "추천 결과는 리스트여야 합니다."
    assert len(recommendations) > 0, "추천 결과가 비어있지 않아야 합니다."
    assert all(isinstance(item, dict) for item in recommendations), "추천 결과 각 항목은 딕셔너리여야 합니다."
    print("추천 결과:", recommendations)

