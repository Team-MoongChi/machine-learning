import sys
import os
from datetime import datetime
from dotenv import load_dotenv

from gauge.core.gauge_service import GaugeService
from gauge.managers.db_manager import DBManager

# 환경 변수 로드
load_dotenv()

def test_initialize():
  """GaugeService 초기화 테스트"""
  print("\n=== 초기화 테스트 시작 ===")

  try:
    # 서비스 인스턴스 생성
    service = GaugeService()

    # 데이터베이스 연결 테스트
    service.setup_database_connection()

    assert service.db_manager is not None, "DBManager가 생성되지 않았습니다"
    assert service.data_loader is not None, "DataLoader가 생성되지 않았습니다"

    print("✅ 초기화 테스트 성공")

    # 연결 해제
    service.db_manager.disconnect()

    return True

  except Exception as e:
    print(f"❌ 초기화 테스트 실패: {e}")
    return False

def test_data_loading():
  """데이터 로딩 및 조인 테스트"""
  print("\n=== 데이터 로딩 테스트 시작 ===")

  try:
    service = GaugeService()
    service.setup_database_connection()

    # 데이터 로딩 및 조인 테스트
    merged_data = service.load_and_merge_data()

    assert merged_data is not None, "데이터 로딩에 실패했습니다"
    assert not merged_data.empty, "조인된 데이터가 비어있습니다"
    assert 'user_id' in merged_data.columns, "user_id 컬럼이 없습니다"
    assert 'role' in merged_data.columns, "role 컬럼이 없습니다"

    print(f"✅ 데이터 로딩 테스트 성공 - 데이터 크기: {merged_data.shape}")

    # 연결 해제
    service.db_manager.disconnect()

    return True

  except Exception as e:
    print(f"❌ 데이터 로딩 테스트 실패: {e}")
    return False

def test_feature_generation():
  """피처 생성 테스트"""
  print("\n=== 피처 생성 테스트 시작 ===")

  try:
    service = GaugeService()
    service.setup_database_connection()

    # 데이터 로딩
    service.load_and_merge_data()

    # 피처 생성
    service.generate_features()

    # 리더 데이터 검증
    if not service.leader_data.empty:
      assert 'leader_role_count' in service.leader_data.columns, "리더 피처가 생성되지 않았습니다"
      assert 'positive_keyword_count' in service.leader_data.columns, "키워드 피처가 생성되지 않았습니다"
      print(f"✅ 리더 피처 생성 성공 - 데이터 크기: {service.leader_data.shape}")

    # 팔로워 데이터 검증
    if not service.follower_data.empty:
      assert 'participant_role_count' in service.follower_data.columns, "팔로워 피처가 생성되지 않았습니다"
      assert 'positive_keyword_count' in service.follower_data.columns, "키워드 피처가 생성되지 않았습니다"
      print(f"✅ 팔로워 피처 생성 성공 - 데이터 크기: {service.follower_data.shape}")

    # 연결 해제
    service.db_manager.disconnect()

    return True

  except Exception as e:
    print(f"❌ 피처 생성 테스트 실패: {e}")
    return False

def test_target_generation():
  """타겟 생성 테스트"""
  print("\n=== 타겟 생성 테스트 시작 ===")

  try:
    service = GaugeService()
    service.setup_database_connection()

    # 데이터 로딩 및 피처 생성
    service.load_and_merge_data()
    service.generate_features()

    # 타겟 생성
    service.generate_targets()

    # 리더 타겟 검증
    if not service.leader_data.empty:
      assert 'leader_degree' in service.leader_data.columns, "리더 타겟이 생성되지 않았습니다"
      leader_scores = service.leader_data['leader_degree']
      assert leader_scores.min() >= 0 and leader_scores.max() <= 100, "리더 점수 범위가 올바르지 않습니다"
      print(f"✅ 리더 타겟 생성 성공 - 평균 점수: {leader_scores.mean():.2f}")

    # 팔로워 타겟 검증
    if not service.follower_data.empty:
      assert 'participant_degree' in service.follower_data.columns, "팔로워 타겟이 생성되지 않았습니다"
      follower_scores = service.follower_data['participant_degree']
      assert follower_scores.min() >= 0 and follower_scores.max() <= 100, "팔로워 점수 범위가 올바르지 않습니다"
      print(f"✅ 팔로워 타겟 생성 성공 - 평균 점수: {follower_scores.mean():.2f}")

    # 연결 해제
    service.db_manager.disconnect()

    return True

  except Exception as e:
    print(f"❌ 타겟 생성 테스트 실패: {e}")
    return False

def test_model_training():
  """모델 훈련 테스트"""
  print("\n=== 모델 훈련 테스트 시작 ===")

  try:
    service = GaugeService()
    service.setup_database_connection()

    # 데이터 로딩, 피처 생성, 타겟 생성
    service.load_and_merge_data()
    service.generate_features()
    service.generate_targets()

    # 모델 훈련
    service.train_models()

    # 리더 모델 검증
    if not service.leader_data.empty:
      assert 'new_leader_degree' in service.leader_data.columns, "리더 예측값이 생성되지 않았습니다"
      print("✅ 리더 모델 훈련 성공")

    # 팔로워 모델 검증
    if not service.follower_data.empty:
      assert 'new_participant_degree' in service.follower_data.columns, "팔로워 예측값이 생성되지 않았습니다"
      print("✅ 팔로워 모델 훈련 성공")

    # 연결 해제
    service.db_manager.disconnect()

    return True

  except Exception as e:
    print(f"❌ 모델 훈련 테스트 실패: {e}")
    return False

def test_model_evaluation():
  """모델 평가 테스트"""
  print("\n=== 모델 평가 테스트 시작 ===")

  try:
    service = GaugeService()
    service.setup_database_connection()

    # 전체 파이프라인 실행 (평가 단계까지)
    service.load_and_merge_data()
    service.generate_features()
    service.generate_targets()
    service.train_models()
    service.evaluate_models()

    # 평가 결과 검증
    assert 'leader_evaluation' in service.results or 'follower_evaluation' in service.results, "평가 결과가 생성되지 않았습니다"

    if 'leader_evaluation' in service.results:
      leader_metrics = service.results['leader_evaluation']['metrics']
      assert 'mae' in leader_metrics, "리더 MAE 메트릭이 없습니다"
      assert 'r2' in leader_metrics, "리더 R² 메트릭이 없습니다"
      print(f"✅ 리더 모델 평가 성공 - MAE: {leader_metrics['mae']:.4f}, R²: {leader_metrics['r2']:.4f}")

    if 'follower_evaluation' in service.results:
      follower_metrics = service.results['follower_evaluation']['metrics']
      assert 'mae' in follower_metrics, "팔로워 MAE 메트릭이 없습니다"
      assert 'r2' in follower_metrics, "팔로워 R² 메트릭이 없습니다"
      print(f"✅ 팔로워 모델 평가 성공 - MAE: {follower_metrics['mae']:.4f}, R²: {follower_metrics['r2']:.4f}")

    # 연결 해제
    service.db_manager.disconnect()

    return True

  except Exception as e:
    print(f"❌ 모델 평가 테스트 실패: {e}")
    return False

def test_database_update():
  """데이터베이스 업데이트 테스트"""
  print("\n=== 데이터베이스 업데이트 테스트 시작 ===")

  try:
    service = GaugeService()
    service.setup_database_connection()

    # 전체 파이프라인 실행
    service.load_and_merge_data()
    service.generate_features()
    service.generate_targets()
    service.train_models()
    service.evaluate_models()

    # 업데이트 데이터 준비
    update_data = service.prepare_update_data()

    assert update_data is not None, "업데이트 데이터 준비에 실패했습니다"

    if not update_data.empty:
      assert 'user_id' in update_data.columns, "user_id 컬럼이 없습니다"
      assert 'leader_percent' in update_data.columns or 'participant_percent' in update_data.columns, "점수 컬럼이 없습니다"

      # 실제 DB 업데이트 (테스트 환경에서는 주의)
      service.update_manner_percents_table(update_data)

      print(f"✅ 데이터베이스 업데이트 테스트 성공 - 업데이트 건수: {len(update_data)}")
    else:
      print("⚠️ 업데이트할 데이터가 없습니다")

    # 연결 해제
    service.db_manager.disconnect()

    return True

  except Exception as e:
    print(f"❌ 데이터베이스 업데이트 테스트 실패: {e}")
    return False

def test_full_pipeline():
  """전체 파이프라인 테스트"""
  print("\n=== 전체 파이프라인 테스트 시작 ===")

  try:
    service = GaugeService()

    # 전체 파이프라인 실행
    result = service.run_full_pipeline()

    assert result is not None, "파이프라인 실행 결과가 없습니다"
    assert result['success'] == True, "전체 파이프라인 실행에 실패했습니다"

    print(f"✅ 전체 파이프라인 테스트 성공")
    print(f"   - 실행 시간: {result['duration']}")
    print(f"   - 업데이트 건수: {result.get('update_count', 0)}")

    return True

  except Exception as e:
    print(f"❌ 전체 파이프라인 테스트 실패: {e}")
    return False

def test_database_connection():
  """데이터베이스 연결 테스트"""
  print("\n=== 데이터베이스 연결 테스트 시작 ===")

  try:
    db_manager = DBManager()
    db_manager.connect()

    # 간단한 쿼리 테스트
    result = db_manager.execute_query("SELECT 1 as test")
    assert result is not None, "데이터베이스 쿼리 실행에 실패했습니다"
    assert result[0]['test'] == 1, "쿼리 결과가 올바르지 않습니다"

    db_manager.disconnect()

    print("✅ 데이터베이스 연결 테스트 성공")
    return True

  except Exception as e:
    print(f"❌ 데이터베이스 연결 테스트 실패: {e}")
    return False

def test_manner_percents_table():
  """manner_percents 테이블 접근 테스트"""
  print("\n=== manner_percents 테이블 테스트 시작 ===")

  try:
    db_manager = DBManager()
    db_manager.connect()

    # 테이블 구조 확인
    result = db_manager.execute_query("DESCRIBE manner_percents")
    assert result is not None, "manner_percents 테이블에 접근할 수 없습니다"

    # 기존 데이터 확인
    count_result = db_manager.execute_query("SELECT COUNT(*) as count FROM manner_percents")
    record_count = count_result[0]['count'] if count_result else 0

    db_manager.disconnect()

    print(f"✅ manner_percents 테이블 테스트 성공 - 기존 레코드 수: {record_count}")
    return True

  except Exception as e:
    print(f"❌ manner_percents 테이블 테스트 실패: {e}")
    return False

def run_all_tests():
  """모든 테스트 실행"""
  print("🚀 GaugeService 테스트 시작")
  print(f"⏰ 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
  print("=" * 60)

  test_results = []

  # 개별 테스트 실행
  tests = [
      ("데이터베이스 연결", test_database_connection),
      ("manner_percents 테이블", test_manner_percents_table),
      ("초기화", test_initialize),
      ("데이터 로딩", test_data_loading),
      ("피처 생성", test_feature_generation),
      ("타겟 생성", test_target_generation),
      ("모델 훈련", test_model_training),
      ("모델 평가", test_model_evaluation),
      ("데이터베이스 업데이트", test_database_update),
      ("전체 파이프라인", test_full_pipeline),
  ]

  for test_name, test_func in tests:
    try:
      result = test_func()
      test_results.append((test_name, result))
    except Exception as e:
      print(f"❌ {test_name} 테스트 중 예외 발생: {e}")
      test_results.append((test_name, False))

  # 결과 요약
  print("\n" + "=" * 60)
  print("📊 테스트 결과 요약")
  print("=" * 60)

  passed = sum(1 for _, result in test_results if result)
  total = len(test_results)

  for test_name, result in test_results:
    status = "✅ PASS" if result else "❌ FAIL"
    print(f"{status} {test_name}")

  print(f"\n총 테스트: {total}개, 성공: {passed}개, 실패: {total - passed}개")
  print(f"성공률: {passed / total * 100:.1f}%")

  if passed == total:
    print("🎉 모든 테스트가 성공했습니다!")
  else:
    print("⚠️ 일부 테스트가 실패했습니다.")

  print(f"⏰ 종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
  run_all_tests()
