import asyncio
import datetime
from unittest import mock

import pytest
from domain.errors.base_exceptions import UnexpectedError
from domain.events.batch_processor import EventBatch, EventBatchProcessor, EventBatchRegistry
from domain.events.controllable_event import ControllableEvent
from domain.events.exceptions import RetryLater
from domain.events.models.event import Event
from tests.event_handler import TestEventHandler
from tests.rabbitmq_test_impl import TestQueueControlInterface
from tests.task import TestTask

ts = datetime.datetime.now().timestamp()


@pytest.fixture
def events() -> list[Event[TestTask]]:
    return [
        ControllableEvent(
            Event[TestTask](
                id="1",
                event="test",
                data=TestTask(value="1"),
                timestamp=ts,
            ),
            TestQueueControlInterface(),
        ),
        ControllableEvent(
            Event[TestTask](
                id="2",
                event="test",
                data=TestTask(value="2"),
                timestamp=ts,
                rollback=True,
            ),
            TestQueueControlInterface(),
        ),
    ]


@pytest.mark.unit
async def test_batch_flush_ok(events):
    handler = TestEventHandler()
    batch = EventBatch(handler, mock.Mock(), events)

    assert batch.events == [events[0], events[1]]
    assert len(handler.received_events) == 0

    await asyncio.sleep(0.05)

    assert batch.events == [events[0], events[1]]
    assert len(handler.received_events) == 0

    await asyncio.sleep(0.10)

    assert len(batch.events) == 0
    assert handler.received_events == [events[0].event, events[1].event]
    assert events[0].control.status == "acked"
    assert events[1].control.status == "acked"
    assert batch.flush_task is None


@pytest.mark.unit
async def test_batch_flush_fail(events):
    handler = TestEventHandler(fail=True)
    batch = EventBatch(handler, mock.Mock(), events)

    await asyncio.sleep(0.15)

    assert len(batch.events) == 0
    assert handler.received_events == [events[0].event, events[1].event]
    assert events[0].control.status == "retried"
    assert events[1].control.status == "retried"
    assert batch.flush_task is None


@pytest.mark.unit
async def test_batch_flush_delay(events):
    handler = TestEventHandler(delay=True)
    batch = EventBatch(handler, mock.Mock(), events)

    await asyncio.sleep(0.15)

    assert len(batch.events) == 0
    assert handler.received_events == [events[0].event, events[1].event]
    assert events[0].control.status == "delayed"
    assert events[1].control.status == "delayed"
    assert batch.flush_task is None


@pytest.mark.unit
async def test_batch_flush_new_events_while_flushing(events, monkeypatch):
    async def mock_handle_batch(self: TestEventHandler, events: list[Event]):
        self.received_events.extend(events)
        batch.add(extra_event)

    real_handle_batch = TestEventHandler.handle_batch
    monkeypatch.setattr(TestEventHandler, "handle_batch", mock_handle_batch)

    handler = TestEventHandler()
    batch = EventBatch(handler, mock.Mock(), events)

    extra_event = ControllableEvent(
        Event[TestTask](id="3", event="test", data=TestTask(value="3"), timestamp=ts),
        TestQueueControlInterface(),
    )

    assert batch.events == [events[0], events[1]]
    assert len(handler.received_events) == 0

    await asyncio.sleep(0.15)

    assert batch.events == [extra_event]
    assert handler.received_events == [events[0].event, events[1].event]
    assert events[0].control.status == "acked"
    assert events[1].control.status == "acked"
    assert batch.flush_task is not None

    monkeypatch.setattr(TestEventHandler, "handle_batch", real_handle_batch)

    await asyncio.sleep(0.10)

    assert len(batch.events) == 0
    assert handler.received_events == [events[0].event, events[1].event, extra_event.event]
    assert extra_event.control.status == "acked"
    assert batch.flush_task is None


@pytest.mark.unit
async def test_batch_registry():
    handler = TestEventHandler()
    registry = EventBatchRegistry()

    batch1 = registry.get("1", lambda: EventBatch(handler, mock.Mock()))
    batch2 = registry.get("2", lambda: EventBatch(handler, mock.Mock()))

    assert registry.get("1", lambda: EventBatch(handler, mock.Mock())) == batch1
    assert registry.get("2", lambda: EventBatch(handler, mock.Mock())) == batch2

    assert registry.batches == {"1": batch1, "2": batch2}

    batch2.flush_task = "test"
    registry._cleanup()
    assert registry.batches == {"2": batch2}


@pytest.mark.unit
async def test_processor_immediate_ok(events):
    handler = TestEventHandler()
    processor = EventBatchProcessor(mock.Mock())
    event = events[0]
    await processor.handle(handler, event)
    assert event.control.status == "acked"
    assert len(handler.rolled_back_events) == 0


@pytest.mark.unit
async def test_processor_immediate_ok_rollback(events):
    handler = TestEventHandler()
    processor = EventBatchProcessor(mock.Mock())
    event = events[1]
    await processor.handle(handler, event)
    assert event.control.status == "acked"
    assert handler.rolled_back_events[0] == event.event


@pytest.mark.unit
async def test_processor_immediate_fail(events):
    handler = TestEventHandler(fail=True)
    processor = EventBatchProcessor(mock.Mock())
    event = events[0]
    with pytest.raises(UnexpectedError):
        await processor.handle(handler, event)
        assert event.control.status == "retried"


@pytest.mark.unit
async def test_processor_immediate_delay(events):
    handler = TestEventHandler(delay=True)
    processor = EventBatchProcessor(mock.Mock())
    event = events[1]
    with pytest.raises(RetryLater):
        await processor.handle(handler, event)
        assert event.control.status == "delayed"


@pytest.mark.unit
async def test_processor_batched(events):
    handler = TestEventHandler(batch_id="test")
    processor = EventBatchProcessor(mock.Mock())

    await processor.handle(handler, events[0])
    await processor.handle(handler, events[1])

    assert events[0].control.status == ""
    assert events[1].control.status == ""

    await asyncio.sleep(0.15)

    assert events[0].control.status == "acked"
    assert events[1].control.status == "acked"
