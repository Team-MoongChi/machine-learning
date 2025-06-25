GROUP_RECOMMENDATION_MAPPING = {
    "mappings": {
        "properties": {
            "doc_id": {"type": "keyword"},
            "user_id": {"type": "keyword"},
            "user_district": {"type": "keyword"},
            "analysis_period": {"type": "keyword"},
            "total_local_groups": {"type": "integer"},
            "returned_groups": {"type": "integer"},
            "latest_favorite": {"type": "date"},
            "popular_groups": {
                "type": "nested",
                "properties": {
                    "group_id": {"type": "keyword"},
                    "title": {"type": "text"},
                    "location": {"type": "text"},
                    "recent_favorites": {"type": "integer"},
                    "latest_favorite": {"type": "date"}
                }
            }
        }
    }
}

PRODUCT_MAPPING = {
    "mappings": {
        "properties": {
            "doc_id": {"type": "keyword"},
            "user_id": {"type": "keyword"},
            "recommended_item_ids": {
                "type": "nested",
                "properties": {
                    "item_id": {"type": "keyword"},
                    "score": {"type": "float"}
                }
            },
            "experiment_id": {"type": "keyword"},
            "run_id": {"type": "keyword"}
        }
    }
}

