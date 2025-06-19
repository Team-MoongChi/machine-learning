from fastapi import FastAPI
from api.routers import recommendation
from api.routers import group_board
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title="ML API Service",
    description="API for serving ML predictions including recommendations and leaders",
    version="1.0.0"
)

# 라우터 등록
app.include_router(
    recommendation,
    prefix="/api/v1",
    tags=["recommendations"]
)

# groupboard 라우터 추가
app.include_router(
    group_board,
    prefix="/api/v1",
    tags=["group_boards"]
)

@app.get("/health")
async def health_check():
    """서비스 헬스 체크"""
    return {"status": "healthy", "service": "ml-api"}