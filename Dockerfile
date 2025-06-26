# 1단계: 의존성만 설치하는 빌더 스테이지
FROM python:3.12-slim AS builder

WORKDIR /app

# 시스템 패키지 최소화, 빌드 툴만 설치
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

# requirements.txt만 복사 (캐시 최적화)
COPY requirements.txt .

# 패키지 설치 (캐시 활용)
RUN pip install --no-cache-dir -r requirements.txt

# 2단계: 실행용 베이스 이미지
FROM python:3.12-slim

WORKDIR /app

# 빌더에서 설치한 패키지 복사 
COPY --from=builder /root/.local /root/.local

# 환경변수
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PORT=8000

# 소스코드 복사
COPY . .

# 불필요한 파일 복사 방지 (반드시 .dockerignore 사용)
# 예: .git, __pycache__, *.log 등

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]