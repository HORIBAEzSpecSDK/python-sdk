from enum import Enum
from typing import final


@final
class TimerResolution(Enum):
    """
    .. note:: The timer resolution value MICROSECONDS is not supported by all CCDs.
    """

    MILLISECONDS = 0
    MICROSECONDS = 1
    NOTHING_EVAL = 2
