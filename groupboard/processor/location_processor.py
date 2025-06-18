import pandas as pd
import re
from typing import Optional

class LocationProcessor:
    """지역 정보 처리 담당 클래스"""
    
    @staticmethod
    def extract_district(address: str) -> Optional[str]:
        """주소에서 구 정보 추출"""
        if pd.isna(address) or not isinstance(address, str):
            return None
        
        district_match = re.search(r'([가-힣]+구)', address)
        return district_match.group(1) if district_match else None
    
    @staticmethod
    def add_district_info(data: pd.DataFrame) -> pd.DataFrame:
        """데이터에 구 정보 컬럼 추가"""
        data_copy = data.copy()
        data_copy['user_district'] = data_copy['address'].apply(
            LocationProcessor.extract_district
        )
        data_copy['group_district'] = data_copy['location'].apply(
            LocationProcessor.extract_district
        )
        return data_copy
