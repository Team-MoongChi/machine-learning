import pandas as pd
import numpy as np

class BaseTargetGenerator:
  """
  타겟 생성을 위한 기본 클래스
  공통 기능들을 제공하며, 리더/팔로워 특화 클래스에서 상속받아 사용
  """

  def __init__(self, df):
    """
    Args:
        df: 피처가 생성된 데이터프레임
    """
    self.df = df.copy()

  @staticmethod
  def mean_or_nan(series):
    """평균값 계산, 빈 시리즈면 NaN 반환"""
    return series.mean() if not series.empty else np.nan

  @staticmethod
  def mode_or_nan(series):
    """최빈값 계산, 빈 시리즈면 NaN 반환"""
    mode_vals = series.mode()
    return mode_vals.iloc[0] if not mode_vals.empty else np.nan

  def aggregate_user_level(self, agg_dict):
    """
    user_id 기준으로 집계 수행

    Args:
        agg_dict: 집계할 컬럼과 함수 딕셔너리

    Returns:
        pd.DataFrame: 집계된 user_level 데이터프레임
    """
    user_level_df = self.df.groupby("user_id").agg(agg_dict).reset_index()
    return user_level_df

  def clip_score(self, score, lower=-2, upper=2):
    """점수를 지정된 범위로 클리핑"""
    return max(min(score, upper), lower)

  def limit_score_range(self, score, lower=0, upper=100):
    """최종 점수를 0-100 범위로 제한하고 정수로 반환"""
    return int(round(min(max(score, lower), upper)))

  def calculate_base_score(self, row):
    """
    공통 점수 계산 로직

    Args:
        row: 데이터프레임의 행

    Returns:
        float: 기본 점수 (완료율 제외)
    """
    score = 50  # 기본값

    # 1. 별점: ±20점
    if pd.notnull(row["star"]):
      score += (row["star"] - 3.0) / 2.0 * 20

    # 2. 감정 점수: ±15점 (정규분포 기반, clip ±2σ)
    if pd.notnull(row["review_score_normalized"]):
      clipped = self.clip_score(row["review_score_normalized"])
      score += clipped * 7.5

    # 3. 키워드 수: 최대 +15점 (현재 데이터 기준 max=3)
    if pd.notnull(row["positive_keyword_count"]):
      if row["positive_keyword_count"] == 0:
        score -= 5
      else:
        score += (row["positive_keyword_count"] / 3) * 15

    return score

  def get_common_agg_dict(self):
    """공통 집계 딕셔너리 반환"""
    return {
        "star": self.mean_or_nan,
        "positive_keyword_count": "max",
        "review_score_normalized": self.mean_or_nan,
        "k_친절해": "max",
        "k_약속_시간을_지켰어": "max",
        "k_채팅_응답이_빨라": "max",
        "k_설명과_같아": "max",
        "k_믿을_수_있어": "max",
        "k_가격∙수량이_확실해": "max",
        "k_또_거래하고_싶어": "max",
    }

  def get_dataframe(self):
    """처리된 데이터프레임 반환"""
    return self.df

  def print_target_summary(self, target_col):
    """타겟 변수 요약 정보 출력"""
    if target_col in self.df.columns:
      print(f"=== {target_col} 요약 정보 ===")
      print(f"개수: {self.df[target_col].count()}")
      print(f"평균: {self.df[target_col].mean():.2f}")
      print(f"표준편차: {self.df[target_col].std():.2f}")
      print(f"최솟값: {self.df[target_col].min()}")
      print(f"최댓값: {self.df[target_col].max()}")
      print(f"분위수:")
      print(self.df[target_col].describe())
    else:
      print(f"{target_col} 컬럼이 존재하지 않습니다.")
