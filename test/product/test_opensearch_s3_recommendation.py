import logging
from datetime import datetime, timedelta
from product.repository.recommendation_repository import RecommendationRepository
from utils.storage.s3_manager import S3Manager
from utils.storage.opensearch_manager import OpenSearchManager

import logging
from datetime import datetime, timedelta
from utils.storage.s3_manager import S3Manager
from utils.storage.opensearch_manager import OpenSearchManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_recommendations():
    """S3 데이터를 OpenSearch로 마이그레이션"""
    
    # 초기화
    s3 = S3Manager(bucket="team6-mlops-bucket")
    opensearch = OpenSearchManager(index="recommendations")
    
    try:
        # S3 기본 경로에서 모든 user 디렉토리 검색
        base_prefix = "recommendations/user_"
        all_files = s3.list_objects(prefix=base_prefix)
        
        if not all_files:
            logger.warning(f"No files found in base path: {base_prefix}")
            return
            
        # 어제 날짜 형식으로 필터링
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
        s3_files = [
            file for file in all_files 
            if f"product_{yesterday}" in file
        ]
        
        if not s3_files:
            logger.warning(f"No files found for date: {yesterday}")
            return
            
        logger.info(f"Found {len(s3_files)} files to process for {yesterday}")
        
        # OpenSearch 인덱스 초기화
        opensearch.delete_index()
        
        # 각 파일 처리
        success_count = 0
        for s3_key in s3_files:
            try:
                # S3에서 데이터 읽기
                data = s3.download(s3_key)
                
                # user_id 추출
                user_id = s3_key.split('/')[1].replace('user_', '')
                doc_id = f"user_{user_id}"
                
                # OpenSearch에 저장
                opensearch.upload(doc_id=doc_id, data=data)
                success_count += 1
                
                logger.info(f"Successfully processed {s3_key}")
                
            except Exception as e:
                logger.error(f"Error processing file {s3_key}: {str(e)}")
                continue
        
        logger.info(f"Migration completed: {success_count}/{len(s3_files)} files processed")
        
        # 결과 검증
        test_file = s3_files[0]
        test_user_id = test_file.split('/')[1].replace('user_', '')
        test_doc_id = f"user_{test_user_id}"
        
        # S3 원본 데이터와 OpenSearch 저장 데이터 비교
        s3_data = s3.download(test_file)
        opensearch_data = opensearch.get(test_doc_id)
        
        if opensearch_data:
            logger.info("Data verification successful!")
        else:
            logger.error("Data verification failed!")
            
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        raise

if __name__ == "__main__":
    migrate_recommendations()