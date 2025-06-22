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
    