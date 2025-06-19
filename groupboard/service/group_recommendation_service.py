import logging
from typing import Dict
from groupboard.processor.data_processor import DataProcessor
from groupboard.core.recommendation_engine import RecommendationEngine
from groupboard.transformer.response_transformer import ResponseTransformer
from config.group_board_config import ANALYSIS_DAYS, TOP_N_GROUPS
from datetime import datetime, timedelta
from utils.storage.s3_manager import S3Manager
from utils.storage.opensearch_manager import OpenSearchManager

class GroupRecommendationService:
    """공구방 추천 서비스 메인 클래스"""
    
    def __init__(self, data_path: str, s3_bucket: str, opensearch_index: str):
        self.data_processor = DataProcessor(data_path)
        self.recommendation_engine = None
        self.response_formatter = ResponseTransformer()
        

        # 저장소 매니저 초기화
        self.s3_manager = S3Manager(s3_bucket)
        self.opensearch = OpenSearchManager(opensearch_index)
        
    def initialize(self) -> bool:
        """데이터 로드 및 서비스 초기화"""
        if not self.data_processor.load_data():
            logging.error("데이터 로드 실패")
            return False
        self.recommendation_engine = RecommendationEngine(self.data_processor)
        logging.info("공구방 추천 서비스 초기화 완료")
        return True
            