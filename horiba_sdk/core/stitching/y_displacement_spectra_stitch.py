from typing import Any, List

from loguru import logger
from numpy import array, concatenate, dtype, ndarray
from overrides import override

from horiba_sdk.core.stitching.spectra_stitch import SpectraStitch


class YDisplacementSpectraStitch(SpectraStitch):
    """Stiches a list of spectra using a linear model"""

    def __init__(self, spectrum1: List[List[float]], spectrum2: List[List[float]], y_displacement_count: int) -> None:
        """Constructs a linear stitch of spectra.

        .. warning:: The spectra in the list must overlap

        Parameters
            spectra_list : List[List[List[float]]] List of spectra to stitch in the form [[x1_values, y1_values],
            [x2_values, y2_values], etc].
            y_displacement_count : int The amount of displacement in the y direction for the second spectrum
        """
        self._y_displacement_count = y_displacement_count
        stitched_spectrum = self._stitch_spectra(spectrum1, spectrum2)

        self._stitched_spectrum: List[List[float]] = stitched_spectrum

    @override
    def stitch_with(self, other_stitch: SpectraStitch) -> SpectraStitch:
        """Stitches this stitch with another stitch.

        Parameters
            other_stitch : SpectraStitch The other stitch to stitch with

        Returns:
            SpectraStitch: The stitched spectra.
        """
        new_stitch = YDisplacementSpectraStitch([self.stitched_spectra(), other_stitch.stitched_spectra()])
        return new_stitch

    @override
    def stitched_spectra(self) -> Any:
        """Returns the raw data of the stitched spectra.

        Returns:
            Any: The stitched spectra.
        """
        return self._stitched_spectrum

    def _stitch_spectra(self, spectrum1: List[List[float]], spectrum2: List[List[float]]) -> List[List[float]]:
        fx1, fy1 = spectrum1
        fx2, fy2 = spectrum2

        x1: ndarray[Any, dtype[Any]] = array(fx1)
        x2: ndarray[Any, dtype[Any]] = array(fx2)
        y1: ndarray[Any, dtype[Any]] = array(fy1)
        y2: ndarray[Any, dtype[Any]] = array(fy2)

        overlap_start = max(x1[0], x2[0])
        overlap_end = min(x1[-1], x2[-1])

        if overlap_start >= overlap_end:
            logger.error(f'No overlap between two spectra: {spectrum1}, {spectrum2}')
            raise Exception('No overlapping region between spectra')

        # Masks for overlapping region
        mask1 = (x1 >= overlap_start) & (x1 <= overlap_end)
        mask2 = (x2 >= overlap_start) & (x2 <= overlap_end)

        x1_overlap = x1[mask1]
        y1_overlap = y1[mask1]

        y2_displaced = y2 + self._y_displacement_count
        y2_overlap = y2_displaced[mask2]

        y_stitched_overlap = (y1_overlap + y2_overlap) / 2

        x1_before_overlap = x1[x1 < overlap_start]
        y1_before_overlap = y1[x1 < overlap_start]

        x2_after_overlap = x2[x2 > overlap_end]
        y2_after_overlap = y2_displaced[x2 > overlap_end]

        x_stitched = concatenate([x1_before_overlap, x1_overlap, x2_after_overlap])
        y_stitched = concatenate([y1_before_overlap, y_stitched_overlap, y2_after_overlap])

        return [x_stitched.tolist(), y_stitched.tolist()]
