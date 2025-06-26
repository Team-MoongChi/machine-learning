import os
from datetime import datetime
from dotenv import load_dotenv

from prefect import task, flow, get_run_logger

from gauge.core.gauge_service import GaugeService
from gauge.managers.db_manager import DBManager

# 환경 변수 로드
load_dotenv()

@task
def database_connection():
    logger = get_run_logger()
    logger.info("=== 데이터베이스 연결 테스트 시작 ===")
    try:
        db_manager = DBManager()
        db_manager.connect()
        result = db_manager.execute_query("SELECT 1 as test")
        result[0]['test'] == 1, "쿼리 결과가 올바르지 않습니다"
        db_manager.disconnect()
        logger.info("✅ 데이터베이스 연결 테스트 성공")
        return True
    except Exception as e:
        logger.error(f"❌ 데이터베이스 연결 테스트 실패: {e}")
        return False

@task
def test_manner_percents_table():
    logger = get_run_logger()
    logger.info("=== manner_percents 테이블 테스트 시작 ===")
    try:
        db_manager = DBManager()
        db_manager.connect()
        result = db_manager.execute_query("DESCRIBE manner_percents")
        assert result is not None, "manner_percents 테이블에 접근할 수 없습니다"
        count_result = db_manager.execute_query("SELECT COUNT(*) as count FROM manner_percents")
        record_count = count_result[0]['count'] if count_result else 0
        db_manager.disconnect()
        logger.info(f"✅ manner_percents 테이블 테스트 성공 - 기존 레코드 수: {record_count}")
        return True
    except Exception as e:
        logger.error(f"❌ manner_percents 테이블 테스트 실패: {e}")
        return False
    
@task
def run_pipeline():
    service = GaugeService()
    result = service.run_full_pipeline()
    return service, result