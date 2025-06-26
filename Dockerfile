# 경량 베이스 이미지 사용
FROM python:3.12-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 의존성 설치 및 정리
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# requirements.txt만 먼저 복사 - 캐시 최적화 
COPY requirements.txt .

# 패키지 설치 - requirements가 변경되지 않으면 캐시됨
RUN pip install --no-cache-dir -r requirements.txt

# 이후 전체 소스 코드 복사 - 변경된 코드만 캐시 무효화
COPY . .

# 환경변수 설정
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PORT=8000

# 포트 노출
EXPOSE 8000

# 컨테이너 시작 시 실행할 명령어
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
