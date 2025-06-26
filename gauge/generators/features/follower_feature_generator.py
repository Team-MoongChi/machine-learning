from gauge.generators.features.base_feature_generator import BaseFeatureGenerator

class FollowerFeatureGenerator(BaseFeatureGenerator):
  """
  팔로워(참가자) 역할에 특화된 피처 생성 클래스
  """

  def __init__(self, merged_all):
    super().__init__(merged_all)
    self.role = 'MEMBER'
    self.keyword_list = [
        "친절해요", "약속 시간을 지켰어요", "채팅 응답이 빨라요",
        "설명과 같아요", "믿을 수 있어요", "가격∙수량이 확실해요", "또 거래하고 싶어요"
    ]
    self.drop_cols = [
        "interest_category", "review", "keywords", "group_board_id", "participant_id",
        "created_at", "group_product_id", "total_users"
    ]

  def generate_follower_features(self):
    """
    팔로워 역할 관련 모든 피처 생성

    Returns:
        pd.DataFrame: 피처가 생성된 데이터프레임
    """
    print("=== 팔로워 피처 생성 시작 ===")

    # 1. 팔로워 역할 관련 피처 생성
    print("1. 팔로워 역할 카운트 피처 생성...")
    self.count_unique_group_boards(self.role, 'participant_role_count')

    print("2. 팔로워 완료 카운트 피처 생성...")
    self.count_completed(self.role, 'participant_completed_count')

    print("3. 팔로워 완료율 피처 생성...")
    self.calculate_rate(self.role, 'participant_role_count', 'participant_completed_count', 'participant_completed_rate')

    # 2. 키워드 피처 생성
    print("4. 키워드 피처 생성...")
    self.add_keyword_features(self.keyword_list)

    # 3. 감성 분석 관련 피처 생성
    print("5. 감성 분석 적용...")
    self.apply_sentiment_analysis()

    print("6. 중립 보정 적용...")
    self.apply_neutral_adjustment()

    print("7. Jittering 적용...")
    self.apply_jittering()

    print("8. 정규분포 변환 적용...")
    self.apply_quantile_transform()

    # 4. 불필요한 컬럼 제거
    print("9. 불필요한 컬럼 제거...")
    self.drop_unnecessary_columns(self.drop_cols)

    print("=== 팔로워 피처 생성 완료 ===")

    # 생성된 피처 정보 출력
    follower_features = ['participant_role_count', 'participant_completed_count', 'participant_completed_rate', 'positive_keyword_count', 'review_score_normalized']
    self.print_feature_info(follower_features)

    return self.get_dataframe()

  def get_follower_summary(self):
    """팔로워 데이터 요약 정보"""
    follower_data = self.filter_role(self.role)
    if follower_data.empty:
      print("팔로워 데이터가 없습니다.")
      return

    print("=== 팔로워 데이터 요약 ===")
    print(f"총 팔로워 수: {follower_data['user_id'].nunique()}")
    print(f"총 팔로워 활동 건수: {len(follower_data)}")

    if 'participant_role_count' in follower_data.columns:
      print(f"평균 참가 경험 수: {follower_data['participant_role_count'].mean():.2f}")

    if 'participant_completed_rate' in follower_data.columns:
      print(f"평균 완료율: {follower_data['participant_completed_rate'].mean():.2f}")
