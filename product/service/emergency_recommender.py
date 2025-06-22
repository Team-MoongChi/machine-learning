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

        # 사용되지 않았고, 가격이 1,000~25,000원인 상품만 필터링
        available = self.products_df[
            (~self.products_df['id'].isin(used_product_ids)) &
            (self.products_df['price'] <= 25000) &
            (self.products_df['price'] >= 1000)
        ]

        # 만약 적정 가격대 상품이 없다면, 전체에서 일부만 선택 
        if available.empty:
            available = self.products_df[
                ~self.products_df['id'].isin(used_product_ids)
            ].head(count * 2)

        # 사용자별 고정 시드로 랜덤 샘플링 
        selected = available.sample(n=min(count, len(available)), random_state=user_id)

        # 추천 결과 데이터(딕셔너리) 리스트 생성
        # - 점수, 부스팅 등은 기본값으로 고정
        emergency_recs = []
        for _, p in selected.iterrows():
            rec_data = {
                'product_id': p['id'],
                'name': p['name'],
                'price': p.get('price', 0),
                'category_path': p.get('category_path', ''),
                'large_category': p.get('large_category', '기타'),
                'single_household_score': 6.0,     # 기본 적합도 점수
                'base_similarity': 0.6,            # 기본 유사도
                'final_score': 0.6,                # 최종 점수(고정)
                'boost_ratio': 1.5,                # 고정 부스팅 배수
                'behavior_boost': 1.0,             # 행동 부스팅 없음
                'user_type': 'emergency_guaranteed',# 응급 추천 유형
                'recommendation_reason': '다양성 확보 | 적당한 선택',
                'premium_score': 6.0,
                'appeal_score': 6.0
            }
            emergency_recs.append(rec_data)

        return emergency_recs
        