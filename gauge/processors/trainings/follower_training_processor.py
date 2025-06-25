from gauge.processors.trainings.base_training_processor import BaseTrainingProcessor

class FollowerTrainingProcessor(BaseTrainingProcessor):
  """
  팔로워 역할에 특화된 모델 훈련 클래스
  """

  def __init__(self, user_level_df):
    super().__init__(
        user_level_df=user_level_df,
        target_column="participant_degree",
        prediction_column="new_participant_degree"
    )

  def train_follower_model(self, model_params=None, cv_params=None):
    """
    팔로워 모델 훈련 파이프라인

    Args:
        model_params: 모델 파라미터
        cv_params: 교차 검증 파라미터

    Returns:
        pd.DataFrame: 예측 결과가 포함된 데이터프레임
    """
    print("=== 팔로워 모델 훈련 시작 ===")

    # 1. 피처 및 타겟 준비
    features = self.prepare_features_and_target()

    # 2. 결측값 처리
    self.handle_missing_values(strategy='mean')

    # 3. 모델 설정
    if model_params is None:
      model_params = {'n_estimators': 100, 'random_state': 42}
    self.setup_model(model_params)

    # 4. K-Fold 교차 검증으로 훈련
    if cv_params is None:
      cv_params = {'n_splits': 5, 'shuffle': True, 'random_state': 42}
    self.train_with_kfold(**cv_params)

    # 5. 예측 결과 저장
    self.save_predictions()

    print("=== 팔로워 모델 훈련 완료 ===")

    return self.get_dataframe()

  def get_follower_feature_importance(self):
    """팔로워 모델의 피처 중요도 반환"""
    importance_df = self.get_feature_importance(top_n=15)

    if importance_df is not None:
      print("=== 팔로워 모델 피처 중요도 (Top 15) ===")
      for idx, row in importance_df.iterrows():
        print(f"{row['feature']}: {row['importance']:.4f}")

    return importance_df
