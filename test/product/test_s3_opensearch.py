from product.transformer.recommendation_transformer import RecommendationTransformer
from utils.storage.opensearch_manager import OpenSearchManager

def test_recommendation_flow():
    # S3에서 가져온 추천 데이터 
    test2_data = {
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
    print("\n1. Raw data from S3:", test2_data)

    # OpenSearch에 맞는 데이터로 변환
    transformer = RecommendationTransformer()
    core_data = transformer.to_core_data(test2_data)
    print("\n2. Transformed data for OpenSearch:", core_data)

    # OpenSearch에 업로드
    opensearch = OpenSearchManager(
        index="test_recommendations"
    )
    doc_id = f"user_{test2_data['user_id']}"
    opensearch.upload(doc_id, core_data)

     # OpenSearch에서 데이터 조회
    retrieved_data = opensearch.get(doc_id)
    print("\n4. Retrieved data from OpenSearch:", retrieved_data)
    
    # 저장된 데이터 검증
    assert retrieved_data == core_data, "Retrieved data doesn't match uploaded data"
    print("\n5. Data verification successful!")

if __name__ == "__main__":
    test_recommendation_flow()