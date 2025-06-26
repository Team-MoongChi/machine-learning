import pandas as pd

class DataLoader:
  """
  DBManager를 사용하여 데이터를 조회하고 분석하는 서비스 클래스
  """

  def __init__(self, db_manager):
    """
    Args:
        db_manager: DBManager 인스턴스
    """
    self.db_manager = db_manager

  def get_all_tables_as_dataframes(self):
    """모든 테이블을 DataFrame으로 반환"""
    try:
      # 각 테이블 조회
      users_data = self.db_manager.execute_query("SELECT * FROM users")
      group_boards_data = self.db_manager.execute_query("SELECT * FROM group_boards")
      participants_data = self.db_manager.execute_query("SELECT * FROM participants")
      reviews_data = self.db_manager.execute_query("SELECT * FROM reviews")

      # DataFrame으로 변환
      dataframes = {
          'users': pd.DataFrame(users_data) if users_data else pd.DataFrame(),
          'group_boards': pd.DataFrame(group_boards_data) if group_boards_data else pd.DataFrame(),
          'participants': pd.DataFrame(participants_data) if participants_data else pd.DataFrame(),
          'reviews': pd.DataFrame(reviews_data) if reviews_data else pd.DataFrame()
      }

      return dataframes

    except Exception as e:
      print(f"Error loading tables: {e}")
      return None

  def get_table_dataframe(self, table_name):
    """특정 테이블을 DataFrame으로 반환"""
    try:
      data = self.db_manager.execute_query(f"SELECT * FROM {table_name}")
      return pd.DataFrame(data) if data else pd.DataFrame()
    except Exception as e:
      print(f"Error loading table {table_name}: {e}")
      return pd.DataFrame()

  def get_users_dataframe(self):
    """Users 테이블을 DataFrame으로 반환"""
    return self.get_table_dataframe('users')

  def get_group_boards_dataframe(self):
    """Group_boards 테이블을 DataFrame으로 반환"""
    return self.get_table_dataframe('group_boards')

  def get_participants_dataframe(self):
    """Participants 테이블을 DataFrame으로 반환"""
    return self.get_table_dataframe('participants')

  def get_reviews_dataframe(self):
    """Reviews 테이블을 DataFrame으로 반환"""
    return self.get_table_dataframe('reviews')

  def get_custom_query_dataframe(self, sql, args=None):
    """커스텀 쿼리 결과를 DataFrame으로 반환"""
    try:
      data = self.db_manager.execute_query(sql, args)
      return pd.DataFrame(data) if data else pd.DataFrame()
    except Exception as e:
      print(f"Error executing custom query: {e}")
      return pd.DataFrame()

  def merge_user_group_data(self, users_df, group_boards_df):
    """사용자와 그룹보드 데이터를 조인하는 함수"""
    try:
      # 필요한 컬럼만 추출
      users_sel = users_df[["user_id", "interest_category"]]
      group_boards_sel = group_boards_df[[
          "user_id", "group_product_id", "status", "group_board_id", "total_users"
      ]]

      # user_id 기준으로 조인
      user_group_merged = pd.merge(users_sel, group_boards_sel, on="user_id", how="left")

      print(f"User-Group 조인 완료: {user_group_merged.shape}")
      return user_group_merged

    except Exception as e:
      print(f"Error merging user and group  {e}")
      return pd.DataFrame()

  def merge_participant_review_data(self, participants_df, reviews_df):
    """참가자와 리뷰 데이터를 조인하는 함수"""
    try:
      # 필요한 컬럼 추출
      participants_sel = participants_df[["participant_id", "role", "group_board_id"]]
      reviews_sel = reviews_df[["participant_id", "keywords", "review", "star"]]

      # participant_id 기준으로 조인
      participant_review_merged = pd.merge(
          participants_sel,
          reviews_sel,
          on="participant_id",
          how="left"
      )

      print(f"Participant-Review 조인 완료: {participant_review_merged.shape}")
      return participant_review_merged

    except Exception as e:
      print(f"Error merging participant and review  {e}")
      return pd.DataFrame()

  def merge_all_data(self, user_group_df, participant_review_df):
    """모든 데이터를 최종 조인하는 함수"""
    try:
      # group_board_id 기준으로 조인
      merged_all = pd.merge(
          user_group_df,
          participant_review_df,
          on="group_board_id",
          how="left"
      )

      # 중복 제거
      merged_all = merged_all.drop_duplicates(subset=["user_id", "group_board_id", "role"])

      print(f"전체 데이터 조인 완료: {merged_all.shape}")
      return merged_all

    except Exception as e:
      print(f"Error merging all  {e}")
      return pd.DataFrame()

  def create_complete_dataset(self):
    """모든 테이블을 조인하여 완전한 데이터셋을 생성하는 함수"""
    try:
      # 모든 테이블 데이터 가져오기
      print("=== 데이터 로딩 시작 ===")
      users_df = self.get_users_dataframe()
      group_boards_df = self.get_group_boards_dataframe()
      participants_df = self.get_participants_dataframe()
      reviews_df = self.get_reviews_dataframe()

      print(f"Users: {users_df.shape}")
      print(f"Group Boards: {group_boards_df.shape}")
      print(f"Participants: {participants_df.shape}")
      print(f"Reviews: {reviews_df.shape}")

      # 단계별 조인
      print("\n=== 데이터 조인 시작 ===")

      # 1단계: 사용자-그룹보드 조인
      user_group_merged = self.merge_user_group_data(users_df, group_boards_df)

      # 2단계: 참가자-리뷰 조인
      participant_review_merged = self.merge_participant_review_data(participants_df, reviews_df)

      # 3단계: 전체 조인
      final_dataset = self.merge_all_data(user_group_merged, participant_review_merged)

      print(f"\n=== 최종 데이터셋 완성: {final_dataset.shape} ===")
      return final_dataset

    except Exception as e:
      print(f"Error creating complete dataset: {e}")
      return pd.DataFrame()
