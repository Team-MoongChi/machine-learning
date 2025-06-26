import datetime
from typing import Dict, Any, List
import pandas as pd

from config.opensearch_mappings import PRODUCT_MAPPING
from product.processor.data_processor import DataProcessor
from product.processor.category_processor import CategoryProcessor
from product.processor.product_score_processor import ProductSingleScoreProcessor
from product.feature.user_profile import UserProfiler
from product.embedding.embedding_generator import EmbeddingGenerator
from product.embedding.faiss_manager import FAISSIndexManager
from product.core.recommendation_engine import RecommendationEngine
from product.service.recommendation_saver import RecommendationSaver
from product.repository.recommendation_repository import RecommendationRepository

class RecommendationService:
    """
    데이터 준비, 임베딩, 인덱스, 추천 엔진, 추천 결과 저장까지
    전체 파이프라인 담당 클래스
    """
    def __init__(self, bucket: str = "team6-mlops-bucket"):
        self.bucket=bucket
        self.dp=DataProcessor()
        self.scored_df=None
        self.user_profiles = None
        self.product_embeddings = None
        self.user_embedding = None
        self.faiss_manager = None
        self.embedding_generator = None
        self.engine = None
        self.repository = RecommendationRepository(
            s3_bucket="team6-mlops-bucket",
            opensearch_index="recommendations-v2",
            mapping=PRODUCT_MAPPING
        )
    
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

    def user_profile_pipeline(self, scored_df: pd.DataFrame) -> Dict:
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
    
    def embedding_pipeline(self, scored_df: pd.DataFrame, user_profile: Dict):
        """
        상품 임베딩 및 단일 사용자 임베딩 벡터를 생성
        """
        embedding_generator = EmbeddingGenerator()
        product_embeddings, _ = embedding_generator.generate_product_embeddings(scored_df)
        user_embedding, _ = embedding_generator.generate_user_embedding(user_profile)
        self.embedding_generator = embedding_generator
        self.product_embeddings = product_embeddings
        self.user_embedding = user_embedding
    
    def faiss_pipeline(self, product_embeddings, user_embedding, local_path='faiss.index'):
        """
        FAISS 인덱스를 구축하고, S3와 로컬에 저장 및 복구를 수행
        """
        today_str = datetime.datetime.now().strftime("%Y-%m-%d")
        bucket = "team6-mlops-bucket"
        s3_key = f"faiss_index/{today_str}_index/faiss.index"

        faiss_manager = FAISSIndexManager()
        faiss_manager.build_index(product_embeddings)
        faiss_manager.save_index_to_local(local_path)
        faiss_manager.load_index_from_local(local_path)
        if bucket and s3_key:
            faiss_manager.save_index_to_S3(local_path, bucket, s3_key)
            faiss_manager.load_index_from_s3(local_path, bucket, s3_key)
        faiss_manager.auto_load_index(local_path, bucket, s3_key)
        faiss_manager.search(user_embedding, k=4)
        self.faiss_manager = faiss_manager


    def recommendation_engine_pipeline(self, scored_df, user_profiles, faiss_manager, embedding_generator):
        """
        추천 엔진
        """
        engine = RecommendationEngine(
            products_df=scored_df,
            faiss_manager=faiss_manager,
            embedding_generator=embedding_generator,
            user_profiles=user_profiles
        )
        self.engine = engine
    
    def save_all_user_recommendations(self, user_profiles, engine, repository, top_k=4):
        """
        모든 사용자에 대해 추천을 생성하고, S3/Opensearch에 저장
        """
        for user_id in user_profiles.keys():
            RecommendationSaver.recommend_for_existing_user(
                user_id=user_id,
                engine=engine,
                repository=repository,
                top_k=top_k
            )
    
    def run_full_pipeline(self):
        """
        전체 파이프라인
        """
        scored_df = self.category_score_pipeline()
        user_profiles = self.user_profile_pipeline(scored_df)
        self.embedding_pipeline(scored_df, user_profiles)
        self.faiss_pipeline(
            self.product_embeddings, 
            self.user_embedding,
            local_path='faiss.index'
        )
        # 추천 엔진 준비
        self.recommendation_engine_pipeline(
            scored_df,
            user_profiles,
            self.faiss_manager,
            self.embedding_generator
        )
        # 추천 결과 저장소 준비 및 전체 사용자 추천 결과 저장
        self.save_all_user_recommendations(
            user_profiles=user_profiles,
            engine=self.engine,
            repository=self.repository,
            top_k=4
        )
    