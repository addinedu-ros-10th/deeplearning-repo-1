import pytest
import os
import asyncio

from app.services.notify_dispatcher import dispatcher_loop


@pytest.mark.asyncio
async def test_dispatcher_does_not_start_when_flags_false(monkeypatch):
    monkeypatch.setenv('NOTIFY_ENABLE', 'false')
    monkeypatch.setenv('NOTIFY_DISPATCH_ENABLE', 'false')
    # should return immediately without looping
    await dispatcher_loop(poll_interval=0.01, batch=1)


