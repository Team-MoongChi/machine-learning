import os
import json
import pandas as pd
from typing import Tuple, List, Optional, Dict
from utils.storage.mysql_manager import MySQLManager

class DataProcessor:
    """데이터 로드 및 전처리 담당 클래스"""
    def __init__(self):
        self.mysql = MySQLManager()
        self.data_path = os.path.join(self.data_path, "data/user_activity_logs_final_.json")
        self.products = None
        self.categories = None
        self.users = None
        self.favorite_products = None
        self.search_logs = None
        self.click_logs = None
        
    def load_db_data(self) -> bool:
        """백엔드 MySQL에서 데이터 추출해서 반환"""
        try:
            self.products= self.mysql.read_table('products')
            self.categories = self.mysql.read_table('categories')
            self.users = self.mysql.read_table('users')
            favorite_products = self.mysql.read_table('favorite_products')
            
            # 상품 찜 데이터만 필터링 
            self.favorite_products = favorite_products[
                (favorite_products ['product_type'] == 'SHOPPING') &
                (favorite_products['product_id'].notna())
            ]
            return True
            
        except Exception as e:
            raise Exception(f"데이터 로드 실패: {e}")
    
    def load_log_data(self) -> bool:
        """
        JSON 배열 로그 파일을 
        - 검색 로그 DataFrame
        - 클릭 로그 DataFrame
        으로 저장 
        """
        # 파일 포맷 판별
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        except Exception as e:
            print(f"[ERROR] 로그 파일 읽기 실패: {e}")
            return pd.DataFrame(), pd.DataFrame()

        # 이벤트별 분리
        search_logs, click_logs = self.split_by_event(logs)

        # 정제 및 DataFrame 변환
        self.search_logs = self.clean_search_logs(search_logs)
        self.click_logs = self.clean_click_logs(click_logs)
        print(f"[INFO] 검색 로그 {len(search_df)}개, 클릭 로그 {len(click_df)}개 로드 완료")

        return True
    
    def read_jsonl(self, S3_logs) -> List[Dict]:
        """
        {\"key\":\"value\"} 형태의 이중 이스케이프 JSONL 파일을 리스트로 반환
        S3 로그 파일을 불러올 때 사용    
        """
        logs = []
        try:
            with open(S3_logs, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        # 1차 파싱(문자열)
                        tmp = json.loads(line)
                        # 2차 파싱(딕셔너리)
                        obj = json.loads(tmp)
                        logs.append(obj)
                    except Exception as e:
                        print(f"파싱 실패: {e}")
            return logs
        except Exception as e:
            print(f"JSONL 파일 읽기 실패: {e}")
            return []
    
    def read_json(self) -> List[Dict]:
        """
        Json 배열 파일을 리스트로 반환 
        학습용 로그 데이터를 불러올 때 사용
        """
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"JSON 파일 읽기 실패: {e}")
            return []
    
    def split_by_event(self, logs: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """검색/클릭 이벤트로 분리"""
        search, click = [], []  

        for log in logs:  # logs 리스트를 한 개씩 꺼내서
            msg = log.get('message', {})  # log에서 message라는 값을 꺼냄. 없으면 빈 dict

            # 만약 message가 문자열이면, json.loads로 딕셔너리로 바꿔줌
            if isinstance(msg, str):
                try:
                    msg = json.loads(msg)
                except Exception:
                    continue  # 변환 실패하면 무시하고 다음으로

            # message가 딕셔너리가 아니면 무시
            if not isinstance(msg, dict):
                continue

            # 이벤트 타입 가져오기
            ev = msg.get('event_type')

            # 검색이면 search 리스트에 추가
            if ev == 'search':
                search.append(msg)
            # 클릭이면 click 리스트에 추가
            elif ev == 'click':
                click.append(msg)

        return search, click  

    
    def clean_search_logs(self, logs: List[Dict]) -> pd.DataFrame:
        """검색 로그 데이터 정제 및 데이터프레임 변환"""
        rows = []
        for log in logs:
            try:
                user_id = int(log['user_id'])
                keyword = str(log['search_keyword']).strip()
                if not keyword:
                    continue
                rows.append({
                    'user_id': user_id,
                    'keyword': keyword,
                    'searched_at': log.get('searched_at', ''),
                    'search_result_count': int(log.get('search_result_count', 0))
                })
            except Exception:
                continue
        return pd.DataFrame(rows)

    def clean_click_logs(self, logs: List[Dict]) -> pd.DataFrame:
        """클릭 로그 데이터 정제 및 데이터프레임 변환"""
        rows = []
        for log in logs:
            try:
                user_id = int(log['user_id'])
                product_id = int(log['item_id'])
                rows.append({
                    'user_id': user_id,
                    'product_id': product_id,
                    'item_name': str(log.get('item_name', '')),
                    'clicked_at': log.get('clicked_at', ''),
                    'item_category': str(log.get('item_category', '')),
                    'item_price': int(log.get('item_price', 0))
                })
            except Exception:
                continue
        return pd.DataFrame(rows)
