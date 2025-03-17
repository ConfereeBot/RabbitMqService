import asyncio
from enum import StrEnum

import aiormq
from aiormq.abc import AbstractConnection
from pamqp.commands import Basic

connection: AbstractConnection = None


async def get_connection() -> AbstractConnection:
    global connection
    if connection and not connection.is_closed:
        return connection
    connection = await aiormq.connect("amqp://admin:adm1n@localhost/")
    return connection


class Res(StrEnum):
    STARTED = "started"
    ERROR = "error"


class Command(StrEnum):
    STOP = "stop"


async def schedule_task(link: str, in_secs: int):
    print(f"Scheduled new task ({link}) in {in_secs} sec")
    connection = await get_connection()
    channel = await connection.channel()
    await channel.basic_publish(
        body=link.encode(),
        exchange="conferee_direct",
        routing_key="gmeet_schedule",
        properties=Basic.Properties(expiration=str(in_secs * 1000)),
    )


async def manage_active_task(command: Command):
    print(f"Manage active task: <{command}>")
    connection = await get_connection()
    channel = await connection.channel()
    await channel.basic_publish(
        body=command.encode(), exchange="conferee_direct", routing_key="gmeet_manage"
    )


async def handle_responses(message: aiormq.abc.DeliveredMessage):
    print(f"Received: {message.body.decode()}")
    await message.channel.basic_ack(delivery_tag=message.delivery.delivery_tag)


async def start_listening():
    print("Starting listening to queues...")
    connection = await get_connection()
    async with connection as conn:
        channel = await conn.channel()
        reses = channel.basic_consume(
            queue="gmeet_res", consumer_callback=handle_responses
        )
        await asyncio.gather(reses)
        print("Listeners are ready!")
        await asyncio.Future()
    print("Stopped listening to queues.")


async def decline_task(link: str):
    connection = await get_connection()
    channel = await connection.channel()
    while True:
        message = await channel.basic_get("gmeet_schedule")
        body = message.body.decode()
        if not body:
            break
        if body == link:
            print(f"Task ({link}) canceled.")
            await message.channel.basic_ack(delivery_tag=message.delivery.delivery_tag)


async def main():
    task1 = asyncio.create_task(start_listening())  # Запуск прослушивания очередей
    # task2 = asyncio.create_task(schedule_task("test 1", 30))
    # task3 = asyncio.create_task(schedule_task("test 2", 15))
    # await asyncio.gather(task2, task3)
    # await asyncio.sleep(5)
    # await decline_task("test 1")

if __name__ == "__main__":
    print("Started producer")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Interrupted")
