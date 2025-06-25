# 경량 베이스 이미지 사용
FROM python:3.12-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 의존성 최소화 및 시간대(tzdata) 및 locale 설정
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    tzdata && \
    ln -snf /usr/share/zoneinfo/Asia/Seoul /etc/localtime && \
    echo "Asia/Seoul" > /etc/timezone && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 필요 패키지 복사 및 설치
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY . .

# 환경변수 설정
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PORT=8000 \
    TZ=Asia/Seoul

# 포트 노출
EXPOSE 8000

# 실행 명령어
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
