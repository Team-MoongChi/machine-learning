from typing import Dict, List, Any
from datetime import datetime, timedelta

from config.opensearch_mappings import PRODUCT_MAPPING
from product.processor.data_processor import DataProcessor
from product.processor.category_processor import CategoryProcessor
from product.processor.product_score_processor import ProductSingleScoreProcessor
from product.embedding.embedding_generator import EmbeddingGenerator
from product.embedding.faiss_manager import FAISSIndexManager
from product.repository.recommendation_repository import RecommendationRepository
from product.service.recommendation_saver import RecommendationSaver

class NewUserRecommendationService:
    def __init__(self):
        
        self.dp = DataProcessor()
        if not self.dp.load_db_data():
            raise RuntimeError("DB 데이터 로드 실패")
        categories_with_text = CategoryProcessor.make_category_text(self.dp.categories)
        joined_df = ProductSingleScoreProcessor.join(self.dp.products, categories_with_text)
        self.scored_df = ProductSingleScoreProcessor.calc_score(joined_df)

        # 임베딩 및 FAISS 인덱스 준비
        self.embedding_generator = EmbeddingGenerator()
        # 상품 임베딩은 여기서 새로 만들지 않음!
        self.faiss_manager = FAISSIndexManager()

        yesterday_str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    

        self.faiss_manager.auto_load_index(
            local_path='faiss.index',
            bucket="team6-mlops-bucket",
            s3_key=f"faiss_index/{yesterday_str}_index/faiss.index"
        )

        # 저장소 및 saver 준비
        self.repository = RecommendationRepository(
            s3_bucket="team6-mlops-bucket",
            opensearch_index="recommendations",
            mapping=PRODUCT_MAPPING
        )
        self.saver = RecommendationSaver()
    
    def recommend(self, new_user_info: Dict[str, Any], top_k: int = 4) -> List[Dict[str, Any]]:
        """
        신규 사용자 추천 생성 및 저장
        """
        return self.saver.recommend_for_new_user(
            new_user_info,
            self.scored_df,
            self.faiss_manager,
            self.embedding_generator,
            self.repository,
            top_k
        )
    