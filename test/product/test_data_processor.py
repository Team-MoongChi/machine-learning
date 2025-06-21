import os
import pandas as pd
from product.processor.data_processor import DataProcessor

def test_data_processor():
    # DataProcessor 인스턴스 생성
    dp = DataProcessor()

    # DB 데이터 로드
    db_success = dp.load_db_data()
    print(dp.categories.head())
    print(dp.favorite_products.head())
    print(dp.products.head())
    print(dp.users.head())

    if not db_success:
        print("DB 데이터 로드 실패")
        return

    # 로그 데이터 로드 및 처리
    log_success = dp.load_log_data()
    if not log_success:
        print("로그 데이터 로드 실패")
        return

    # 결과 출력
    print("\n[검색 로그 데이터프레임]")
    print(dp.search_logs)
    print("\n[클릭 로그 데이터프레임]")
    print(dp.click_logs)

    # 검증
    assert isinstance(dp.search_logs, pd.DataFrame), "search_logs는 DataFrame이어야 합니다."
    assert isinstance(dp.click_logs, pd.DataFrame), "click_logs는 DataFrame이어야 합니다."
    assert not dp.search_logs.empty, "search_logs는 비어있지 않아야 합니다."
    assert not dp.click_logs.empty, "click_logs는 비어있지 않아야 합니다."
    print("\n테스트 통과!")

if __name__ == "__main__":
    test_data_processor()