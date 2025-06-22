import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple
from sklearn.preprocessing import normalize

class EmbeddingGenerator:
    """
    SBERT 모델을 활용해 상품/사용자 텍스트를 벡터로 변환하는 클래스 
    """

    def __init__(self, model_name: str = 'jhgan/ko-sroberta-multitask'):
        """
        SBERT 모델 로딩
        """
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name)
        except Exception as e:
            print(f"모델 로딩 실패({e}), 다국어 모델로 대체합니다.")
            self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    
    def generate_product_embeddings(self, products_df : pd.DataFrame) -> Tuple[np.ndarry, List[str]]:
        """
        상품명 + 카테고리 텍스트로 임베딩 생성 
        
        Args:
            카테고리 전처리, 1인 가구 점수 계산 전처리 완료된 df

        Returns:
            임베딩 배열과 임베딩에 사용된 텍스트 리스트
        """

        # 상품명과 카테고리 텍스트를 합쳐서 임베딩용 텍스트 리스트 생성
        product_texts = [
            f"{row['name']} {row.get('category_text', '')}".strip()
            for _, row in products_df.iterrows()
        ]
        
        # SBERT로 각 텍스트를 임베딩 벡터로 변환
        embeddings = self.model.encode(product_texts, show_progress_bar=True, batch_size=32)
        
        # 임베딩 벡터 L2 정규화 
        embeddings = normalize(embeddings, norm='l2', axis=1)
        return embeddings, product_texts
    
    def build_query_text(self, user_profile: Dict) -> str:
        """
        사용자 프로필 정보를 바탕으로 임베딩용 쿼리 텍스트 생성
        """
        query_parts = []

        # 1. 기본 관심사(카테고리) 추가
        if user_profile.get('base_interest_category'):
            query_parts.append(user_profile['base_interest_category'])

        # 2. 나이대별 키워드 추가
        age_group = user_profile.get('age_group', '30대')
        if age_group == '20대':
            query_parts += ['혼밥', '간편식', '트렌디', '가성비', '편리']
        elif age_group == '30대':
            query_parts += ['건강', '품질', '프리미엄', '편의성', '실용']
        else:
            query_parts += ['건강관리', '웰빙', '신뢰성', '안전', '고품질']

        # 3. 성별별 키워드 추가
        gender = user_profile.get('gender', 'M')
        if gender == 'F':
            query_parts += ['뷰티', '홈케어', '건강관리', '세심함']
        else:
            query_parts += ['간편', '실용', '기능성', '효율']

        # 4. 사용자 타입별 행동 데이터 활용
        if user_profile.get('user_type') == 'new':
            query_parts += ['1인 가구', '혼밥', '간편']
        else:
            query_parts += user_profile.get('search_keywords', [])[:3]
            query_parts += user_profile.get('favorite_categories', [])[:2]
            query_parts += user_profile.get('clicked_categories', [])[:2]

        # 5. 1인 가구 공통 키워드 추가
        query_parts += ['소포장', '미니', '1인용']

        return ' '.join(query_parts)