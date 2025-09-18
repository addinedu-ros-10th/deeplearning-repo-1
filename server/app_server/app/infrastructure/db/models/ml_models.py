"""
ML 레지스트리 SQLAlchemy 모델
PostgreSQL ML 스키마용 모델 정의
"""

from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey, UniqueConstraint, Index, text, Integer, BigInteger, CheckConstraint, Numeric
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from uuid import uuid4

Base = declarative_base()

class DatasetModel(Base):
    """데이터셋 모델 - ML 스키마"""
    __tablename__ = "dataset"
    __table_args__ = {'schema': 'ml'}
    
    dataset_id = Column(
        postgresql.UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid4,
        comment="데이터셋 스냅샷의 고유 ID (UUID)"
    )
    name = Column(
        Text, 
        nullable=False,
        comment="데이터셋 명(개념명). 예: AIHub_FallRisk_video_only"
    )
    version = Column(
        Text, 
        nullable=False, 
        server_default='v1',
        comment="데이터셋 버전. 예: v1, 2025-09-13, exp001 등 팀 규칙에 맞춘 버전명"
    )
    storage_path = Column(
        Text, 
        nullable=False,
        comment="해당 버전 스냅샷의 경로(절대 경로/URI). 예: file:///..., s3://..., gcs://..."
    )
    description = Column(
        Text,
        comment="데이터셋 설명/정제 규칙/사용 가이드 등 자유 기술"
    )
    creator_name = Column(
        Text,
        comment="데이터셋 생성자/책임자 이름(또는 조직/팀명)"
    )
    creator_email = Column(
        Text,
        comment="데이터셋 생성자/책임자 연락 이메일"
    )
    source_url = Column(
        Text,
        comment="원천 데이터/설명 페이지 링크. 예: AI-Hub 상세 페이지 URL"
    )
    license = Column(
        Text,
        comment="사용/배포 조건(라이선스 텍스트 요약 또는 링크)"
    )
    class_schema = Column(
        postgresql.JSONB, 
        nullable=False,
        server_default='{"labels":["normal","warning","fall"]}',
        comment="클래스 정의 JSON. 예: {\"labels\":[\"normal\",\"warning\",\"fall\"]} — 실험 코드가 동일 라벨 셋을 참조하도록 고정"
    )
    tags = Column(
        postgresql.ARRAY(Text),
        comment="검색/분류를 위한 자유 태그 배열. 예: {fall, pose, mediapipe, lstm}"
    )
    created_at = Column(
        postgresql.TIMESTAMP(timezone=True), 
        nullable=False, 
        server_default=text('now()'),
        comment="해당 스냅샷 레코드 생성 시각(서버 타임존 기준 timestamptz)"
    )
    
    # 관계 설정
    experiments = relationship("ExperimentModel", back_populates="dataset", cascade="all, delete-orphan")
    
    # 제약조건
    __table_args__ = (
        UniqueConstraint('name', 'version', name='uq_dataset_name_version'),
        Index('ml_dataset_tags_gin', 'tags', postgresql_using='gin'),
        {'schema': 'ml'}
    )

class ExperimentModel(Base):
    """실험 모델 - ML 스키마"""
    __tablename__ = "experiment"
    __table_args__ = {'schema': 'ml'}
    
    experiment_id = Column(
        postgresql.UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid4,
        comment="실험(학습 실행) 고유 ID (UUID)"
    )
    name = Column(
        Text, 
        nullable=False,
        comment="실험 명칭. 예: lstm_fall_detection_v1 (동일 데이터셋 내 중복 방지)"
    )
    dataset_id = Column(
        postgresql.UUID(as_uuid=True), 
        ForeignKey('ml.dataset.dataset_id', ondelete='RESTRICT'),
        nullable=False,
        comment="참조한 데이터셋 버전의 ID(FK). 어떤 데이터로 학습되었는지 명확히 연결"
    )
    model_path = Column(
        Text, 
        nullable=False,
        comment="훈련된 모델 가중치/그래프 파일 경로. 예: file:///..., s3://..."
    )
    framework = Column(
        Text,
        comment="프레임워크 정보. 예: PyTorch, TensorFlow, ONNX 등"
    )
    code_version = Column(
        Text,
        comment="코드 버전(예: git commit hash). 결과 재현성/책임성 확보에 필수"
    )
    params = Column(
        postgresql.JSONB,
        comment="하이퍼파라미터 JSON. 예: {\"seq_len\":60,\"stride\":30,\"hidden_size\":128,\"epochs\":100,\"lr\":1e-3}"
    )
    metrics = Column(
        postgresql.JSONB,
        comment="평가지표 JSON. 예: {\"val_acc\":0.92,\"f1_macro\":0.88,\"confusion\":[[...]]}"
    )
    created_at = Column(
        postgresql.TIMESTAMP(timezone=True), 
        nullable=False, 
        server_default=text('now()'),
        comment="실험 레코드 생성 시각(서버 타임존 기준 timestamptz)"
    )
    
    # 관계 설정
    dataset = relationship("DatasetModel", back_populates="experiments")
    
    # 제약조건 및 인덱스
    __table_args__ = (
        UniqueConstraint('name', 'dataset_id', name='uq_experiment_name_dataset'),
        Index('ml_experiment_dataset_idx', 'dataset_id'),
        Index('ml_experiment_created_idx', 'created_at'),
        {'schema': 'ml'}
    )


class FramePredictionModel(Base):
    """프레임 단위 추론 결과 - ML 스키마"""
    __tablename__ = "frame_prediction"
    __table_args__ = (
        UniqueConstraint('session_id', 'experiment_id', 'frame_index', name='uq_framepred_session_exp_frame'),
        Index('ix_framepred_exp', 'experiment_id'),
        Index('ix_framepred_session_frame', 'session_id', 'frame_index'),
        Index('ix_framepred_label', 'label_pred'),
        Index('gin_framepred_probs', 'probabilities', postgresql_using='gin'),
        CheckConstraint("label_pred IN ('normal','warning','fall')", name='ck_framepred_label_pred'),
        {'schema': 'ml'}
    )

    frame_pred_id = Column(
        BigInteger, primary_key=True, autoincrement=True,
        comment="프레임 예측 레코드 식별자(BIGSERIAL)"
    )
    session_id = Column(
        postgresql.UUID(as_uuid=True), nullable=False,
        comment="동일 입력(영상/스트림) 추론 실행 세션 키"
    )
    experiment_id = Column(
        postgresql.UUID(as_uuid=True),
        ForeignKey('ml.experiment.experiment_id', ondelete='RESTRICT'),
        nullable=False,
        comment="사용된 모델/실험(experiment) FK"
    )
    input_uri = Column(
        Text, nullable=False,
        comment="입력 원본의 URI (file:///..., s3://..., rtsp://...)"
    )
    frame_index = Column(
        Integer, nullable=False,
        comment="프레임 인덱스(1..N)"
    )
    ts_rel_ms = Column(
        BigInteger,
        comment="세션 시작 기준 상대 타임스탬프(ms)"
    )
    label_pred = Column(
        String(16), nullable=False,
        comment="예측 라벨(normal|warning|fall)"
    )
    confidence = Column(
        Numeric(5, 4),
        comment="신뢰도(probabilities의 최댓값 등)"
    )
    probabilities = Column(
        postgresql.JSONB, nullable=False,
        comment='클래스별 확률 JSON (예: {"normal":0.85,"warning":0.08,"fall":0.07})'
    )
    passed = Column(
        Boolean,
        comment="프레임 레벨 임계치 충족 여부"
    )
    threshold_name = Column(
        Text,
        comment="적용 임계치 정책명"
    )
    threshold_snapshot = Column(
        postgresql.JSONB,
        comment="실행 시점 임계치 JSON 스냅샷"
    )
    created_at = Column(
        postgresql.TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'),
        comment="레코드 생성 시각"
    )


class DetectionEventModel(Base):
    """임계치 충족 이벤트 - ML 스키마"""
    __tablename__ = "detection_event"
    __table_args__ = (
        Index('ix_detevent_session_created', 'session_id', 'created_at'),
        Index('ix_detevent_event_type', 'event_type'),
        Index('ix_detevent_top_label', 'top_label'),
        Index('gin_detevent_aggprob', 'agg_prob', postgresql_using='gin'),
        CheckConstraint('end_frame >= start_frame', name='ck_detevent_frame_range'),
        CheckConstraint("top_label IN ('normal','warning','fall')", name='ck_detevent_top_label'),
        {'schema': 'ml'}
    )

    event_id = Column(
        postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4,
        comment="이벤트 고유 ID(UUID)"
    )
    session_id = Column(
        postgresql.UUID(as_uuid=True), nullable=False,
        comment="이벤트가 발생한 세션 키"
    )
    experiment_id = Column(
        postgresql.UUID(as_uuid=True),
        ForeignKey('ml.experiment.experiment_id', ondelete='RESTRICT'),
        nullable=False,
        comment="이벤트를 발생시킨 모델/실험 FK"
    )
    input_uri = Column(
        Text, nullable=False,
        comment="입력 원본의 URI"
    )
    start_frame = Column(
        Integer, nullable=False,
        comment="이벤트 구간 시작 프레임"
    )
    end_frame = Column(
        Integer, nullable=False,
        comment="이벤트 구간 종료 프레임"
    )
    start_ts_ms = Column(
        BigInteger,
        comment="세션 시작 기준 이벤트 시작 시각(ms)"
    )
    end_ts_ms = Column(
        BigInteger,
        comment="세션 시작 기준 이벤트 종료 시각(ms)"
    )
    event_type = Column(
        String(32), nullable=False,
        comment="이벤트 유형 키 (예: fall_detected, warning_continuous)"
    )
    top_label = Column(
        String(16), nullable=False,
        comment="이벤트 대표 라벨"
    )
    max_confidence = Column(
        Numeric(5, 4),
        comment="구간 내 최고 confidence"
    )
    agg_prob = Column(
        postgresql.JSONB,
        comment="구간의 집계 확률(JSON)"
    )
    threshold_name = Column(
        Text,
        comment="적용한 임계치 정책명"
    )
    threshold_snapshot = Column(
        postgresql.JSONB, nullable=False,
        comment="임계치 규칙의 스냅샷(JSON)"
    )
    trigger_reason = Column(
        Text,
        comment="임계치 충족 사유 요약"
    )
    created_at = Column(
        postgresql.TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'),
        comment="이벤트 기록 생성 시각"
    )
