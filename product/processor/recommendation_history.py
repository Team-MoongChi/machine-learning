import pandas as pd

class RecommendationHistoryManager:

    """
    사용자별 추천 히스토리 관리 클래스 
    - 사용자가 이미 추천받았던 상품을 반복해서 추천하는 것을 방지하기 위해 필요 
    """
    def __init__(self):
        # 사용자별 추천 히스토리를 저장하는 딕셔너리
        # {user_id: set(추천된 상품 ID)}
        self.history = {}
    
    def update(self, user_id: int, recommendations_df: pd.DataFrame):
        """
        추천 히스토리 업데이트 및 크기 제한

        Args:
            user_id: 추천을 받은 사용자 ID
            recommendations_df: 새로 추천된 상품들의 DataFrame
        """
        # 해당 사용자의 히스토리가 없으면 빈 set으로 초기화
        if user_id not in self.history:
            self.history[user_id] = set()
        
        # 새로 추천된 상품 ID들을 히스토리에 추가
        new_product_ids = set(recommendations_df['product_id'].tolist())
        self.history[user_id].update(new_product_ids)

        # 히스토리의 크기가 15개를 초과하면, 최근 8개만 남기고 나머지는 삭제
        if len(self.history[user_id]) > 15:
            history_list = list(self.history[user_id])
            self.history[user_id] = set(history_list[-8:])
