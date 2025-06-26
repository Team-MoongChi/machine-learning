from gauge.generators.targets.base_target_generator import BaseTargetGenerator
import pandas as pd
import numpy as np

class FollowerTargetGenerator(BaseTargetGenerator):
  """
  팔로워(참가자) 역할에 특화된 타겟 생성 클래스
  """

  def __init__(self, df):
    super().__init__(df)
    self.target_column = "participant_degree"

  def rule_based_participant_score(self, row):
    """
    팔로워 점수 계산 함수

    Args:
        row: 데이터프레임의 행

    Returns:
        int: 0-100 범위의 팔로워 점수
    """
    # 기본 점수 계산 (별점, 감정점수, 키워드)
    score = self.calculate_base_score(row)

    # 4. 팔로워 완료율: 최대 +10점
    if pd.notnull(row["participant_completed_rate"]):
      score += row["participant_completed_rate"] * 10

    # 점수 범위 제한
    return self.limit_score_range(score)

  def get_follower_agg_dict(self):
    """팔로워 전용 집계 딕셔너리 반환"""
    agg_dict = self.get_common_agg_dict()
    agg_dict.update({
        "participant_completed_rate": self.mean_or_nan,
        "participant_role_count": "max",
        "participant_completed_count": "max",
    })
    return agg_dict

  def generate_follower_targets(self):
    """
    팔로워 타겟 변수 생성

    Returns:
        pd.DataFrame: 팔로워 점수가 포함된 user_level 데이터프레임
    """
    print("=== 팔로워 타겟 생성 시작 ===")

    # 1. user_id 기준으로 집계
    print("1. user_id 기준 집계 수행...")
    agg_dict = self.get_follower_agg_dict()
    user_level_df = self.aggregate_user_level(agg_dict)

    # 2. 팔로워 점수 계산
    print("2. 팔로워 점수 계산...")
    user_level_df[self.target_column] = user_level_df.apply(
        self.rule_based_participant_score, axis=1
    )

    # 3. 결과 저장
    self.df = user_level_df

    print("=== 팔로워 타겟 생성 완료 ===")
    print(f"생성된 사용자 수: {len(user_level_df)}")

    # 타겟 요약 정보 출력
    self.print_target_summary(self.target_column)

    return user_level_df

  def get_follower_statistics(self):
    """팔로워 통계 정보 반환"""
    if self.target_column not in self.df.columns:
      print("팔로워 타겟이 생성되지 않았습니다. generate_follower_targets()를 먼저 실행하세요.")
      return None

    stats = {
        'count': self.df[self.target_column].count(),
        'mean': self.df[self.target_column].mean(),
        'std': self.df[self.target_column].std(),
        'min': self.df[self.target_column].min(),
        'max': self.df[self.target_column].max(),
        'high_score_count': (self.df[self.target_column] >= 80).sum(),
        'low_score_count': (self.df[self.target_column] <= 30).sum()
    }

    return stats
