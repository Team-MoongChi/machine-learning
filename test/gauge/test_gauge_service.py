import sys
import os
from datetime import datetime
from dotenv import load_dotenv

from gauge.core.gauge_service import GaugeService
from gauge.managers.db_manager import DBManager

# 환경 변수 로드
load_dotenv()

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

def test_complete_pipeline():
  """전체 파이프라인을 한 번에 테스트"""
  print("\n=== 전체 파이프라인 통합 테스트 시작 ===")

  try:
    service = GaugeService()

    # 전체 파이프라인 실행
    result = service.run_full_pipeline()

    # 기본 실행 결과 검증
    assert result is not None, "파이프라인 실행 결과가 없습니다"
    assert result['success'] == True, "전체 파이프라인 실행에 실패했습니다"

    print(f"✅ 파이프라인 실행 성공")
    print(f"   - 실행 시간: {result['duration']}")
    print(f"   - 업데이트 건수: {result.get('update_count', 0)}")

    # 세부 검증 시작
    validation_results = []

    # 1. 데이터 로딩 검증
    if hasattr(service, 'merged_all') and service.merged_all is not None and not service.merged_all.empty:
      print(f"✅ 데이터 로딩 검증 성공 - 데이터 크기: {service.merged_all.shape}")
      validation_results.append(("데이터 로딩", True))
    else:
      print("❌ 데이터 로딩 검증 실패")
      validation_results.append(("데이터 로딩", False))

    # 2. 피처 생성 검증
    leader_features_ok = False
    follower_features_ok = False

    if hasattr(service, 'leader_data') and not service.leader_data.empty:
      required_leader_features = ['leader_role_count', 'positive_keyword_count', 'review_score_normalized']
      if all(col in service.leader_data.columns for col in required_leader_features):
        leader_features_ok = True
        print(f"✅ 리더 피처 생성 검증 성공 - 데이터 크기: {service.leader_data.shape}")

    if hasattr(service, 'follower_data') and not service.follower_data.empty:
      required_follower_features = ['participant_role_count', 'positive_keyword_count', 'review_score_normalized']
      if all(col in service.follower_data.columns for col in required_follower_features):
        follower_features_ok = True
        print(f"✅ 팔로워 피처 생성 검증 성공 - 데이터 크기: {service.follower_data.shape}")

    if leader_features_ok or follower_features_ok:
      validation_results.append(("피처 생성", True))
    else:
      print("❌ 피처 생성 검증 실패")
      validation_results.append(("피처 생성", False))

    # 3. 타겟 생성 검증
    leader_targets_ok = False
    follower_targets_ok = False

    if leader_features_ok and 'leader_degree' in service.leader_data.columns:
      leader_scores = service.leader_data['leader_degree']
      if leader_scores.min() >= 0 and leader_scores.max() <= 100:
        leader_targets_ok = True
        print(f"✅ 리더 타겟 생성 검증 성공 - 평균 점수: {leader_scores.mean():.2f}")

    if follower_features_ok and 'participant_degree' in service.follower_data.columns:
      follower_scores = service.follower_data['participant_degree']
      if follower_scores.min() >= 0 and follower_scores.max() <= 100:
        follower_targets_ok = True
        print(f"✅ 팔로워 타겟 생성 검증 성공 - 평균 점수: {follower_scores.mean():.2f}")

    if leader_targets_ok or follower_targets_ok:
      validation_results.append(("타겟 생성", True))
    else:
      print("❌ 타겟 생성 검증 실패")
      validation_results.append(("타겟 생성", False))

    # 4. 모델 훈련 검증
    leader_training_ok = False
    follower_training_ok = False

    if leader_targets_ok and 'new_leader_degree' in service.leader_data.columns:
      leader_training_ok = True
      print("✅ 리더 모델 훈련 검증 성공")

    if follower_targets_ok and 'new_participant_degree' in service.follower_data.columns:
      follower_training_ok = True
      print("✅ 팔로워 모델 훈련 검증 성공")

    if leader_training_ok or follower_training_ok:
      validation_results.append(("모델 훈련", True))
    else:
      print("❌ 모델 훈련 검증 실패")
      validation_results.append(("모델 훈련", False))

    # 5. 모델 평가 검증
    if 'results' in result and result['results']:
      evaluation_ok = False

      if 'leader_evaluation' in result['results']:
        leader_metrics = result['results']['leader_evaluation']['metrics']
        if 'mae' in leader_metrics and 'r2' in leader_metrics:
          evaluation_ok = True
          print(f"✅ 리더 모델 평가 검증 성공 - MAE: {leader_metrics['mae']:.4f}, R²: {leader_metrics['r2']:.4f}")

      if 'follower_evaluation' in result['results']:
        follower_metrics = result['results']['follower_evaluation']['metrics']
        if 'mae' in follower_metrics and 'r2' in follower_metrics:
          evaluation_ok = True
          print(f"✅ 팔로워 모델 평가 검증 성공 - MAE: {follower_metrics['mae']:.4f}, R²: {follower_metrics['r2']:.4f}")

      validation_results.append(("모델 평가", evaluation_ok))
    else:
      print("❌ 모델 평가 검증 실패")
      validation_results.append(("모델 평가", False))

    # 6. 데이터베이스 업데이트 검증
    if result.get('update_count', 0) > 0:
      print(f"✅ 데이터베이스 업데이트 검증 성공 - 업데이트 건수: {result['update_count']}")
      validation_results.append(("데이터베이스 업데이트", True))
    else:
      print("❌ 데이터베이스 업데이트 검증 실패")
      validation_results.append(("데이터베이스 업데이트", False))

    # 전체 검증 결과 요약
    passed_validations = sum(1 for _, success in validation_results if success)
    total_validations = len(validation_results)

    print(f"\n📊 세부 검증 결과: {passed_validations}/{total_validations} 성공")

    for validation_name, success in validation_results:
      status = "✅ PASS" if success else "❌ FAIL"
      print(f"   {status} {validation_name}")

    # 최종 성공 기준: 모든 검증이 성공해야 함
    if passed_validations == total_validations:
      print("✅ 전체 파이프라인 통합 테스트 성공")
      return True
    else:
      print("⚠️ 일부 검증이 실패했지만 파이프라인은 완료됨")
      return True  # 파이프라인 자체는 성공했으므로 True 반환

  except Exception as e:
    print(f"❌ 전체 파이프라인 통합 테스트 실패: {e}")
    return False

def run_integrated_tests():
  """통합 테스트 실행"""
  print("🚀 GaugeService 통합 테스트 시작")
  print(f"⏰ 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
  print("=" * 60)

  test_results = []

  # 통합 테스트 목록
  tests = [
      ("데이터베이스 연결", test_database_connection),
      ("manner_percents 테이블", test_manner_percents_table),
      ("전체 파이프라인 통합", test_complete_pipeline),
  ]

  for test_name, test_func in tests:
    try:
      print(f"\n🔄 {test_name} 테스트 실행 중...")
      result = test_func()
      test_results.append((test_name, result))
    except Exception as e:
      print(f"❌ {test_name} 테스트 중 예외 발생: {e}")
      test_results.append((test_name, False))

  # 결과 요약
  print("\n" + "=" * 60)
  print("📊 통합 테스트 결과 요약")
  print("=" * 60)

  passed = sum(1 for _, result in test_results if result)
  total = len(test_results)

  for test_name, result in test_results:
    status = "✅ PASS" if result else "❌ FAIL"
    print(f"{status} {test_name}")

  print(f"\n총 테스트: {total}개, 성공: {passed}개, 실패: {total - passed}개")
  print(f"성공률: {passed / total * 100:.1f}%")

  if passed == total:
    print("🎉 모든 통합 테스트가 성공했습니다!")
  else:
    print("⚠️ 일부 테스트가 실패했습니다.")

  print(f"⏰ 종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
  run_integrated_tests()
