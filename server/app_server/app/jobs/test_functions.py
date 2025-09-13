"""
테스트용 스케줄 작업 함수들
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Dict

logger = logging.getLogger(__name__)

async def test_function(*args, **kwargs):
    """기본 테스트 함수"""
    logger.info(f"테스트 함수 실행: args={args}, kwargs={kwargs}")
    return {"status": "success", "message": "테스트 함수 실행 완료"}

async def test_1min_function(*args, **kwargs):
    """1분 테스트 함수"""
    now = datetime.now(timezone.utc)
    logger.info(f"1분 테스트 함수 실행: {now.isoformat()}")
    logger.info(f"인자: args={args}, kwargs={kwargs}")
    
    # 간단한 작업 시뮬레이션
    await asyncio.sleep(1)
    
    return {
        "status": "success",
        "message": "1분 테스트 함수 실행 완료",
        "timestamp": now.isoformat(),
        "args": args,
        "kwargs": kwargs
    }

async def test_5min_function(*args, **kwargs):
    """5분 테스트 함수"""
    now = datetime.now(timezone.utc)
    logger.info(f"5분 테스트 함수 실행: {now.isoformat()}")
    
    # 더 복잡한 작업 시뮬레이션
    await asyncio.sleep(2)
    
    return {
        "status": "success",
        "message": "5분 테스트 함수 실행 완료",
        "timestamp": now.isoformat()
    }

async def test_error_function(*args, **kwargs):
    """오류 발생 테스트 함수"""
    logger.info("오류 테스트 함수 실행")
    raise Exception("의도된 테스트 오류")

def test_sync_function(*args, **kwargs):
    """동기 테스트 함수"""
    logger.info(f"동기 테스트 함수 실행: args={args}, kwargs={kwargs}")
    return {"status": "success", "message": "동기 함수 실행 완료"}

# 모듈 레벨 함수들 (스케줄러에서 호출 가능)
async def scheduled_health_check(*args, **kwargs):
    """정기 헬스 체크 함수"""
    now = datetime.now(timezone.utc)
    logger.info(f"헬스 체크 실행: {now.isoformat()}")
    
    # 시스템 상태 체크 시뮬레이션
    await asyncio.sleep(0.5)
    
    return {
        "status": "healthy",
        "timestamp": now.isoformat(),
        "checks": {
            "database": "ok",
            "redis": "ok",
            "scheduler": "ok"
        }
    }

async def scheduled_cleanup(*args, **kwargs):
    """정기 정리 작업 함수"""
    now = datetime.now(timezone.utc)
    logger.info(f"정리 작업 실행: {now.isoformat()}")
    
    # 정리 작업 시뮬레이션
    await asyncio.sleep(1)
    
    return {
        "status": "completed",
        "message": "정리 작업 완료",
        "timestamp": now.isoformat(),
        "cleaned_items": 10
    }
