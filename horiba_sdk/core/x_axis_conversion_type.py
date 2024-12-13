from enum import Enum
from typing import final


@final
class XAxisConversionType(Enum):
    """
    Conversion types for the x axis of acquired data.

    Attributes:
        NONE: No conversion.
        FROM_CCD_FIRMWARE: CCD FIT parameters contained in the CCD firmware.
        FROM_ICL_SETTINGS_INI: Mono Wavelength parameters contained in the icl_settings.ini file
    """

    NONE = 0
    FROM_CCD_FIRMWARE = 1
    FROM_ICL_SETTINGS_INI = 2
