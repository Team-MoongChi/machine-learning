import pandas as pd
from product.processor.data_processor import DataProcessor
from product.processor.category_processor import CategoryProcessor
from product.processor.product_score_processor import ProductSingleScoreProcessor

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

if __name__ == "__main__":
    test_category_score_processor()