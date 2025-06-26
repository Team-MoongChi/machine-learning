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

@task
def validate_data_loading(service):
    logger = get_run_logger()
    if hasattr(service, 'merged_all') and service.merged_all is not None and not service.merged_all.empty:
        logger.info(f"✅ 데이터 로딩 검증 성공 - 데이터 크기: {service.merged_all.shape}")
        return True
    logger.error("❌ 데이터 로딩 검증 실패")
    return False

@task
def validate_feature_engineering(service):
    logger = get_run_logger()
    leader_features_ok = False
    follower_features_ok = False

    if hasattr(service, 'leader_data') and not service.leader_data.empty:
        required_leader_features = ['leader_role_count', 'positive_keyword_count', 'review_score_normalized']
        if all(col in service.leader_data.columns for col in required_leader_features):
            leader_features_ok = True
            logger.info(f"✅ 리더 피처 생성 검증 성공 - 데이터 크기: {service.leader_data.shape}")

    if hasattr(service, 'follower_data') and not service.follower_data.empty:
        required_follower_features = ['participant_role_count', 'positive_keyword_count', 'review_score_normalized']
        if all(col in service.follower_data.columns for col in required_follower_features):
            follower_features_ok = True
            logger.info(f"✅ 팔로워 피처 생성 검증 성공 - 데이터 크기: {service.follower_data.shape}")

    if leader_features_ok or follower_features_ok:
        return True
    logger.error("❌ 피처 생성 검증 실패")
    return False

@task
def validate_target_generation(service):
    logger = get_run_logger()
    leader_targets_ok = False
    follower_targets_ok = False

    if hasattr(service, 'leader_data') and 'leader_degree' in service.leader_data.columns:
        leader_scores = service.leader_data['leader_degree']
        if leader_scores.min() >= 0 and leader_scores.max() <= 100:
            leader_targets_ok = True
            logger.info(f"✅ 리더 타겟 생성 검증 성공 - 평균 점수: {leader_scores.mean():.2f}")

    if hasattr(service, 'follower_data') and 'participant_degree' in service.follower_data.columns:
        follower_scores = service.follower_data['participant_degree']
        if follower_scores.min() >= 0 and follower_scores.max() <= 100:
            follower_targets_ok = True
            logger.info(f"✅ 팔로워 타겟 생성 검증 성공 - 평균 점수: {follower_scores.mean():.2f}")

    if leader_targets_ok or follower_targets_ok:
        return True
    logger.error("❌ 타겟 생성 검증 실패")
    return False

@task
def validate_model_training(service):
    logger = get_run_logger()
    leader_training_ok = False
    follower_training_ok = False

    if hasattr(service, 'leader_data') and 'new_leader_degree' in service.leader_data.columns:
        leader_training_ok = True
        logger.info("✅ 리더 모델 훈련 검증 성공")

    if hasattr(service, 'follower_data') and 'new_participant_degree' in service.follower_data.columns:
        follower_training_ok = True
        logger.info("✅ 팔로워 모델 훈련 검증 성공")

    if leader_training_ok or follower_training_ok:
        return True
    logger.error("❌ 모델 훈련 검증 실패")
    return False

@task
def validate_model_evaluation(result):
    logger = get_run_logger()
    if 'results' in result and result['results']:
        evaluation_ok = False
        if 'leader_evaluation' in result['results']:
            leader_metrics = result['results']['leader_evaluation']['metrics']
            if 'mae' in leader_metrics and 'r2' in leader_metrics:
                evaluation_ok = True
                logger.info(f"✅ 리더 모델 평가 검증 성공 - MAE: {leader_metrics['mae']:.4f}, R²: {leader_metrics['r2']:.4f}")
        if 'follower_evaluation' in result['results']:
            follower_metrics = result['results']['follower_evaluation']['metrics']
            if 'mae' in follower_metrics and 'r2' in follower_metrics:
                evaluation_ok = True
                logger.info(f"✅ 팔로워 모델 평가 검증 성공 - MAE: {follower_metrics['mae']:.4f}, R²: {follower_metrics['r2']:.4f}")
        return evaluation_ok
    logger.error("❌ 모델 평가 검증 실패")
    return False

@task
def validate_db_update(result):
    logger = get_run_logger()
    if result.get('update_count', 0) > 0:
        logger.info(f"✅ 데이터베이스 업데이트 검증 성공 - 업데이트 건수: {result['update_count']}")
        return True
    logger.error("❌ 데이터베이스 업데이트 검증 실패")
    return False

@flow(name="leader_flow")
def leader_flow():
    logger = get_run_logger()
    logger.info("=== 전체 파이프라인 통합 테스트 시작 ===")
    service, result = run_pipeline()
    validations = [
        validate_data_loading(service),
        validate_feature_engineering(service),
        validate_target_generation(service),
        validate_model_training(service),
        validate_model_evaluation(result),
        validate_db_update(result),
    ]
    passed = sum(validations)
    total = len(validations)
    logger.info(f"\n📊 세부 검증 결과: {passed}/{total} 성공")
    if passed == total:
        logger.info("✅ 전체 파이프라인 통합 테스트 성공")
        return True
    else:
        logger.warning("⚠️ 일부 검증이 실패했지만 파이프라인은 완료됨")
        return False