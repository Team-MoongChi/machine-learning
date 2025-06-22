
class RecommendationHistoryManager:

    """
    사용자별 추천 히스토리 관리 클래스 
    - 사용자가 이미 추천받았던 상품을 반복해서 추천하는 것을 방지하기 위해 필요 
    """
    def __init__(self):
        # 사용자별 추천 히스토리를 저장하는 딕셔너리
        # {user_id: set(추천된 상품 ID)}
        self.history = {}