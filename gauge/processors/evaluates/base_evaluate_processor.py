import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
# import matplotlib.pyplot as plt
# import seaborn as sns

class BaseEvaluateProcessor:
  """
  모델 평가를 위한 기본 클래스
  공통 평가 기능들을 제공하며, 역할별 특화 클래스에서 상속받아 사용
  """

  def __init__(self, user_level_df, target_column, prediction_column):
    """
    Args:
        user_level_df: 예측 결과가 포함된 데이터프레임
        target_column: 실제 값 컬럼명
        prediction_column: 예측 값 컬럼명
    """
    self.user_level_df = user_level_df.copy()
    self.target_column = target_column
    self.prediction_column = prediction_column
    self.y_true = user_level_df[target_column]
    self.y_pred = user_level_df[prediction_column]

  def calculate_metrics(self):
    """
    기본 회귀 메트릭 계산

    Returns:
        dict: 메트릭 딕셔너리
    """
    metrics = {
        'mae': mean_absolute_error(self.y_true, self.y_pred),
        'rmse': np.sqrt(mean_squared_error(self.y_true, self.y_pred)),
        'r2': r2_score(self.y_true, self.y_pred),
        'mape': np.mean(np.abs((self.y_true - self.y_pred) / self.y_true)) * 100
    }

    return metrics

  def print_evaluation_results(self, model_name="GradientBoostingRegressor"):
    """
    평가 결과 출력

    Args:
        model_name: 모델명
    """
    metrics = self.calculate_metrics()

    print(f"[{model_name} 모델 성능 평가]")
    print(f"MAE  (평균 절대 오차): {metrics['mae']:.4f}")
    print(f"RMSE (평균 제곱근 오차): {metrics['rmse']:.4f}")
    print(f"R²   (설명력): {metrics['r2']:.4f}")
    print(f"MAPE (평균 절대 백분율 오차): {metrics['mape']:.2f}%")

    return metrics

  # def plot_predictions(self, figsize=(12, 5)):
  #   """
  #   예측 결과 시각화

  #   Args:
  #       figsize: 그래프 크기
  #   """
  #   fig, axes = plt.subplots(1, 2, figsize=figsize)

  #   # 실제값 vs 예측값 산점도
  #   axes[0].scatter(self.y_true, self.y_pred, alpha=0.6)
  #   axes[0].plot([self.y_true.min(), self.y_true.max()], [self.y_true.min(), self.y_true.max()], 'r--', lw=2)
  #   axes[0].set_xlabel('실제값')
  #   axes[0].set_ylabel('예측값')
  #   axes[0].set_title('실제값 vs 예측값')

  #   # 잔차 히스토그램
  #   residuals = self.y_true - self.y_pred
  #   axes[1].hist(residuals, bins=30, alpha=0.7)
  #   axes[1].set_xlabel('잔차 (실제값 - 예측값)')
  #   axes[1].set_ylabel('빈도')
  #   axes[1].set_title('잔차 분포')
  #   axes[1].axvline(x=0, color='r', linestyle='--')

  #   plt.tight_layout()
  #   plt.show()

  def analyze_prediction_distribution(self):
    """예측값 분포 분석"""
    print("=== 예측값 분포 분석 ===")
    print(f"실제값 범위: {self.y_true.min():.2f} ~ {self.y_true.max():.2f}")
    print(f"예측값 범위: {self.y_pred.min():.2f} ~ {self.y_pred.max():.2f}")
    print(f"실제값 평균: {self.y_true.mean():.2f}")
    print(f"예측값 평균: {self.y_pred.mean():.2f}")
    print(f"실제값 표준편차: {self.y_true.std():.2f}")
    print(f"예측값 표준편차: {self.y_pred.std():.2f}")

  def get_prediction_errors(self, threshold=None):
    """
    예측 오차가 큰 케이스 분석

    Args:
        threshold: 오차 임계값 (None이면 상위 10% 사용)

    Returns:
        pd.DataFrame: 오차가 큰 케이스들
    """
    errors = np.abs(self.y_true - self.y_pred)

    if threshold is None:
      threshold = np.percentile(errors, 90)

    high_error_mask = errors > threshold
    high_error_cases = self.user_level_df[high_error_mask].copy()
    high_error_cases['prediction_error'] = errors[high_error_mask]

    print(f"오차 임계값: {threshold:.2f}")
    print(f"높은 오차 케이스 수: {len(high_error_cases)}")

    return high_error_cases.sort_values('prediction_error', ascending=False)
