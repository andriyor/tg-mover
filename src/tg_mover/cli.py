"""Move messages from one Telegram channel to another without the "Forwarded from" header.

Each message is copied to dest, then deleted from source (only if the copy succeeded).
If MATCH_REGEX is set, only messages whose text matches it (case-insensitive) are moved;
otherwise all messages are moved.

Setup:  put TG_API_ID / TG_API_HASH (and optionally MATCH_REGEX) in .env
        # https://my.telegram.org -> API development tools
Usage:  uv run --env-file .env tg-mover @source @dest
First run asks for phone + login code and saves tg_mover.session (keep it private).
"""
import asyncio
import os
import random
import re
import sys

from telethon import TelegramClient
from telethon.errors import FloodWaitError


# random pause (seconds) after each moved message; human-like pace keeps the account safe
DELAY = (2, 5)


def matches(text, pattern):
    # msg.text is markdown, so hidden links ([label](url)) are matched too
    return pattern is None or bool(pattern.search(text or ""))


async def retry(coro_fn):
    """Run coro_fn, waiting out Telegram flood limits."""
    while True:
        try:
            return await coro_fn()
        except FloodWaitError as e:
            print(f"flood wait {e.seconds}s", file=sys.stderr)
            await asyncio.sleep(e.seconds + 1)


async def main(source, dest, pattern):
    async with TelegramClient("tg_mover", int(os.environ["TG_API_ID"]), os.environ["TG_API_HASH"]) as client:
        await client.get_dialogs()  # caches your chats so numeric ids of private channels resolve
        src = await client.get_entity(source)
        dst = await client.get_entity(dest)
        count = 0
        async for msg in client.iter_messages(src, reverse=True):
            if msg.action or not matches(msg.text, pattern):  # others stay in source untouched
                continue
            try:
                await retry(lambda: client.send_message(dst, msg))  # copy = no sender header
            except Exception as e:
                print(f"#{msg.id} skipped: {e}", file=sys.stderr)
                await asyncio.sleep(random.uniform(*DELAY))
                continue  # never delete what wasn't copied
            try:
                await retry(lambda: client.delete_messages(src, msg.id))
            except Exception as e:
                print(f"#{msg.id} copied but not deleted: {e}", file=sys.stderr)
            count += 1
            print(f"#{msg.id} moved ({count})")
            await asyncio.sleep(random.uniform(*DELAY))
        print(f"moved {count} message(s)")


def run():
    # numeric ids like -1001234567890 must be ints for get_entity
    args = [int(a) if a.lstrip("-").isdigit() else a for a in sys.argv[1:]]
    if len(args) != 2:
        sys.exit("usage: uv run --env-file .env tg-mover <source> <dest>")
    regex = os.environ.get("MATCH_REGEX")
    pattern = re.compile(regex, re.I) if regex else None  # bad regex fails here, before touching anything
    print(f"filter: {regex}" if pattern else "filter: none, moving ALL messages")
    asyncio.run(main(*args, pattern))


if __name__ == "__main__":
    run()
