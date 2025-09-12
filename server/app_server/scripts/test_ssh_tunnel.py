#!/usr/bin/env python3
"""
SSH 터널 연결 테스트 스크립트
"""

import os
import sys
import asyncio
import asyncpg
from dotenv import load_dotenv

# 환경 변수 로딩
load_dotenv()

async def test_database_connection():
    """데이터베이스 연결 테스트"""
    try:
        # 환경 변수에서 DB URL 가져오기
        db_url = os.getenv('DB_APP_URL')
        if not db_url:
            print("❌ DB_APP_URL 환경 변수가 설정되지 않았습니다.")
            return False
        
        print(f"🔗 데이터베이스 연결 시도: {db_url}")
        
        # 데이터베이스 연결 테스트
        conn = await asyncpg.connect(db_url)
        
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

async def test_ssh_tunnel():
    """SSH 터널 테스트"""
    print("🔍 SSH 터널 설정 확인...")
    
    # 환경 변수 확인
    tunnel_enable = os.getenv('SSH_TUNNEL_ENABLE', 'false').lower() == 'true'
    local_port = os.getenv('SSH_TUNNEL_LOCAL_PORT', '15432')
    remote_host = os.getenv('SSH_TUNNEL_REMOTE_HOST')
    remote_port = os.getenv('SSH_TUNNEL_REMOTE_PORT', '5432')
    bastion_host = os.getenv('SSH_TUNNEL_BASTION_HOST')
    user = os.getenv('SSH_TUNNEL_USER', 'ubuntu')
    key_path = os.getenv('SSH_TUNNEL_KEY_PATH', 'secret/iot_db_key_pair.pem')
    
    print(f"  - SSH 터널 활성화: {tunnel_enable}")
    print(f"  - 로컬 포트: {local_port}")
    print(f"  - 원격 호스트: {remote_host}:{remote_port}")
    print(f"  - Bastion 호스트: {user}@{bastion_host}")
    print(f"  - SSH 키 경로: {key_path}")
    
    if not all([remote_host, bastion_host, key_path]):
        print("❌ SSH 터널 설정이 불완전합니다.")
        return False
    
    # SSH 키 파일 존재 확인
    if not os.path.exists(key_path):
        print(f"❌ SSH 키 파일이 존재하지 않습니다: {key_path}")
        return False
    
    print("✅ SSH 터널 설정이 올바릅니다.")
    return True

async def main():
    """메인 함수"""
    print("🚀 SSH 터널 및 데이터베이스 연결 테스트 시작")
    print("=" * 50)
    
    # SSH 터널 설정 확인
    tunnel_ok = await test_ssh_tunnel()
    if not tunnel_ok:
        print("\n❌ SSH 터널 설정에 문제가 있습니다.")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    
    # 데이터베이스 연결 테스트
    db_ok = await test_database_connection()
    if not db_ok:
        print("\n❌ 데이터베이스 연결에 실패했습니다.")
        print("💡 SSH 터널이 실행 중인지 확인하세요.")
        sys.exit(1)
    
    print("\n🎉 모든 테스트가 성공했습니다!")
    print("✅ SSH 터널과 데이터베이스 연결이 정상적으로 작동합니다.")

if __name__ == "__main__":
    asyncio.run(main())
