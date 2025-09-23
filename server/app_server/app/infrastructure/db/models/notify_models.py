"""
SQLAlchemy models for notify schema (pre-existing tables).
Note: Tables are assumed to exist via SQL scripts; models are for ORM mapping only.
"""

from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Text, TIMESTAMP, Boolean, BigInteger
from sqlalchemy.dialects import postgresql
from sqlalchemy import Index

Base = declarative_base()


class NotifyMessage(Base):
    __tablename__ = "notify_message"
    __table_args__ = {"schema": "notify"}

    message_id = Column(postgresql.UUID(as_uuid=True), primary_key=True)
    kind = Column(postgresql.ENUM(
        'system','schedule','info','contact','marketing','inbound',
        name="kind_enum", schema="notify", create_type=False
    ), nullable=False)
    severity = Column(postgresql.ENUM(
        'green','blue','yellow','orange','red',
        name="severity_enum", schema="notify", create_type=False
    ), nullable=False)
    title = Column(Text)
    body = Column(Text)
    data = Column(postgresql.JSONB)
    scheduled_at = Column(postgresql.TIMESTAMP(timezone=True))
    expires_at = Column(postgresql.TIMESTAMP(timezone=True))
    created_by = Column(postgresql.UUID(as_uuid=True))
    created_ip = Column(postgresql.INET)
    created_at = Column(postgresql.TIMESTAMP(timezone=True), nullable=False)
    updated_at = Column(postgresql.TIMESTAMP(timezone=True), nullable=False)


class NotifyDelivery(Base):
    __tablename__ = "notify_delivery"
    __table_args__ = {"schema": "notify"}

    delivery_id = Column(BigInteger, primary_key=True, autoincrement=True)
    message_id = Column(postgresql.UUID(as_uuid=True), nullable=False)
    user_id = Column(postgresql.UUID(as_uuid=True), nullable=False)
    channel = Column(postgresql.ENUM(
        'websocket','sse','push','email','sms','voice','kakao',
        name="channel_enum", schema="notify", create_type=False
    ), nullable=False)
    endpoint = Column(Text)
    status = Column(postgresql.ENUM(
        'queued','sent','delivered','read','ack','failed','expired','canceled',
        name="delivery_status_enum", schema="notify", create_type=False
    ), nullable=False)
    send_at = Column(postgresql.TIMESTAMP(timezone=True))
    delivered_at = Column(postgresql.TIMESTAMP(timezone=True))
    read_at = Column(postgresql.TIMESTAMP(timezone=True))
    ack_at = Column(postgresql.TIMESTAMP(timezone=True))
    error_text = Column(Text)
    payload = Column(postgresql.JSONB)
    client_meta = Column(postgresql.JSONB)
    created_at = Column(postgresql.TIMESTAMP(timezone=True), nullable=False)
    updated_at = Column(postgresql.TIMESTAMP(timezone=True), nullable=False)


class NotifyDevice(Base):
    __tablename__ = "notify_device"
    __table_args__ = {"schema": "notify"}

    device_id = Column(postgresql.UUID(as_uuid=True), primary_key=True)
    user_id = Column(postgresql.UUID(as_uuid=True), nullable=False)
    channel = Column(postgresql.ENUM(
        'websocket','sse','push','email','sms','voice','kakao',
        name="channel_enum", schema="notify", create_type=False
    ), nullable=False)
    endpoint = Column(Text, nullable=False)
    is_active = Column(Boolean, nullable=False)
    device_meta = Column(postgresql.JSONB)
    last_seen_at = Column(postgresql.TIMESTAMP(timezone=True))
    created_at = Column(postgresql.TIMESTAMP(timezone=True), nullable=False)
    updated_at = Column(postgresql.TIMESTAMP(timezone=True), nullable=False)


