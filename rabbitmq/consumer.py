import asyncio
from enum import StrEnum

import aiormq
from aiormq.abc import AbstractChannel, AbstractConnection

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


async def some_func():
    await asyncio.sleep(100)


async def run_task(message: aiormq.abc.DeliveredMessage):
    print(f"Received: {message.body.decode()}")
    await message.channel.basic_ack(delivery_tag=message.delivery.delivery_tag)
    await answer_producer(message.channel, Res.STARTED)
    try:
        await some_func()
    except Exception as e:
        print(e)
        await answer_producer(message.channel, Res.ERROR)


async def answer_producer(channel: AbstractChannel, res: Res):
    await channel.basic_publish(
        body=res.encode(),
        exchange="conferee_direct",
        routing_key="gmeet_res",
    )


async def manage_task(message: aiormq.abc.DeliveredMessage):
    print(f"Received: {message.body.decode()}")
    await message.channel.basic_publish(
        exchange="conferee_direct", routing_key="gmeet_res", body="GOOD".encode()
    )
    await message.channel.basic_ack(delivery_tag=message.delivery.delivery_tag)


async def main():
    print("Starting listening to queues...")
    connection = await get_connection()
    print("Connect")
    async with connection as conn:
        channel = await conn.channel()
        q_tasks = channel.basic_consume(queue="gmeet_tasks", consumer_callback=run_task)
        q_manage = channel.basic_consume(
            queue="gmeet_manage", consumer_callback=manage_task
        )

        await asyncio.gather(q_tasks, q_manage)
        print("Listeners are ready!")
        await asyncio.Future()
    print("Stopped listening to queues.")


if __name__ == "__main__":
    print("Started consumer")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Interrupted")
