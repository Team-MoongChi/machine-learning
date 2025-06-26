import pandas as pd
import numpy as np
from datetime import datetime
from dotenv import load_dotenv

from gauge.core.data_loader import DataLoader
from gauge.managers.db_manager import DBManager
from gauge.generators.features.leader_feature_generator import LeaderFeatureGenerator
from gauge.generators.features.follower_feature_generator import FollowerFeatureGenerator
from gauge.generators.targets.leader_target_generator import LeaderTargetGenerator
from gauge.generators.targets.follower_target_generator import FollowerTargetGenerator
from gauge.processors.trainings.leader_training_processor import LeaderTrainingProcessor
from gauge.processors.trainings.follower_training_processor import FollowerTrainingProcessor
from gauge.processors.evaluates.leader_evaluate_processor import LeaderEvaluateProcessor
from gauge.processors.evaluates.follower_evaluate_processor import FollowerEvaluateProcessor

# 환경 변수 로드
load_dotenv()

class GaugeService:
  """
  전체 게이지 생성 파이프라인을 관리하는 메인 서비스 클래스
  """

  def __init__(self):
    """GaugeService 초기화"""
    self.db_manager = None
    self.data_loader = None
    self.merged_all = None
    self.leader_data = None
    self.follower_data = None
    self.results = {}

  def setup_database_connection(self):
    """데이터베이스 연결 설정"""
    try:
      self.db_manager = DBManager()
      self.db_manager.connect()
      self.data_loader = DataLoader(self.db_manager)
      print("✅ 데이터베이스 연결 성공")
    except Exception as e:
      print(f"❌ 데이터베이스 연결 실패: {e}")
      raise

  def load_and_merge_data(self):
    """1단계: DB에서 데이터 로드 및 조인"""
    print("\n" + "=" * 60)
    print("📊 1단계: 데이터 로드 및 조인 시작")
    print("=" * 60)

    try:
      # 전체 데이터셋 생성
      self.merged_all = self.data_loader.create_complete_dataset()

      if self.merged_all.empty:
        raise ValueError("조인된 데이터가 비어있습니다.")

      print(f"✅ 데이터 로드 및 조인 완료: {self.merged_all.shape}")
      return self.merged_all

    except Exception as e:
      print(f"❌ 데이터 로드 및 조인 실패: {e}")
      raise

  def generate_features(self):
    """2단계: 피처 생성"""
    print("\n" + "=" * 60)
    print("🔧 2단계: 피처 생성 시작")
    print("=" * 60)

    try:
      # 리더 데이터 피처 생성
      leader_raw_data = self.merged_all[self.merged_all['role'] == 'LEADER'].copy()
      if not leader_raw_data.empty:
        leader_feature_gen = LeaderFeatureGenerator(leader_raw_data)
        self.leader_data = leader_feature_gen.generate_leader_features()
        print(f"✅ 리더 피처 생성 완료: {self.leader_data.shape}")
      else:
        print("⚠️ 리더 데이터가 없습니다.")
        self.leader_data = pd.DataFrame()

      # 팔로워 데이터 피처 생성
      follower_raw_data = self.merged_all[self.merged_all['role'] == 'MEMBER'].copy()
      if not follower_raw_data.empty:
        follower_feature_gen = FollowerFeatureGenerator(follower_raw_data)
        self.follower_data = follower_feature_gen.generate_follower_features()
        print(f"✅ 팔로워 피처 생성 완료: {self.follower_data.shape}")
      else:
        print("⚠️ 팔로워 데이터가 없습니다.")
        self.follower_data = pd.DataFrame()

    except Exception as e:
      print(f"❌ 피처 생성 실패: {e}")
      raise

  def generate_targets(self):
    """3단계: 타겟 생성"""
    print("\n" + "=" * 60)
    print("🎯 3단계: 타겟 생성 시작")
    print("=" * 60)

    try:
      # 리더 타겟 생성
      if not self.leader_data.empty:
        leader_target_gen = LeaderTargetGenerator(self.leader_data)
        self.leader_data = leader_target_gen.generate_leader_targets()
        print("✅ 리더 타겟 생성 완료")

      # 팔로워 타겟 생성
      if not self.follower_data.empty:
        follower_target_gen = FollowerTargetGenerator(self.follower_data)
        self.follower_data = follower_target_gen.generate_follower_targets()
        print("✅ 팔로워 타겟 생성 완료")

    except Exception as e:
      print(f"❌ 타겟 생성 실패: {e}")
      raise

  def train_models(self):
    """4단계: 모델 훈련"""
    print("\n" + "=" * 60)
    print("🤖 4단계: 모델 훈련 시작")
    print("=" * 60)

    try:
      # 리더 모델 훈련
      if not self.leader_data.empty:
        leader_trainer = LeaderTrainingProcessor(self.leader_data)
        self.leader_data = leader_trainer.train_leader_model()
        self.results['leader_feature_importance'] = leader_trainer.get_leader_feature_importance()
        print("✅ 리더 모델 훈련 완료")

      # 팔로워 모델 훈련
      if not self.follower_data.empty:
        follower_trainer = FollowerTrainingProcessor(self.follower_data)
        self.follower_data = follower_trainer.train_follower_model()
        self.results['follower_feature_importance'] = follower_trainer.get_follower_feature_importance()
        print("✅ 팔로워 모델 훈련 완료")

    except Exception as e:
      print(f"❌ 모델 훈련 실패: {e}")
      raise

  def evaluate_models(self):
    """5단계: 모델 평가"""
    print("\n" + "=" * 60)
    print("📈 5단계: 모델 평가 시작")
    print("=" * 60)

    try:
      # 리더 모델 평가
      if not self.leader_data.empty:
        leader_evaluator = LeaderEvaluateProcessor(self.leader_data)
        self.results['leader_evaluation'] = leader_evaluator.evaluate_leader_model()
        print("✅ 리더 모델 평가 완료")

      # 팔로워 모델 평가
      if not self.follower_data.empty:
        follower_evaluator = FollowerEvaluateProcessor(self.follower_data)
        self.results['follower_evaluation'] = follower_evaluator.evaluate_follower_model()
        print("✅ 팔로워 모델 평가 완료")

    except Exception as e:
      print(f"❌ 모델 평가 실패: {e}")
      raise

  def prepare_update_data(self):
    """6단계: DB 업데이트용 데이터 준비"""
    print("\n" + "=" * 60)
    print("📝 6단계: DB 업데이트 데이터 준비")
    print("=" * 60)

    try:
        # user_id를 기준으로 리더/팔로워 점수를 통합
      update_data = {}

      # 리더 데이터 처리
      if not self.leader_data.empty and 'new_leader_degree' in self.leader_data.columns:
        for _, row in self.leader_data.iterrows():
          user_id = int(row['user_id'])
          if user_id not in update_data:
            update_data[user_id] = {'leader_percent': None, 'participant_percent': None}
          update_data[user_id]['leader_percent'] = round(float(row['new_leader_degree']), 1)
        print(f"✅ 리더 업데이트 데이터 준비: {len(self.leader_data)}건")

      # 팔로워 데이터 처리
      if not self.follower_data.empty and 'new_participant_degree' in self.follower_data.columns:
        for _, row in self.follower_data.iterrows():
          user_id = int(row['user_id'])
          if user_id not in update_data:
            update_data[user_id] = {'leader_percent': None, 'participant_percent': None}
          update_data[user_id]['participant_percent'] = round(float(row['new_participant_degree']), 1)
        print(f"✅ 팔로워 업데이트 데이터 준비: {len(self.follower_data)}건")

      if update_data:
          # DataFrame으로 변환
        final_update_data = pd.DataFrame([
            {
                'user_id': user_id,
                'leader_percent': data['leader_percent'],
                'participant_percent': data['participant_percent']
            }
            for user_id, data in update_data.items()
        ])
        print(f"✅ 전체 업데이트 데이터 준비 완료: {len(final_update_data)}건")
        return final_update_data
      else:
        print("⚠️ 업데이트할 데이터가 없습니다.")
        return pd.DataFrame()

    except Exception as e:
      print(f"❌ 업데이트 데이터 준비 실패: {e}")
      raise

  def update_manner_percents_table(self, update_data):
    """7단계: manner_percents 테이블 업데이트"""
    print("\n" + "=" * 60)
    print("💾 7단계: manner_percents 테이블 업데이트")
    print("=" * 60)

    if update_data.empty:
      print("⚠️ 업데이트할 데이터가 없습니다.")
      return

    try:
      success_count = 0
      error_count = 0

      for idx, row in update_data.iterrows():
        try:
          user_id = int(row['user_id'])
          leader_percent = row['leader_percent'] if pd.notnull(row['leader_percent']) else None
          participant_percent = row['participant_percent'] if pd.notnull(row['participant_percent']) else None

          # 기존 레코드 확인
          check_sql = "SELECT manner_percent_id, leader_percent, participant_percent FROM manner_percents WHERE user_id = %s"
          existing_record = self.db_manager.execute_query(check_sql, (user_id,))

          if existing_record:
            # 기존 레코드가 있으면 UPDATE
            existing = existing_record[0]

            # 기존 값과 새 값을 병합 (NULL이 아닌 값 우선)
            final_leader_percent = leader_percent if leader_percent is not None else existing.get('leader_percent')
            final_participant_percent = participant_percent if participant_percent is not None else existing.get('participant_percent')

            update_sql = """
              UPDATE manner_percents 
              SET leader_percent = %s, participant_percent = %s
              WHERE user_id = %s
            """

            args = (final_leader_percent, final_participant_percent, user_id)
            result = self.db_manager.execute_update(update_sql, args)

          else:
            # 새 레코드 INSERT (role 컬럼 제거)
            insert_sql = """
              INSERT INTO manner_percents (user_id, leader_percent, participant_percent)
              VALUES (%s, %s, %s)
            """

            args = (user_id, leader_percent, participant_percent)
            result = self.db_manager.execute_update(insert_sql, args)

          if result is not None:
            success_count += 1
            print(f"✅ 업데이트 성공: user_id={user_id}, leader={leader_percent}, participant={participant_percent}")
          else:
            error_count += 1
            print(f"⚠️ 업데이트 실패: user_id={user_id}")

        except Exception as e:
          error_count += 1
          print(f"❌ 개별 업데이트 오류: user_id={row['user_id']}, error={e}")

      print(f"✅ DB 업데이트 완료: 성공 {success_count}건, 실패 {error_count}건")

      if error_count > 0:
        print(f"⚠️ {error_count}건의 업데이트가 실패했습니다.")

    except Exception as e:
      print(f"❌ DB 업데이트 실패: {e}")
      raise

  def run_full_pipeline(self):
    """전체 파이프라인 실행"""
    start_time = datetime.now()
    print("🚀 게이지 생성 파이프라인 시작")
    print(f"⏰ 시작 시간: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    try:
      # 1. 데이터베이스 연결
      self.setup_database_connection()

      # 2. 데이터 로드 및 조인
      self.load_and_merge_data()

      # 3. 피처 생성
      self.generate_features()

      # 4. 타겟 생성
      self.generate_targets()

      # 5. 모델 훈련
      self.train_models()

      # 6. 모델 평가
      self.evaluate_models()

      # 7. DB 업데이트 데이터 준비
      update_data = self.prepare_update_data()

      # 8. DB 업데이트
      self.update_manner_percents_table(update_data)

      end_time = datetime.now()
      duration = end_time - start_time

      print("\n" + "=" * 60)
      print("🎉 게이지 생성 파이프라인 완료!")
      print(f"⏰ 종료 시간: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
      print(f"⏱️ 총 소요 시간: {duration}")
      print("=" * 60)

      return {
          'success': True,
          'duration': duration,
          'results': self.results,
          'update_count': len(update_data) if not update_data.empty else 0
      }

    except Exception as e:
      end_time = datetime.now()
      duration = end_time - start_time

      print("\n" + "=" * 60)
      print("💥 게이지 생성 파이프라인 실패!")
      print(f"❌ 오류: {e}")
      print(f"⏱️ 실행 시간: {duration}")
      print("=" * 60)

      return {
          'success': False,
          'error': str(e),
          'duration': duration
      }

    finally:
      # 데이터베이스 연결 해제
      if self.db_manager:
        self.db_manager.disconnect()

  def get_pipeline_summary(self):
    """파이프라인 실행 결과 요약"""
    if not self.results:
      print("파이프라인이 아직 실행되지 않았습니다.")
      return

    print("\n📊 파이프라인 실행 결과 요약")
    print("=" * 50)

    # 리더 결과
    if 'leader_evaluation' in self.results:
      leader_metrics = self.results['leader_evaluation']['metrics']
      print(f"🔵 리더 모델 성능:")
      print(f"   - MAE: {leader_metrics['mae']:.4f}")
      print(f"   - RMSE: {leader_metrics['rmse']:.4f}")
      print(f"   - R²: {leader_metrics['r2']:.4f}")

    # 팔로워 결과
    if 'follower_evaluation' in self.results:
      follower_metrics = self.results['follower_evaluation']['metrics']
      print(f"🟢 팔로워 모델 성능:")
      print(f"   - MAE: {follower_metrics['mae']:.4f}")
      print(f"   - RMSE: {follower_metrics['rmse']:.4f}")
      print(f"   - R²: {follower_metrics['r2']:.4f}")
