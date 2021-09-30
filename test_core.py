import bot
import asyncio
import utils.test_helper as th
import pytest


@pytest.mark.asyncio
async def test_startup():
    # starts and stops the bot.
    await bot.start_loop(1)
    await asyncio.sleep(10)
    loop = asyncio.get_running_loop()
    loop.stop()
    loop.close()

    startup_logs = ["[Bot] Creating vote manager...",
                    "[Bot] Creating clocks...",
                    "[Bot] Creating input parser...",
                    "[Bot] Adding commands...",
                    "[Bot] Adding sfx commands...",
                    "[Bot] Starting bots...]"
    ]

    assert th.lines_exists_in_log(startup_logs)