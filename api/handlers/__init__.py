

# fix for asyncio_loop.add_reader NotImplementedError in windows
# https://github.com/django/channels/issues/969#issuecomment-596746621
import asyncio
import sys
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())