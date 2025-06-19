class RecommendationTransformer:
    @staticmethod
    def to_core_data(doc_id: str, recommendation_data: dict) -> dict:
        """S3 데이터를 OpenSearch 형식으로 변환"""
        return {
            "doc_id": doc_id,
            "user_id": str(recommendation_data["user_id"]),
            "recommended_item_ids": [str(item["item_id"]) for item in recommendation_data.get("recommendations", [])],
            "experiment_id": str(recommendation_data["experiment_id"]),
            "run_id": str(recommendation_data["run_id"])
        }
    
    @staticmethod
    def to_backend_format(core_data: dict) -> dict:
        """OpenSearch 데이터를 백엔드 형식으로 변환"""
        return {
            "user_id": int(core_data["user_id"]),
            "recommended_item_ids": [
                int(item["item_id"]) for item in core_data.get("recommendations", [])
            ],
            "experiment_id": int(core_data["experiment_id"]),
            "run_id": core_data["run_id"]
        }