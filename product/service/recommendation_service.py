import datetime
from typing import Dict, Any, List
import pandas as pd

from product.processor.data_processor import DataProcessor
from product.processor.category_processor import CategoryProcessor
from product.processor.product_score_processor import ProductSingleScoreProcessor
from product.feature.user_profile import UserProfiler
from product.service.recommendation_saver import RecommendationSaver

class RecommendationService:
    """
    데이터 준비, 임베딩, 인덱스, 추천 엔진, 추천 결과 저장까지
    전체 파이프라인 담당 클래스
    """
    def __init__(self, s3_key: str, bucket: str = "team6-mlops-bucket"):
        self.bucket=bucket
        self.s3_key=s3_key
        self.dp=DataProcessor()
        self.scored_df=None
        self.user_profiles = None
        self.product_embeddings = None
        self.user_embedding = None
        self.faiss_manager = None
        self.embedding_generator = None
        self.engine = None
        self.repository = None
    
    def category_score_pipeline(self) -> pd.DataFrame:
        """
        원본 상품 데이터와 카테고리 정보를 결합하고,
        1인 가구 적합도 점수까지 포함된 상품 데이터프레임을 생성
        """
        self.dp.load_db_data()
        categories_with_text = CategoryProcessor.make_category_text(self.dp.categories)
        joined_df = ProductSingleScoreProcessor.join(self.dp.products, categories_with_text)
        scored_df = ProductSingleScoreProcessor.calc_score(joined_df)
        self.scored_df = scored_df
        return scored_df

    def user_profile_pipeline(self, scored_df: pd.DataFrame) -> dict:
        """
        사용자 로그 및 상품 데이터를 활용해 사용자별 프로필을 생성
        """
        self.dp.load_db_data()
        self.dp.load_log_data()
        profiler = UserProfiler(
            products=scored_df,
            search_logs=self.dp.search_logs,
            click_logs=self.dp.click_logs,
            favorite_products=self.dp.favorite_products
        )
        user_profiles = profiler.create_user_profiles(self.dp.users)
        self.user_profiles = user_profiles
        return user_profiles