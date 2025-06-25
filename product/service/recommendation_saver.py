from typing import List, Dict, Any
import pandas as pd
import datetime
import logging

from product.repository.recommendation_repository import RecommendationRepository
from product.feature.user_profile import UserProfiler

logger = logging.getLogger(__name__)

class RecommendationSaver:
    """
    추천 결과를 S3와 OpenSearch에 저장
    """

    def recommend_for_new_user(
            self,
            new_user_info: Dict,
            products_df: pd.DataFrame,
            faiss_manager,
            embedding_generator,
            repository,  # RecommendationRepository 인스턴스
            top_k: int = 4
        ) -> List[Dict[str, Any]]:
        """
        신규 사용자 추천: 실시간 임베딩 생성 + FAISS 유사도 기반 Top-K 추천 + 저장
        """
        new_user_profile = UserProfiler.create_new_user_profile(new_user_info)

        # 신규 사용자 임베딩 벡터 생성
        user_embedding, query_text = embedding_generator.generate_user_embedding(new_user_profile)

        # FAISS 인덱스에서 유사 상품 Top-K 검색
        scores, indices = faiss_manager.search(user_embedding, k=top_k)
        recommended_products = products_df.iloc[indices].copy()
        recommended_products['faiss_score'] = scores

        # Timestamp 컬럼을 문자열로 변환
        for col in recommended_products.select_dtypes(include=["datetime", "datetime64[ns]"]).columns:
            recommended_products[col] = recommended_products[col].astype(str)
        
        # 추천 결과 dict로 변환
        rec_result = recommended_products.to_dict(orient='records')

        # doc_id, user_id, experiment_id, run_id 생성
        today = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        user_id = str(new_user_info.get('user_id', 'unknown'))
        experiment_id = 2
        run_id = f"run_id_{today}"
        doc_id = f"user_{user_id}_{today}"

        recommendation_data = {
            "user_id": user_id,
            "recommendations": rec_result,
            "experiment_id": experiment_id,
            "run_id": run_id
        }

        # S3 저장 경로 생성
        s3_key = f"recommendations/user_{user_id}/product_{today}.json"

        # S3와 OpenSearch에 저장
        repository.save_to_s3(s3_key, recommendation_data)
        repository.save_to_opensearch(doc_id, recommendation_data)
        print(f"신규 사용자 추천 결과 S3/Opensearch 저장 완료: {doc_id}")

        return rec_result

    def recommend_for_existing_user(
            user_id: int,
            engine,
            repository,  
            top_k: int = 4
        ) -> List[Dict[str, Any]]:
        """
        기존 사용자 추천: 엔진 추천 + 저장 
        """
        # 추천 엔진 실행
        recommendations = engine.recommend(user_id, top_k=top_k)
        rec_result = recommendations.to_dict(orient='records')

        # S3 키 생성
        today = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        doc_id = f"user_{user_id}_{today}"
        s3_key = f"recommendations/user_{user_id}/product_{today}.json"
        experiment_id = 2
        run_id = f"run_id_{today}"

        recommendation_data = {
            "user_id": user_id,
            "recommendations": rec_result,
            "experiment_id": experiment_id,
            "run_id": run_id
        }

        # S3와 opensearch에 저장
        repository.save_to_s3(s3_key=s3_key, recommendation_data=recommendation_data)
        repository.save_to_opensearch(doc_id, recommendation_data)
        print(f"기존 사용자 {user_id} 추천 결과 S3/Opensearch 저장 완료")
        print(f"{doc_id}")

        return rec_result