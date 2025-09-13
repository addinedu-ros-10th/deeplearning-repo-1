"""
APScheduler 스케줄러 서비스
데이터베이스의 scheduled_jobs 테이블을 소스 오브 트루스로 사용하여 스케줄 작업을 관리
"""

import asyncio
import logging
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
import asyncpg
import os
from dotenv import load_dotenv

# 환경 변수 로딩
load_dotenv('secret/.env.local')

logger = logging.getLogger(__name__)

class SchedulerService:
    """APScheduler 스케줄러 서비스"""
    
    def __init__(self):
        self.scheduler: Optional[AsyncIOScheduler] = None
        self.db_url = self._get_db_url()
        self.is_running = False
        
    def _get_db_url(self) -> str:
        """데이터베이스 URL 생성"""
        db_url = os.getenv('DB_APP_URL', 'postgresql://svc_dev:IOT_dev_123%21%40%23@host.docker.internal:15432/iot_care')
        if db_url.startswith('postgresql+asyncpg://'):
            db_url = db_url.replace('postgresql+asyncpg://', 'postgresql://')
        return db_url
    
    async def initialize(self):
        """스케줄러 초기화"""
        try:
            # Job Store 설정 (PostgreSQL 사용)
            jobstore = SQLAlchemyJobStore(url=self.db_url)
            
            # Executor 설정
            executor = AsyncIOExecutor()
            
            # 스케줄러 설정
            self.scheduler = AsyncIOScheduler(
                jobstores={'default': jobstore},
                executors={'default': executor},
                job_defaults={
                    'coalesce': False,
                    'max_instances': 3,
                    'misfire_grace_time': 30
                },
                timezone='UTC'
            )
            
            # 이벤트 리스너 등록
            self.scheduler.add_listener(self._job_executed, EVENT_JOB_EXECUTED)
            self.scheduler.add_listener(self._job_error, EVENT_JOB_ERROR)
            
            logger.info("스케줄러 초기화 완료")
            
        except Exception as e:
            logger.error(f"스케줄러 초기화 실패: {e}")
            raise
    
    async def start(self):
        """스케줄러 시작"""
        if not self.scheduler:
            await self.initialize()
        
        if not self.is_running:
            self.scheduler.start()
            self.is_running = True
            
            # 기존 작업들을 DB에서 로드
            await self._load_jobs_from_db()
            
            logger.info("스케줄러 시작 완료")
    
    async def stop(self):
        """스케줄러 중지"""
        if self.scheduler and self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("스케줄러 중지 완료")
    
    async def _load_jobs_from_db(self):
        """데이터베이스에서 활성화된 작업들을 로드"""
        try:
            conn = await asyncpg.connect(
                host="host.docker.internal",
                port=15432,
                user="svc_dev",
                password="IOT_dev_123!@#",
                database="iot_care"
            )
            
            # 활성화된 작업들 조회
            jobs = await conn.fetch("""
                SELECT id, name, func, cron, args, kwargs, enabled, status
                FROM scheduled_jobs 
                WHERE enabled = true AND is_deleted = false
                ORDER BY created_at
            """)
            
            for job_data in jobs:
                await self._add_job_to_scheduler(job_data)
            
            await conn.close()
            logger.info(f"데이터베이스에서 {len(jobs)}개 작업 로드 완료")
            
        except Exception as e:
            logger.error(f"작업 로드 실패: {e}")
    
    async def _add_job_to_scheduler(self, job_data: Dict[str, Any]):
        """스케줄러에 작업 추가"""
        try:
            job_id = job_data['id']
            name = job_data['name']
            func = job_data['func']
            cron = job_data['cron']
            args = job_data['args'] or {}
            kwargs = job_data['kwargs'] or {}
            
            # Cron 표현식 파싱
            cron_parts = cron.split()
            if len(cron_parts) != 5:
                logger.warning(f"잘못된 Cron 표현식: {cron} (작업: {name})")
                return
            
            # CronTrigger 생성
            trigger = CronTrigger(
                minute=cron_parts[0],
                hour=cron_parts[1],
                day=cron_parts[2],
                month=cron_parts[3],
                day_of_week=cron_parts[4]
            )
            
            # 작업 추가 (정적 메서드 사용)
            self.scheduler.add_job(
                func=SchedulerService._execute_job_static,
                trigger=trigger,
                args=[job_id, func, args, kwargs],
                id=job_id,
                name=name,
                replace_existing=True
            )
            
            logger.info(f"작업 추가 완료: {name} (ID: {job_id})")
            
        except Exception as e:
            logger.error(f"작업 추가 실패: {e}")
    
    @staticmethod
    async def _execute_job_static(job_id: str, func: str, args: Any, kwargs: Any):
        """작업 실행 (정적 메서드)"""
        try:
            # 전역 스케줄러 서비스 인스턴스 가져오기
            from app.services.scheduler_service import scheduler_service
            
            # 작업 상태를 'running'으로 업데이트
            await scheduler_service._update_job_status(job_id, 'running')
            
            # args와 kwargs 파싱
            parsed_args = scheduler_service._parse_json_args(args)
            parsed_kwargs = scheduler_service._parse_json_args(kwargs)
            
            # 함수 실행
            result = await scheduler_service._call_function(func, parsed_args, parsed_kwargs)
            
            # 성공 시 상태 업데이트
            await scheduler_service._update_job_status(job_id, 'completed', result)
            
            logger.info(f"작업 실행 완료: {job_id}")
            
        except Exception as e:
            # 실패 시 상태 업데이트
            try:
                from app.services.scheduler_service import scheduler_service
                await scheduler_service._update_job_status(job_id, 'failed', str(e))
            except:
                pass
            logger.error(f"작업 실행 실패: {job_id}, 오류: {e}")

    async def _execute_job(self, job_id: str, func: str, args: Any, kwargs: Any):
        """작업 실행 (인스턴스 메서드 - 호환성 유지)"""
        try:
            # 작업 상태를 'running'으로 업데이트
            await self._update_job_status(job_id, 'running')
            
            # args와 kwargs 파싱
            parsed_args = self._parse_json_args(args)
            parsed_kwargs = self._parse_json_args(kwargs)
            
            # 함수 실행
            result = await self._call_function(func, parsed_args, parsed_kwargs)
            
            # 성공 시 상태 업데이트
            await self._update_job_status(job_id, 'completed', result)
            
            logger.info(f"작업 실행 완료: {job_id}")
            
        except Exception as e:
            # 실패 시 상태 업데이트
            await self._update_job_status(job_id, 'failed', str(e))
            logger.error(f"작업 실행 실패: {job_id}, 오류: {e}")
    
    def _parse_json_args(self, data: Any) -> Any:
        """JSON 문자열을 파싱하여 Python 객체로 변환"""
        if isinstance(data, str):
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                return data
        return data
    
    async def _call_function(self, func: str, args: Dict, kwargs: Dict):
        """함수 호출"""
        try:
            # 모듈과 함수명 분리
            module_name, function_name = func.rsplit('.', 1)
            
            # 모듈 동적 임포트
            module = __import__(module_name, fromlist=[function_name])
            function = getattr(module, function_name)
            
            # 함수 실행
            if asyncio.iscoroutinefunction(function):
                result = await function(*args, **kwargs)
            else:
                result = function(*args, **kwargs)
            
            return result
            
        except Exception as e:
            logger.error(f"함수 호출 실패: {func}, 오류: {e}")
            raise
    
    async def _update_job_status(self, job_id: str, status: str, result: Any = None):
        """작업 상태 업데이트"""
        try:
            conn = await asyncpg.connect(
                host="host.docker.internal",
                port=15432,
                user="svc_dev",
                password="IOT_dev_123!@#",
                database="iot_care"
            )
            
            now = datetime.now(timezone.utc)
            
            # 상태 업데이트
            await conn.execute("""
                UPDATE scheduled_jobs 
                SET status = $1, last_run_at = $2, updated_at = $3
                WHERE id = $4
            """, status, now, now, job_id)
            
            # 결과가 있으면 로그에 기록
            if result is not None:
                logger.info(f"작업 결과: {job_id} -> {result}")
            
            await conn.close()
            
        except Exception as e:
            logger.error(f"작업 상태 업데이트 실패: {e}")
    
    async def _job_executed(self, event):
        """작업 실행 완료 이벤트"""
        logger.info(f"작업 실행 완료: {event.job_id}")
    
    async def _job_error(self, event):
        """작업 실행 오류 이벤트"""
        logger.error(f"작업 실행 오류: {event.job_id}, 오류: {event.exception}")
    
    async def add_job(self, job_data: Dict[str, Any]):
        """새 작업 추가"""
        await self._add_job_to_scheduler(job_data)
    
    async def remove_job(self, job_id: str):
        """작업 제거"""
        if self.scheduler:
            self.scheduler.remove_job(job_id)
            logger.info(f"작업 제거 완료: {job_id}")
    
    async def reload_jobs(self):
        """작업 재로드"""
        if self.scheduler:
            # 기존 작업들 제거
            for job in self.scheduler.get_jobs():
                self.scheduler.remove_job(job.id)
            
            # DB에서 다시 로드
            await self._load_jobs_from_db()
            logger.info("작업 재로드 완료")
    
    def get_jobs(self) -> List[Dict[str, Any]]:
        """현재 스케줄러의 작업 목록 반환"""
        if not self.scheduler:
            return []
        
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                'id': job.id,
                'name': job.name,
                'next_run_time': getattr(job, 'next_run_time', None),
                'trigger': str(job.trigger)
            })
        
        return jobs

# 전역 스케줄러 서비스 인스턴스
scheduler_service = SchedulerService()
