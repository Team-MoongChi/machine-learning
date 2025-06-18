# 분석 설정
ANALYSIS_DAYS = 14  # 최근 14일
TOP_N_GROUPS = 6    # 상위 6개 결과

# 상태별 가중치
STATUS_WEIGHTS = {
    'OPEN': 1.0,
    'CLOSING_SOON': 1.2,
    'COMPLETED': 0.3,
    'CLOSED': 0.1
}

# 시간 가중치 함수
def get_time_weight(days: int) -> float:
    """최근일수록 높은 가중치 반환"""
    if days <= 7:
        return 1.0
    elif days <= 14:
        return 0.8
    else:
        return 0.6