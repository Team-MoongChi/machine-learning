from typing import Dict, List, Set

class EmergencyRecommender:
    """
    pool/Faiss 기반 추천이 모두 실패했을 때, 
    적정 가격대의 상품 중에서 랜덤으로 추천을 보장하는 클래스
    """
    def __init__(self, products_df):
        self.products_df = products_df

    def recommend(self, count: int, used_product_ids: set, user_id: int) -> list[dict]:
        """
        Args:
            count: 추천할 상품 개수
            used_product_ids: 이미 추천된 상품 ID 집합
            user_id: 사용자 ID - 랜덤 시드 고정용

        Returns:
            list of dict: 추천 후보 상품의 딕셔너리 리스트 - 중복 추천 X
        """

        # 추천 개수가 0 이하이면 빈 리스트 반환
        if count <= 0:
            return []
        