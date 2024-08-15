from abc import ABC, abstractmethod
from typing import Any


class SpectraStitch(ABC):
    """Stitches multiple spectra into a single spectrum."""

    @abstractmethod
    def stitch_with(self, other_stitch: 'SpectraStitch') -> 'SpectraStitch':
        """Stitches this stitch with another stitch."""
        pass

    @abstractmethod
    def stitched_spectra(self) -> Any:
        """Returns the raw data of the stitched spectra."""
        pass
