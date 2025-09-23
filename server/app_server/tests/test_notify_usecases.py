import pytest
from uuid import UUID, uuid4

from app.application.use_cases.notify_queue_use_cases import CreateMessageAndQueueUseCase
from app.application.dto.notify_queue_dto import NotifyQueueRequest


class _Msg:
    def __init__(self, mid):
        self.message_id = mid


class FakeMessageRepo:
    def __init__(self):
        self.saved = []

    async def create(self, payload: dict):
        mid = uuid4()
        self.saved.append({"message_id": mid, **payload})
        return _Msg(mid)


class FakeDeliveryRepo:
    def __init__(self):
        self.saved = []

    async def create(self, payload: dict):
        self.saved.append(payload)
        return payload


class FakeDeviceRepo:
    pass


@pytest.mark.asyncio
async def test_create_message_and_queue_basic():
    msg_repo = FakeMessageRepo()
    deliv_repo = FakeDeliveryRepo()
    device_repo = FakeDeviceRepo()
    uc = CreateMessageAndQueueUseCase(msg_repo, deliv_repo, device_repo)

    u1 = uuid4()
    u2 = uuid4()
    req = NotifyQueueRequest(
        kind="info",
        severity="green",
        title="t",
        body="b",
        data={"k": 1},
        expires_at=None,  # 무기한
        recipients=[u1, u2],
        channel="websocket",
    )

    res = await uc.execute(req)
    assert res["queued_count"] == 2
    assert len(deliv_repo.saved) == 2
    assert {d["user_id"] for d in deliv_repo.saved} == {u1, u2}


