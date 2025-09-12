#!/usr/bin/env python3
"""
데이터베이스 연결 테스트 스크립트
"""

import os
import asyncio
import asyncpg
from dotenv import load_dotenv

# 환경 변수 로딩
load_dotenv('secret/.env.local')

async def test_connection():
    """데이터베이스 연결 테스트"""
    try:
        # 환경 변수에서 DB URL 가져오기
        db_url = os.getenv('DB_APP_URL')
        if not db_url:
            print("❌ DB_APP_URL 환경 변수가 설정되지 않았습니다.")
            return False
        
        # asyncpg용 URL로 변환 (postgresql+asyncpg -> postgresql)
        db_url = db_url.replace('postgresql+asyncpg://', 'postgresql://')
        
        # URL 파싱하여 포트 확인
        print(f"🔍 URL 분석: {db_url}")
        if ':15432' not in db_url:
            print("❌ 포트 15432가 URL에 포함되지 않았습니다.")
            return False
        
        print(f"🔗 데이터베이스 연결 시도: {db_url}")
        
        # 데이터베이스 연결 테스트 (포트 명시적 지정)
        conn = await asyncpg.connect(
            host="0.0.0.0",
            port=15432,
            user="svc_dev",
            password="IOT_dev_123!@#",
            database="iot_care"
        )
        
        # 간단한 쿼리 실행
        result = await conn.fetchval("SELECT version()")
        print(f"✅ 데이터베이스 연결 성공!")
        print(f"📊 PostgreSQL 버전: {result}")
        
        # 연결 종료
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 데이터베이스 연결 실패: {e}")
        return False

async def main():
    """메인 함수"""
    print("🚀 데이터베이스 연결 테스트 시작")
    print("=" * 50)
    
    success = await test_connection()
    
    if success:
        print("\n🎉 데이터베이스 연결이 성공했습니다!")
    else:
        print("\n❌ 데이터베이스 연결에 실패했습니다.")
        print("💡 SSH 터널이 실행 중인지 확인하세요.")

if __name__ == "__main__":
    asyncio.run(main())
