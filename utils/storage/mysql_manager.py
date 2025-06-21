import pymysql
import pandas as pd
from config.mysql_config import MYSQL_CONFIG

class MySQLManager:
    # init에 연결 정보
    def __init__(self):
        self.config = MYSQL_CONFIG
    
    def get_connection(self):
        """
        MySQL 데이터베이스에 연결을 생성하고 반환
        """
        return pymysql.connect(
            host=self.config['url'],
            port=self.config['port'],
            user=self.config['username'],
            password=self.config['password'],
            db=self.config['database'],
            charset=self.config['charset'],
            autocommit=True,
            cursorclass=pymysql.cursors.DictCursor
        )

    def execute_query(self, query: str) -> pd.DataFrame:
        """SELECT 쿼리 결과를 DataFrame으로 반환"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                return pd.DataFrame(result)
        finally:
            conn.close()

    def read_table(self, table_name):
        """테이블 전체를 DataFrame으로 반환"""
        conn = self.get_connection()
        query = f"SELECT * FROM {table_name}"
        try:
            with conn.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                return pd.DataFrame(result)
        finally:
            conn.close()

        return self.execute_query(query)