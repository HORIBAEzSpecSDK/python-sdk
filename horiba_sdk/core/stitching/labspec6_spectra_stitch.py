from typing import Any, List

from loguru import logger
from numpy import array, concatenate, dtype, ndarray
from overrides import override

from horiba_sdk.core.stitching.spectra_stitch import SpectraStitch


class LabSpec6SpectraStitch(SpectraStitch):
    """Stitches a list of spectra using a weighted average as in LabSpec6"""

    def __init__(self, spectra_list: List[List[List[float]]]) -> None:
        """Constructs a linear stitch of spectra.

        .. warning:: The spectra in the list must overlap

        Parameters
            spectra_list : List[List[List[float]]] List of spectra to stitch in the form [[x1_values, y1_values],
            [x2_values, y2_values], etc].
        """
        stitched_spectrum = spectra_list[0]

        for i in range(1, len(spectra_list)):
            stitched_spectrum = self._stitch_spectra(stitched_spectrum, spectra_list[i])

        self._stitched_spectrum: List[List[float]] = stitched_spectrum

    @override
    def stitch_with(self, other_stitch: SpectraStitch) -> SpectraStitch:
        """Stitches this stitch with another stitch.

        Parameters
            other_stitch : SpectraStitch The other stitch to stitch with

        Returns:
            SpectraStitch: The stitched spectra.
        """
        new_stitch = LabSpec6SpectraStitch([self.stitched_spectra(), other_stitch.stitched_spectra()])
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

        mask1 = (x1 >= overlap_start) & (x1 <= overlap_end)
        mask2 = (x2 >= overlap_start) & (x2 <= overlap_end)

        x1_overlap = x1[mask1]
        y1_overlap = y1[mask1]

        x2_overlap = x2[mask2]
        y2_overlap = y2[mask2]

        A = (x1_overlap - overlap_start) / (overlap_end - overlap_start)
        B = (overlap_end - x2_overlap) / (overlap_end - overlap_start)

        y_stitched = (y1_overlap * A + y2_overlap * B) / (A + B)

        x_before = x1[x1 < overlap_start]
        y_before = y1[x1 < overlap_start]

        x_after = x2[x2 > overlap_end]
        y_after = y2[x2 > overlap_end]

        x_stitched = concatenate([x_before, x1_overlap, x_after])
        y_stitched_final = concatenate([y_before, y_stitched, y_after])

        return [x_stitched.tolist(), y_stitched_final.tolist()]
