"""create_scheduled_jobs_only

Revision ID: 20250912_create_scheduled_jobs_only
Revises: 20250912_create_scheduled_jobs
Create Date: 2025-09-12 17:10:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as psql

# revision identifiers, used by Alembic.
revision = '20250912_create_scheduled_jobs_only'
down_revision = '20250912_create_scheduled_jobs'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """scheduled_jobs 테이블만 생성 (기존 테이블은 건드리지 않음)"""
    # 테이블이 이미 존재하는지 확인
    connection = op.get_bind()
    result = connection.execute(sa.text("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'scheduled_jobs'
        )
    """))
    
    if not result.scalar():
        # 테이블이 존재하지 않으면 생성
        op.create_table(
            'scheduled_jobs',
            sa.Column('id', sa.String(length=36), primary_key=True, comment='작업 고유 ID'),
            sa.Column('name', sa.String(length=120), nullable=False, unique=True, comment='작업 이름'),
            sa.Column('func', sa.String(length=200), nullable=False, comment='실행할 함수 (module:function 형태)'),
            sa.Column('cron', sa.String(length=64), nullable=False, comment='Cron 표현식'),
            sa.Column('args', psql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb"), comment='함수 인자'),
            sa.Column('kwargs', psql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb"), comment='함수 키워드 인자'),
            sa.Column('enabled', sa.Boolean(), nullable=False, server_default=sa.text('true'), comment='작업 활성화 여부'),
            sa.Column('last_run_at', sa.TIMESTAMP(timezone=True), nullable=True, comment='마지막 실행 시간'),
            sa.Column('next_run_at', sa.TIMESTAMP(timezone=True), nullable=True, comment='다음 실행 시간'),
            sa.Column('status', sa.String(length=32), server_default=sa.text("'idle'"), comment='작업 상태 (idle, running, failed, completed)'),
            sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.text('false'), comment='논리 삭제 여부'),
            sa.Column('deleted_at', sa.TIMESTAMP(timezone=True), nullable=True, comment='논리 삭제 시간'),
            sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), comment='생성 시간'),
            sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), comment='수정 시간'),
        )
        
        # 인덱스 생성
        op.create_index('ix_scheduled_jobs_name', 'scheduled_jobs', ['name'], unique=True)
        op.create_index('ix_scheduled_jobs_enabled', 'scheduled_jobs', ['enabled'])
        op.create_index('ix_scheduled_jobs_status', 'scheduled_jobs', ['status'])
        op.create_index('ix_scheduled_jobs_is_deleted', 'scheduled_jobs', ['is_deleted'])
        op.create_index('ix_scheduled_jobs_next_run', 'scheduled_jobs', ['next_run_at'])


def downgrade() -> None:
    """scheduled_jobs 테이블 삭제"""
    op.drop_index('ix_scheduled_jobs_next_run', table_name='scheduled_jobs')
    op.drop_index('ix_scheduled_jobs_is_deleted', table_name='scheduled_jobs')
    op.drop_index('ix_scheduled_jobs_status', table_name='scheduled_jobs')
    op.drop_index('ix_scheduled_jobs_enabled', table_name='scheduled_jobs')
    op.drop_index('ix_scheduled_jobs_name', table_name='scheduled_jobs')
    op.drop_table('scheduled_jobs')
