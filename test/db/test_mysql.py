from utils.storage.mysql_manager import MySQLManager
from config.mysql_config import MYSQL_CONFIG

# 인스턴스 생성
db = MySQLManager(MYSQL_CONFIG=MYSQL_CONFIG)

# 연결 테스트 
try:
    df = db.execute_query("SELECT 1 as test_col;")
    print("연결 성공! 결과:")
    print(df)
except Exception as e:
    print("연결 실패:", e)

# 실제 테이블 조회 테스트
try:
    df = db.read_table('users')  
    print("테이블 조회 성공! 일부 데이터:")
    print(df.head())
except Exception as e:
    print("테이블 조회 실패:", e)

if __name__ == "__main__":
    print("MySQL 테스트 스크립트 실행 완료")