import numpy as np
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
    