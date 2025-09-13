"""
테스트 스케줄 작업 생성 스크립트
"""

import asyncpg
import asyncio
from datetime import datetime, timedelta
import uuid

async def create_test_schedule():
    """테스트 스케줄 작업 생성"""
    try:
        # 데이터베이스 연결
        conn = await asyncpg.connect(
            host="0.0.0.0",
            port=15432,
            user="svc_dev",
            password="IOT_dev_123!@#",
            database="iot_care"
        )
        
        # 현재 시간 + 1분
        now = datetime.utcnow()
        next_run = now + timedelta(minutes=1)
        
        # 테스트 작업 데이터
        job_id = str(uuid.uuid4())
        job_data = {
            'id': job_id,
            'name': 'test_1min_schedule',
            'func': 'test_module.test_1min_function',
            'cron': f"{next_run.minute} {next_run.hour} {next_run.day} {next_run.month} *",  # 1분 후 실행
            'args': '{"test": "1min_schedule"}',
            'kwargs': '{"priority": "high"}',
            'enabled': True,
            'status': 'idle',
            'next_run_at': next_run,
            'created_at': now,
            'updated_at': now,
            'is_deleted': False
        }
        
        # SQL 쿼리
        insert_query = """
        INSERT INTO scheduled_jobs (
            id, name, func, cron, args, kwargs, enabled, status,
            last_run_at, next_run_at, created_at, updated_at, is_deleted, deleted_at
        ) VALUES (
            $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14
        )
        """
        
        # 작업 삽입
        await conn.execute(
            insert_query,
            job_data['id'],
            job_data['name'],
            job_data['func'],
            job_data['cron'],
            job_data['args'],
            job_data['kwargs'],
            job_data['enabled'],
            job_data['status'],
            None,  # last_run_at
            job_data['next_run_at'],
            job_data['created_at'],
            job_data['updated_at'],
            job_data['is_deleted'],
            None   # deleted_at
        )
        
        print(f"✅ 테스트 스케줄 작업 생성 완료!")
        print(f"   - 작업 ID: {job_id}")
        print(f"   - 작업명: {job_data['name']}")
        print(f"   - 함수: {job_data['func']}")
        print(f"   - Cron: {job_data['cron']}")
        print(f"   - 다음 실행: {next_run.strftime('%Y-%m-%d %H:%M:%S')} UTC")
        print(f"   - 현재 시간: {now.strftime('%Y-%m-%d %H:%M:%S')} UTC")
        
        await conn.close()
        return job_id
        
    except Exception as e:
        print(f"❌ 테스트 스케줄 작업 생성 실패: {e}")
        return None

if __name__ == "__main__":
    asyncio.run(create_test_schedule())
