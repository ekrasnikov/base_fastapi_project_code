import di
import typer
from app.cli.commands.example import example
from app.cli.decorators.async_run import async_run
from app.settings import settings
from domain.events.broker import EventBroker
from domain.events.parser import EventParser
from domain.events.registry import EventHandlerRegistry

cli = typer.Typer()


@cli.command()
@async_run
async def listen_queue(
    queue: str = "etl",
) -> None:
    typer.echo(f"Started listen queue {queue}")

    handler_registry = EventHandlerRegistry([])
    broker = di.resolve(EventBroker)()
    event_parser = EventParser(handler_registry)

    async for broker_event in broker.listen(queue):
        async with broker_event.process() as message:
            event = event_parser.parse(message)
            await handler_registry.route(event)

    typer.echo(f"Finished listen queue {queue}")


@cli.command()
@async_run
async def task_worker(
    queue: str = settings.task_queue_name,
) -> None:
    typer.echo(f"Started listen task queue {queue}")

    handler_registry = EventHandlerRegistry([])
    broker = di.resolve(EventBroker)()
    event_parser = EventParser(handler_registry)

    async for broker_event in broker.listen(queue):
        async with broker_event.process() as message:
            event = event_parser.parse(message)
            await handler_registry.route_task(event)

    typer.echo(f"Finished listen task queue {queue}")


@cli.command()
@async_run
async def example_task() -> None:
    await example()
