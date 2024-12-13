from enum import Enum
from typing import final


@final
class CleanCountMode(Enum):
    """TODO"""

    NEVER = 0
    FIRST_ONLY = 1
    BETWEEN_ONLY = 2
    EACH = 3
    UNKNOWN = 238
