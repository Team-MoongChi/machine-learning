import pandas as pd
import numpy as np
from collections import Counter

from product.processor.data_processor import DataProcessor
from product.processor.category_processor import CategoryProcessor
from product.processor.product_score_processor import ProductSingleScoreProcessor
from product.feature.user_profile import UserProfiler
from product.embedding.embedding_generator import EmbeddingGenerator

def test_category_score_processor():
    # DataProcessor 인스턴스 생성 및 데이터 로드
    dp = DataProcessor()
    db_success = dp.load_db_data()
    assert db_success, "DB 데이터 로드 실패"

    # 카테고리 텍스트 생성
    categories_with_text = CategoryProcessor.make_category_text(dp.categories)
    print("=== 카테고리 텍스트 생성 결과 ===")
    print(categories_with_text[['category_id', 'category_path', 'category_text']].tail())

    # 상품-카테고리 조인
    joined_df = ProductSingleScoreProcessor.join(dp.products, categories_with_text)
    print("\n=== 상품-카테고리 조인 결과 ===")
    print(joined_df[['product_id', 'name', 'large_category', 'medium_category', 'small_category']].head())

    # 1인 가구 적합도 점수 계산
    scored_df = ProductSingleScoreProcessor.calc_score(joined_df)
    print("\n=== 1인 가구 적합도 점수 결과 ===")
    print(scored_df[scored_df['single_household_score']>=3.5][['name', 'single_household_score']])

    # 검증
    assert 'category_path' in categories_with_text.columns, "category_path 컬럼이 없습니다."
    assert 'category_text' in categories_with_text.columns, "category_text 컬럼이 없습니다."
    assert 'large_category' in joined_df.columns, "large_category 컬럼이 없습니다."
    assert 'single_household_score' in scored_df.columns, "single_household_score 컬럼이 없습니다."
    assert scored_df['single_household_score'].between(0, 10).all(), "점수 범위 오류"

    # scored_df 반환
    return scored_df

def test_user_profile_processor(scored_df):
    # DataProcessor 인스턴스 생성 및 데이터 로드
    dp = DataProcessor()
    db_success = dp.load_db_data()
    log_success = dp.load_log_data()
    assert db_success, "DB 데이터 로드 실패"
    assert log_success, "로그 데이터 로드 실패"

    # UserProfiler 인스턴스 생성 및 프로필 생성
    profiler = UserProfiler(
        products=scored_df,
        search_logs=dp.search_logs,
        click_logs=dp.click_logs,
        favorite_products=dp.favorite_products
    )
    user_profiles = profiler.create_user_profiles(dp.users)

    print("\n=== 사용자 프로필 생성 결과 (일부) ===")
    for uid, profile in list(user_profiles.items())[:3]:
        print(f"\nUser {uid}:")
        for k, v in profile.items():
            print(f"  {k}: {v}")

    # 사용자 타입별 분포 출력
    type_counts = Counter([p['user_type'] for p in user_profiles.values()])
    new_user_ids = [p['user_id'] for p in user_profiles.values() if p['user_type'] == 'new']
    print("\n=== 사용자 타입별 분포 ===")
    print(f"신규 사용자: {type_counts['new']}명")
    print(f"신규 사용자 user_id: {new_user_ids}")
    print(f"활성 사용자: {type_counts['active']}명")
    print(f"파워 사용자: {type_counts['power']}명")

    # 검증
    assert isinstance(user_profiles, dict), "user_profiles는 딕셔너리여야 합니다."
    for profile in user_profiles.values():
        assert 'user_id' in profile, "user_id 필드 누락"
        assert 'user_type' in profile, "user_type 필드 누락"
        assert 'search_keywords' in profile, "search_keywords 필드 누락"
    
    return user_profiles

def test_embedding_generator(scored_df, user_profiles):
    # 임베딩 생성기 인스턴스 생성
    embedding_generator = EmbeddingGenerator()

    # 상품 임베딩 생성
    product_embeddings, product_texts = embedding_generator.generate_product_embeddings(scored_df)
    print(f"상품 임베딩 shape: {product_embeddings.shape}")
    print(f"상품 임베딩 샘플 텍스트: {product_texts[:3]}")

    # 사용자 임베딩 생성 (임의의 사용자 1명)
    sample_user_id = list(user_profiles.keys())[0]
    sample_profile = user_profiles[sample_user_id]
    user_embedding, query_text = embedding_generator.generate_user_embedding(sample_profile)
    print(f"\n샘플 사용자 쿼리 텍스트: {query_text}")
    print(f"샘플 사용자 임베딩 shape: {user_embedding.shape}")

    # 4. 요약 정보 확인
    summary = embedding_generator.get_user_embedding_summary(sample_profile)
    print("\n=== 사용자 임베딩 요약 ===")
    for k, v in summary.items():
        print(f"{k}: {v}")

    # 5. 검증
    assert isinstance(product_embeddings, np.ndarray), "상품 임베딩은 np.ndarray여야 합니다."
    assert len(product_texts) == product_embeddings.shape[0], "텍스트 수와 임베딩 수 불일치"
    assert isinstance(user_embedding, np.ndarray), "사용자 임베딩은 np.ndarray여야 합니다."
    assert user_embedding.shape[0] == 1 or len(user_embedding.shape) == 2, "임베딩 shape 오류"
    assert isinstance(query_text, str), "쿼리 텍스트는 문자열이어야 합니다."
    assert abs(np.linalg.norm(user_embedding) - 1.0) < 1e-5, "임베딩 L2 정규화 오류"

if __name__ == "__main__":
    print("=== 카테고리/점수 파이프라인 테스트 ===")
    scored_df = test_category_score_processor()

    print("\n=== 사용자 프로필 파이프라인 테스트 ===")
    user_profiles = test_user_profile_processor(scored_df)
    
    print("\n=== EmbeddingGenerator 임베딩 테스트 ===")
    test_embedding_generator(scored_df, user_profiles)