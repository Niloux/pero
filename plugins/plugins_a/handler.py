from pero.logger import get_log
from pero.router import MessageAdapter

_log = get_log()


@MessageAdapter.register_message("text")
async def test(message):
    _log.info(f"handle_a_m1: {message}")
