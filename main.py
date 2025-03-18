import asyncio

import rabbitmq as mq


async def main():
    task1 = asyncio.create_task(mq.func.start_listening())
    task2 = asyncio.create_task(
        mq.func.schedule_task("https://meet.google.com/wsc-ywte-njv", 0)
    )
    # task2 = asyncio.create_task(mq.func.manage_active_task(mq.responses.Req.TIME))
    # task2 = asyncio.create_task(mq.func.manage_active_task(mq.responses.Req.SCREENSHOT))
    await asyncio.gather(task1, task2)


if __name__ == "__main__":
    print("Emulate producer")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Interrupted")
