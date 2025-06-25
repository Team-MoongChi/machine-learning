from gauge.processors.evaluates.base_evaluate_processor import BaseEvaluateProcessor

class LeaderEvaluateProcessor(BaseEvaluateProcessor):
  """
  리더 역할에 특화된 모델 평가 클래스
  """

  def __init__(self, user_level_df):
    super().__init__(
        user_level_df=user_level_df,
        target_column="leader_degree",
        prediction_column="new_leader_degree"
    )

  def evaluate_leader_model(self):
    """
    리더 모델 종합 평가

    Returns:
        dict: 평가 메트릭
    """
    print("=== 리더 모델 평가 시작 ===")

    # 1. 기본 메트릭 계산 및 출력
    metrics = self.print_evaluation_results("리더 GradientBoostingRegressor")

    # 2. 예측값 분포 분석
    self.analyze_prediction_distribution()

    # 3. 시각화
    # self.plot_predictions()

    # 4. 높은 오차 케이스 분석
    high_error_cases = self.get_prediction_errors()

    print("=== 리더 모델 평가 완료 ===")

    return {
        'metrics': metrics,
        'high_error_cases': high_error_cases
    }

  def analyze_leader_score_distribution(self):
    """리더 점수 분포 특화 분석"""
    print("=== 리더 점수 분포 분석 ===")

    # 점수 구간별 분석
    score_ranges = [(0, 30), (30, 50), (50, 70), (70, 85), (85, 100)]

    for low, high in score_ranges:
      actual_count = ((self.y_true >= low) & (self.y_true < high)).sum()
      pred_count = ((self.y_pred >= low) & (self.y_pred < high)).sum()
      print(f"{low}-{high}점: 실제 {actual_count}명, 예측 {pred_count}명")
