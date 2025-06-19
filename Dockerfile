# Base Image
FROM python:3.12          

# 컨테이너 내부 작업 디렉토리 설정
WORKDIR /app                  

# 시스템 의존성 설치
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \       
    curl \                  
    && rm -rf /var/lib/apt/lists/*  

# P패키지 설치
COPY requirements.txt .       
RUN pip install --no-cache-dir -r requirements.txt  

# 애플리케이션 파일 복사
COPY api/ api/ 
COPY config/ config/    
COPY recommendation/ recommendation/ 
COPY groupboard/ groupboard/
COPY utils/ utils/

# python 모듈 경로 설정, API 서버 포트 설정 
ENV PYTHONPATH=/app         
ENV PORT=8000              

# 컨테이너 외부로 8000 포트 노출 
EXPOSE 8000                 

# 실행 명령어
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]