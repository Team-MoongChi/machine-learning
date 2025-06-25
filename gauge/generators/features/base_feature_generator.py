import numpy as np
import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from sklearn.preprocessing import QuantileTransformer

class BaseFeatureGenerator:
  """
  피처 생성을 위한 기본 클래스
  공통 기능들을 제공하며, 리더/팔로워 특화 클래스에서 상속받아 사용
  """

  def __init__(self, merged_all):
    """
    Args:
        merged_all: 조인된 전체 데이터프레임
    """
    self.merged_all = merged_all.copy()
    self.sentiment_pipeline = None
    self.qt = QuantileTransformer(output_distribution='normal', random_state=42, n_quantiles=857)

  def filter_role(self, role):
    """특정 역할의 데이터만 필터링"""
    return self.merged_all[self.merged_all['role'] == role]

  def count_unique_group_boards(self, role, count_col_name):
    """
    특정 역할의 사용자별 고유 group_board_id 개수 계산

    Args:
        role: 역할 ('LEADER' 또는 'MEMBER')
        count_col_name: 생성할 컬럼명
    """
    role_df = self.filter_role(role)
    counts = role_df.groupby('user_id')['group_board_id'].nunique().rename(count_col_name)

    self.merged_all[count_col_name] = self.merged_all.apply(
        lambda row: counts.get(row['user_id'], np.nan) if row['role'] == role else np.nan,
        axis=1
    )

  def count_completed(self, role, count_col_name):
    """
    특정 역할의 사용자별 완료된 공구 개수 계산

    Args:
        role: 역할 ('LEADER' 또는 'MEMBER')
        count_col_name: 생성할 컬럼명
    """
    role_df = self.filter_role(role)
    completed_counts = role_df.groupby('user_id').apply(
        lambda x: (x['status'] == 'COMPLETED').sum()
    ).rename(count_col_name)

    self.merged_all[count_col_name] = self.merged_all.apply(
        lambda row: completed_counts.get(row['user_id'], np.nan) if row['role'] == role else np.nan,
        axis=1
    )

  def calculate_rate(self, role, count_col_name, completed_col_name, rate_col_name):
    """
    완료율 계산 (완료 개수 / 전체 개수)

    Args:
        role: 역할 ('LEADER' 또는 'MEMBER')
        count_col_name: 전체 개수 컬럼명
        completed_col_name: 완료 개수 컬럼명
        rate_col_name: 생성할 완료율 컬럼명
    """
    def calc_rate(row):
      if (row['role'] == role and
          pd.notnull(row[count_col_name]) and
              row[count_col_name] != 0):
        return row[completed_col_name] / row[count_col_name]
      else:
        return np.nan

    self.merged_all[rate_col_name] = self.merged_all.apply(calc_rate, axis=1)

  def add_keyword_features(self, keyword_list):
    """
    키워드 기반 피처 생성

    Args:
        keyword_list: 키워드 리스트
    """
    # 각 키워드별 이진 피처 생성
    for kw in keyword_list:
      colname = f'k_{kw.replace(" ", "_").replace(",", "").replace("요", "")}'
      self.merged_all[colname] = self.merged_all['keywords'].fillna("").apply(
          lambda x: int(kw in x)
      )

    # 긍정 키워드 총합 피처 생성
    keyword_cols = [col for col in self.merged_all.columns if col.startswith('k_')]
    self.merged_all['positive_keyword_count'] = self.merged_all[keyword_cols].sum(axis=1)

  def load_sentiment_model(self, model_name="beomi/KcELECTRA-base-v2022"):
    """감성 분석 모델 로드"""
    try:
      tokenizer = AutoTokenizer.from_pretrained(model_name)
      model = AutoModelForSequenceClassification.from_pretrained(model_name)
      self.sentiment_pipeline = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)
      print("감성 분석 모델 로드 완료")
    except Exception as e:
      print(f"모델 로드 실패: {e}")
      self.sentiment_pipeline = None

  def get_sentiment_score(self, text):
    """개별 텍스트의 감성 점수 계산"""
    try:
      if not text or pd.isna(text):
        return 0.5

      result = self.sentiment_pipeline(str(text)[:512])[0]
      return result['score'] if result['label'] == 'LABEL_1' else -result['score']
    except Exception:
      return 0.5

  def apply_sentiment_analysis(self):
    """전체 리뷰에 감성 분석 적용"""
    if self.sentiment_pipeline is None:
      self.load_sentiment_model()

    if self.sentiment_pipeline is None:
      print("감성 분석 모델을 로드할 수 없습니다. 기본값으로 설정합니다.")
      self.merged_all['review_score'] = 0.5
      return

    self.merged_all['review'] = self.merged_all['review'].fillna("")
    self.merged_all['review_score'] = self.merged_all['review'].apply(self.get_sentiment_score)
    print("감성 분석 완료")

  def adjust_neutral_score(self, score):
    """중립 점수 보정"""
    if 0.40 <= score <= 0.60:
      shift = (score - 0.5) * 0.8
      adjusted = score + shift
      return min(max(adjusted, 0), 1)
    return score

  def apply_neutral_adjustment(self):
    """중립 보정 적용"""
    self.merged_all['review_score_adjusted'] = self.merged_all['review_score'].apply(
        self.adjust_neutral_score
    )

  def apply_jitter(self, score):
    """점수 흔들기 (jittering)"""
    return score + np.random.normal(0, 0.002)

  def apply_jittering(self):
    """전체 점수에 jittering 적용"""
    self.merged_all['review_score_jittered'] = self.merged_all['review_score_adjusted'].apply(
        self.apply_jitter
    )

  def apply_quantile_transform(self):
    """정규분포 변환 적용"""
    self.merged_all['review_score_normalized'] = self.qt.fit_transform(
        self.merged_all[['review_score_jittered']]
    )

  def drop_unnecessary_columns(self, drop_cols):
    """불필요한 컬럼 제거"""
    self.merged_all = self.merged_all.drop(columns=drop_cols, errors='ignore')

  def get_dataframe(self):
    """처리된 데이터프레임 반환"""
    return self.merged_all

  def print_feature_info(self, feature_cols):
    """피처 정보 출력"""
    print("=== 생성된 피처 정보 ===")
    for col in feature_cols:
      if col in self.merged_all.columns:
        print(f"{col}: {self.merged_all[col].describe()}")
