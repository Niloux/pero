from pero.router import router
from pero.type import EventType, MessageType, SourceType
from pero.logger import get_log

_log = get_log()


@router.register(
    EventType.EVENT_MESSAGE, MessageType.MESSAGE_TEXT, SourceType.SOURCE_PRIVATE
)
def test(message):
    _log.info(f"handle_a_m1: {message}")
