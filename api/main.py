from fastapi import FastAPI
from api.routers import recommendation
from api.routers import group_board
from api.routers import new_user
import logging
from fastapi.middleware.cors import CORSMiddleware

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title="ML API Service",
    description="API for serving ML predictions including recommendations and leaders",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  #
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

# groupboard 라우터 추가
app.include_router(
    new_user,
    prefix="/api/v1",
    tags=["new_user"]
)


@app.get("/health")
async def health_check():
    """서비스 헬스 체크"""
    return {"status": "healthy", "service": "ml-api"}