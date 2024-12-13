from enum import Enum
from typing import final


@final
class TimerResolution(Enum):
    """Resolution for the timer for the acquisition time.

    .. note:: The timer resolution value MICROSECONDS is not supported by all CCDs.
    """

    MILLISECONDS = 0
    MICROSECONDS = 1
    NOTHING_EVAL = 2
