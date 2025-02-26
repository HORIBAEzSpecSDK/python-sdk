from typing import Any, List

from loguru import logger
from numpy import array, concatenate, dtype, ndarray
from overrides import override

from horiba_sdk.core.stitching.spectra_stitch import SpectraStitch


class SimpleCutSpectraStitch(SpectraStitch):
    """Stitches a list of spectra by always keeping the values from the next spectrum in the overlap region.

    .. warning:: Produces a stitched spectrum with stairs
    """

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
        new_stitch = SimpleCutSpectraStitch([self.stitched_spectra(), other_stitch.stitched_spectra()])
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

        mask2 = (x2 >= overlap_start) & (x2 <= overlap_end)

        x2_overlap = x2[mask2]
        y2_overlap = y2[mask2]

        x1_before_overlap = x1[x1 < overlap_start]
        y1_before_overlap = y1[x1 < overlap_start]

        x2_after_overlap = x2[x2 > overlap_end]
        y2_after_overlap = y2[x2 > overlap_end]

        x_stitched = concatenate([x1_before_overlap, x2_overlap, x2_after_overlap])
        y_stitched = concatenate([y1_before_overlap, y2_overlap, y2_after_overlap])

        return [x_stitched.tolist(), y_stitched.tolist()]
