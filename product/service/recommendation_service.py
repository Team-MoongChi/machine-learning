import datetime
from typing import Dict, Any, List
import pandas as pd

from product.processor.data_processor import DataProcessor
from product.processor.category_processor import CategoryProcessor
from product.processor.product_score_processor import ProductSingleScoreProcessor
from product.service.recommendation_saver import RecommendationSaver

class RecommendationService:
    """
    데이터 준비, 임베딩, 인덱스, 추천 엔진, 추천 결과 저장까지
    전체 파이프라인 담당 클래스
    """
    def __init__(self, s3_key: str, bucket: str = "team6-mlops-bucket"):
        self.bucket=bucket
        self.s3_key=s3_key
        self.scored_df=None
        self.user_profiles = None
        self.product_embeddings = None
        self.user_embedding = None
        self.faiss_manager = None
        self.embedding_generator = None
        self.engine = None
        self.repository = None


