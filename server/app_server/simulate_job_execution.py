"""
스케줄 작업 실행 시뮬레이션 스크립트
"""

import asyncpg
import asyncio
from datetime import datetime, timedelta

async def simulate_job_execution():
    """스케줄 작업 실행 시뮬레이션"""
    try:
        # 데이터베이스 연결
        conn = await asyncpg.connect(
            host="0.0.0.0",
            port=15432,
            user="svc_dev",
            password="IOT_dev_123!@#",
            database="iot_care"
        )
        
        # 현재 시간
        now = datetime.utcnow()
        
        # test_1min_schedule 작업을 실행된 것으로 업데이트
        update_query = """
        UPDATE scheduled_jobs 
        SET 
            status = 'completed',
            last_run_at = $1,
            next_run_at = $2,
            updated_at = $3
        WHERE name = 'test_1min_schedule'
        """
        
        # 다음 실행 시간 (1시간 후로 설정)
        next_run = now + timedelta(hours=1)
        
        await conn.execute(
            update_query,
            now,  # last_run_at
            next_run,  # next_run_at
            now   # updated_at
        )
        
        print(f"✅ 스케줄 작업 실행 시뮬레이션 완료!")
        print(f"   - 작업명: test_1min_schedule")
        print(f"   - 실행 시간: {now.strftime('%Y-%m-%d %H:%M:%S')} UTC")
        print(f"   - 상태: completed")
        print(f"   - 다음 실행: {next_run.strftime('%Y-%m-%d %H:%M:%S')} UTC")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ 작업 실행 시뮬레이션 실패: {e}")

if __name__ == "__main__":
    asyncio.run(simulate_job_execution())
