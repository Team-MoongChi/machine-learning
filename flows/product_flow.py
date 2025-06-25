from prefect import flow, task
from typing import Optional, Dict, List
from datetime import datetime
from product.service.recommendation_service import RecommendationService
import logging

S3_BUCKET = "team6-mlops-bucket"
OPENSEARCH_INDEX = "recommendations"

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@flow(name="product_flow")
def prodcut_flow():
    logger.info("🚀 Starting product recommendation flow...")

    try:
        service = RecommendationService()
        logger.info("✅ RecommendationService initialized.")
        
        service.run_full_pipeline()
        logger.info("🎉 Product recommendation pipeline completed successfully.")
    except Exception as e:
        logger.error(f"❌ Product flow failed: {e}", exc_info=True)
        raise