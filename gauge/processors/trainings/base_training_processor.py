import numpy as np
import pandas as pd
from sklearn.model_selection import KFold
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

class BaseTrainingProcessor:
  """
  모델 훈련을 위한 기본 클래스
  공통 훈련 기능들을 제공하며, 역할별 특화 클래스에서 상속받아 사용
  """

  def __init__(self, user_level_df, target_column, prediction_column):
    """
    Args:
        user_level_df: 사용자 레벨 데이터프레임
        target_column: 타겟 컬럼명
        prediction_column: 예측 결과 저장할 컬럼명
    """
    self.user_level_df = user_level_df.copy()
    self.target_column = target_column
    self.prediction_column = prediction_column
    self.model = None
    self.X = None
    self.y = None
    self.y_preds = None

  def prepare_features_and_target(self, exclude_columns=None):
    """
    피처와 타겟 데이터 준비

    Args:
        exclude_columns: 제외할 컬럼 리스트 (기본적으로 user_id와 타겟 컬럼들 제외)
    """
    if exclude_columns is None:
      exclude_columns = ["user_id", self.target_column, self.prediction_column]

    # 피처 선택
    features = [col for col in self.user_level_df.columns if col not in exclude_columns]

    self.X = self.user_level_df[features]
    self.y = self.user_level_df[self.target_column]

    print(f"선택된 피처 수: {len(features)}")
    print(f"피처 목록: {features}")

    return features

  def handle_missing_values(self, strategy='mean'):
    """
    결측값 처리

    Args:
        strategy: 결측값 처리 전략 ('mean', 'median', 'mode', 'drop')
    """
    if strategy == 'mean':
      self.X = self.X.fillna(self.X.mean())
    elif strategy == 'median':
      self.X = self.X.fillna(self.X.median())
    elif strategy == 'drop':
      # 결측값이 있는 행 제거
      mask = ~(self.X.isnull().any(axis=1) | self.y.isnull())
      self.X = self.X[mask]
      self.y = self.y[mask]

    print(f"결측값 처리 완료 (전략: {strategy})")
    print(f"최종 데이터 크기: {self.X.shape}")

  def setup_model(self, model_params=None):
    """
    모델 설정

    Args:
        model_params: 모델 파라미터 딕셔너리
    """
    if model_params is None:
      model_params = {'n_estimators': 100, 'random_state': 42}

    self.model = GradientBoostingRegressor(**model_params)
    print(f"모델 설정 완료: {self.model}")

  def train_with_kfold(self, n_splits=5, shuffle=True, random_state=42):
    """
    K-Fold 교차 검증을 사용한 모델 훈련

    Args:
        n_splits: 폴드 수
        shuffle: 데이터 셔플 여부
        random_state: 랜덤 시드
    """
    print(f"=== K-Fold 교차 검증 시작 (n_splits={n_splits}) ===")

    kf = KFold(n_splits=n_splits, shuffle=shuffle, random_state=random_state)
    self.y_preds = np.zeros(len(self.X))

    fold_scores = []

    for fold, (train_idx, val_idx) in enumerate(kf.split(self.X), 1):
      print(f"Fold {fold} 훈련 중...")

      X_train, X_val = self.X.iloc[train_idx], self.X.iloc[val_idx]
      y_train, y_val = self.y.iloc[train_idx], self.y.iloc[val_idx]

      # 모델 훈련
      self.model.fit(X_train, y_train)

      # 검증 세트 예측
      val_preds = self.model.predict(X_val)
      self.y_preds[val_idx] = val_preds

      # 폴드별 성능 계산
      fold_mae = mean_absolute_error(y_val, val_preds)
      fold_scores.append(fold_mae)
      print(f"Fold {fold} MAE: {fold_mae:.4f}")

    print(f"평균 MAE: {np.mean(fold_scores):.4f} (±{np.std(fold_scores):.4f})")
    print("K-Fold 교차 검증 완료")

  def save_predictions(self):
    """예측 결과를 데이터프레임에 저장"""
    self.user_level_df[self.prediction_column] = self.y_preds
    print(f"예측 결과가 '{self.prediction_column}' 컬럼에 저장되었습니다.")

  def get_feature_importance(self, top_n=10):
    """
    피처 중요도 반환

    Args:
        top_n: 상위 n개 피처만 반환

    Returns:
        pd.DataFrame: 피처 중요도 데이터프레임
    """
    if self.model is None:
      print("모델이 훈련되지 않았습니다.")
      return None

    feature_names = self.X.columns
    importances = self.model.feature_importances_

    feature_importance_df = pd.DataFrame({
        'feature': feature_names,
        'importance': importances
    }).sort_values('importance', ascending=False)

    return feature_importance_df.head(top_n)

  def get_dataframe(self):
    """처리된 데이터프레임 반환"""
    return self.user_level_df
