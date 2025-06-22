import os
from typing import Tuple
import numpy as np
import faiss
import boto3

class FAISSIndexManager:
    """
    FAISS 내부 VectorDB를 활용해 L2 정규화된 벡터의 
    코사인 유사도 기반 고속 검색 인덱스를 생성/검색/저장/복구하는 클래스 
    """
    def __init__(self):
        self.index = None
        self.normalized_embeddings = None
    
    def build_index(self, embeddings: np.ndarray) -> faiss.IndexFlatIP:
        """
        상품 임베딩 배열을 받아 L2 정규화하고 FAISS 인덱스를 생성

        Args:
            embeddings (np.ndarray): (N, D) 임베딩 배열

        Returns:
            faiss.IndexFlatIP: FAISS 인덱스 객체
        """
        # L2 정규화 
        self.normalized_embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        dimension = embeddings.shape[1]
        
        # FAISS의 벡터 내적 기반 인덱스 생성 - 코사도 유사도 기반 검색 
        self.index = faiss.IndexFlatIP(dimension)
        
        # FAISS는 float32 타입만 지원하므로 형 변환
        self.index.add(self.normalized_embeddings.astype('float32'))
        return self.index
       
