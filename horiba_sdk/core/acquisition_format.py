from enum import Enum
from typing import final


@final
class AcquisitionFormat(Enum):
    """Formats for the acquisition.

    Attributes:
        SPECTRA: X axis in nm, Y axis in counts
        IMAGE: X axis in pixels, Y axis in counts
        CROP: TBD
        FAST_KINETICS: TBD

    """

    SPECTRA_IMAGE = 1
    CROP = 2
    FAST_KINETICS = 3
