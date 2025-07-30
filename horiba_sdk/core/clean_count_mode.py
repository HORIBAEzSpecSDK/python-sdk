from enum import Enum
from typing import final


@final
class CleanCountMode(Enum):
    """ccd_setCleanCount
    Sets the number of cleans to be performed according to the specified mode setting.

    0 = Never
    1 = First Only
    2 = Between Only
    3 = Each"""

    NEVER = 0
    FIRST_ONLY = 1
    BETWEEN_ONLY = 2
    EACH = 3
