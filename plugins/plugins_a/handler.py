from pero.logger import get_log
from pero.router import router
from pero.type import EventType, MessageType

_log = get_log()


@router.register(EventType.EVENT_MESSAGE, MessageType.MESSAGE_TEXT)
async def test(message):
    _log.info(f"handle_a_m1: {message}")
