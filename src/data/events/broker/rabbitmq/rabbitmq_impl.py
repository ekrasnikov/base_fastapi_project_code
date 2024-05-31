import logging
from contextlib import asynccontextmanager
from datetime import timedelta
from typing import AsyncGenerator, AsyncIterator

import aio_pika
import di
import orjson
import pamqp
from aio_pika.abc import AbstractChannel, AbstractIncomingMessage, AbstractQueue
from app.settings import Settings
from domain.events.broker import EventBroker
from domain.events.controllable_message import ControllableMessage
from domain.events.processable_event import ProcessableEvent
from domain.events.queue_control_interface import QueueControlInterface


class RabbitMQQueueControlInterface(QueueControlInterface):
    _processed = False

    def __init__(self, message: AbstractIncomingMessage, message_data: dict, broker: EventBroker, queue_name: str):
        self._message = message
        self._message_data = message_data
        self._broker = broker
        self._queue_name = queue_name

    async def ack(self):
        if not self._processed:
            await self._message.ack()
            self._processed = True

    async def retry(self):
        await self.delay(timedelta(seconds=5))

    async def delay(self, delay: timedelta):
        if not self._processed:
            await self._broker.publish(self._queue_name, self._message_data, delay)
            await self._message.ack()
            self._processed = True


class RabbitMQEventBroker(EventBroker):
    logger: logging.Logger | None = None

    def __init__(self, settings: Settings):
        assert settings.broker
        self._broker_url: str = settings.broker.url

    async def listen(self, queue_name: str) -> AsyncIterator[ProcessableEvent]:
        if self.logger is None:
            self.logger = di.resolve(logging.Logger)()

        async with self._channel() as channel:
            queue = await self._declare_queue(channel, queue_name)

            async with queue.iterator() as queue_iterator:
                async for message in queue_iterator:
                    try:
                        message_data: dict = orjson.loads(message.body)
                        yield ProcessableEvent(
                            ControllableMessage(
                                data=message_data,
                                control=RabbitMQQueueControlInterface(message, message_data, self, queue_name),
                            )
                        )
                    except Exception as e:
                        self.logger.error(
                            "Exception while parsing message body",
                            extra={"message_body": message.body, "error": e},
                        )
                        await message.reject(True)

    async def publish(self, queue_name: str, message: dict, delay: timedelta = timedelta()) -> None:
        if delay == timedelta():
            await self._publish_immediate(queue_name, message)
        else:
            await self._publish_delayed(queue_name, message, delay)

    @asynccontextmanager
    async def _channel(self) -> AsyncGenerator[AbstractChannel, None]:
        connection = await aio_pika.connect_robust(url=self._broker_url)
        async with connection:
            yield await connection.channel()

    async def _declare_queue(self, channel: AbstractChannel, queue_name: str) -> AbstractQueue:
        return await channel.declare_queue(
            queue_name,
            durable=True,
            exclusive=False,
            auto_delete=False,
        )

    async def _publish_immediate(self, queue_name: str, message: dict) -> None:
        async with self._channel() as channel:
            await self._declare_queue(channel, queue_name)

            await channel.default_exchange.publish(
                aio_pika.Message(
                    orjson.dumps(message),
                    content_type="application/json",
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                ),
                queue_name,
                mandatory=True,
            )

    async def _publish_delayed(self, queue_name: str, message: dict, delay: timedelta = timedelta()) -> None:
        async with self._channel() as channel:
            delay_queue_name = f"{queue_name}-delay"

            await self._declare_delay_queue(channel, delay_queue_name, queue_name)

            await channel.default_exchange.publish(
                aio_pika.Message(
                    orjson.dumps(message),
                    content_type="application/json",
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                    expiration=delay,
                ),
                delay_queue_name,
                mandatory=True,
            )

    async def _declare_delay_queue(
        self,
        channel: AbstractChannel,
        delay_queue_name: str,
        orig_queue_name: str,
    ) -> None:
        orig_queue = await self._declare_queue(channel, orig_queue_name)

        args: pamqp.common.Arguments = {
            "x-dead-letter-exchange": "dlx-exchange",
            "x-dead-letter-routing-key": orig_queue_name,
        }
        await channel.declare_queue(
            delay_queue_name,
            durable=True,
            exclusive=False,
            auto_delete=False,
            arguments=args,
        )

        await orig_queue.bind(
            await channel.declare_exchange("dlx-exchange", aio_pika.ExchangeType.DIRECT, durable=True),
        )
