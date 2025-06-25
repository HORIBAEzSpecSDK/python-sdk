from typing import Any, List

from loguru import logger
from numpy import array, concatenate, dtype, ndarray, interp
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
        # Grab x and y values from the spectra
        fx1, fy1 = spectrum1
        fx2, fy2 = spectrum2

        # Convert to numpy arrays
        x1: ndarray[Any, dtype[Any]] = array(fx1)
        x2: ndarray[Any, dtype[Any]] = array(fx2)
        y1: ndarray[Any, dtype[Any]] = array(fy1)
        y2: ndarray[Any, dtype[Any]] = array(fy2)

        # Sort spectra while maintaining x-y correspondence
        sort1 = argsort(x1)
        sort2 = argsort(x2)

        # Create sorted views of both arrays
        x1_sorted = x1[sort1]
        y1_sorted = y1[sort1]
        x2_sorted = x2[sort2]
        y2_sorted = y2[sort2]

        # Raises exception if there is no overlap between the two spectra
        if x1_sorted[-1] <= x2_sorted[0]:
            logger.error(f'No overlap between two spectra: {spectrum1}, {spectrum2}')
            raise Exception('No overlapping region between spectra')
        
        # Define mask that will split the first spectrum into overlapping and non-overlapping regions
        mask1 = (x1_sorted >= x2_sorted[0])
        
        # Apply mask to get overlapping region
        x1_overlap = x1_sorted[mask1]
        y1_overlap = y1_sorted[mask1]

        # Linearly interpolate y2 values at the x1_overlap points
        y2_interpolated = interp(x1_overlap, x2_sorted, y2_sorted)

        # Find the largest x value in the first spectrum that is less than the smallest x value in the second spectrum
        overlap_start = max(x1_sorted[~mask1])

        # Find the smallest x value in the second spectrum that is greater than the largest x value in the first spectrum
        mask2 = (x2_sorted >= x1_sorted[-1])
        overlap_end = min(x2_sorted[mask2])

        # Create new overlap region via a weighted average of the y1 and interpolated y2 values
        y_stitched = (y1_overlap * (overlap_end - x1_overlap) + y2_interpolated * (x1_overlap - overlap_start)) / (overlap_end - overlap_start)
 
        y_before = y1[~mask1]

        x_after = x2_sorted[mask2]
        y_after = y2_sorted[mask2]

        x_stitched = concatenate([x1_sorted, x_after])
        y_stitched_final = concatenate([y_before, y_stitched, y_after])

        return [x_stitched.tolist(), y_stitched_final.tolist()]
