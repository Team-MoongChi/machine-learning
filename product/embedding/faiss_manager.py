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
       
    def search(self, query_embedding: np.ndarray, k: int=50) -> Tuple[np.ndarray, np.ndarray]:
        """
        사용자 임베딩(1D 벡터)로 유사 상품 검색

        Args:
            query_embedding (np.ndarray): (D,) L2 정규화된 쿼리 임베딩
            k (int): 반환할 유사 상품 개수

        Returns:
            Tuple[np.ndarray, np.ndarray]: (유사도 점수 배열, 상품 인덱스 배열)
        """
        if self.index is None:
            raise ValueError("FAISS 인덱스가 구축되지 않았습니다.")

        query_embedding = query_embedding.reshape(1, -1).astype('float32')
        query_embedding = query_embedding / np.linalg.norm(query_embedding)

        # FAISS 인덱스에서 쿼리 벡터와 가장 유사한 k개의 벡터를 검색 
        scores, indices = self.index.search(query_embedding, k)
        return scores[0], indices[0]
    
    def save_index_to_local(self, local_path: str):
        """
        현재 인덱스를 로컬 파일로 저장
        """
        if self.index is None:
            raise ValueError("저장할 인덱스가 없습니다.")
        faiss.write_index(self.index, local_path)
    
    def load_index_from_local(self, local_path: str):
        """
        로컬 파일에서 인덱스를 로드
        """
        if not os.path.exists(local_path):
            raise FileNotFoundError(f"인덱스 파일이 존재하지 않습니다:{local_path}")
        self.index = faiss.read_index(local_path)
    
    def save_index_to_S3(self, local_path: str, bucket: str, s3_key: str):
        """
        로컬 인덱스 파일을 S3에 업로드
        """
        s3 = boto3.client('s3')
        s3.upload_file(local_path, bucket, s3_key)
    
    def load_index_from_s3(self, local_path: str, bucket: str, s3_key: str):
        """
        S3에서 인덱스 파일을 다운로드 후 로컬에 저장 및 인덱스 로드
        """
        s3 = boto3.client('s3')
        s3.download_file(bucket, s3_key, local_path)
        self.index = faiss.read_index(local_path)
    
    def auto_load_index(self, local_path: str, bucket: str, s3_key: str):
        """
        로컬에 인덱스 파일이 있으면 로컬에서, 없으면 S3에서 다운로드 후 로드
        """
        if os.path.exists(local_path):
            print(f"로컬 인덱스 파일에서 로드: {local_path}")
            self.load_index_from_local(local_path)
        else:
            print(f"S3에서 인덱스 파일 다운로드 후 로드: s3://{bucket}/{s3_key}")
            self.load_index_from_s3(local_path, bucket, s3_key)