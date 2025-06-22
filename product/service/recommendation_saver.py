from typing import List, Dict, Any
import pandas as pd
import datetime
import logging

from product.repository.recommendation_repository import RecommendationRepository

logger = logging.getLogger(__name__)

class RecommendationSaver:
    """
    추천 결과를 S3와 OpenSearch에 저장
    """

    def recommend_for_new_user(
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
        # 신규 사용자 임베딩 벡터 생성
        user_embedding, query_text = embedding_generator.generate_user_embedding(new_user_info)

        # FAISS 인덱스에서 유사 상품 Top-K 검색
        scores, indices = faiss_manager.search(user_embedding, k=top_k)
        recommended_products = products_df.iloc[indices].copy()
        recommended_products['faiss_score'] = scores

        # 추천 결과 dict로 변환
        rec_result = recommended_products.to_dict(orient='records')

        # doc_id 생성
        today = datetime.datetime.now().strftime("%Y%m%d")
        doc_id = f"{new_user_info.get('gender','unknown')}_{new_user_info.get('birth','unknown')}_{today}"

        # S3와 opensearch에 저장
        repository.save_to_s3(doc_id, rec_result)
        repository.save_to_opensearch(doc_id, rec_result)
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

        # doc_id 생성
        today = datetime.datetime.now().strftime("%Y%m%d")
        doc_id = f"{user_id}_{today}"

        # S3와 opensearch에 저장
        repository.save_to_s3(str(user_id), rec_result)
        repository.save_to_opensearch(doc_id, rec_result)
        print(f"기존 사용자 {user_id} 추천 결과 S3/Opensearch 저장 완료")

        return rec_result