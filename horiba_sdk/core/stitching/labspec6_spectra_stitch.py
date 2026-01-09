from typing import Any

from loguru import logger
from numpy import argmax, argmin, argsort, array, concatenate, dtype, ndarray
from overrides import override

from horiba_sdk.core.stitching.spectra_stitch import SpectraStitch


class LabSpec6SpectraStitch(SpectraStitch):
    """Stitches a list of spectra using a weighted average as in LabSpec6"""

    def __init__(self, spectra_list: list[list[list[float]]]) -> None:
        """Constructs a linear stitch of spectra.

        .. warning:: The spectra in the list must overlap

        Parameters
            spectra_list : list[list[list[float]]] list of spectra to stitch in the form [[x1_values, y1_values],
            [x2_values, y2_values], etc].
        """
        stitched_spectrum = spectra_list[0]

        for i in range(1, len(spectra_list)):
            stitched_spectrum = self._stitch_spectra(stitched_spectrum, spectra_list[i])

        self._stitched_spectrum: list[list[float]] = stitched_spectrum

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

    def _stitch_spectra(self, spectrum1: list[list[float]], spectrum2: list[list[float]]) -> list[list[float]]:
        # Sitches spectra using a weighted average in the overlap region.
        # This stitching method only works with spectra, not images.
        # If full CCD data is passed, only the first row is used.
        fx1 = spectrum1[0]
        fy1 = spectrum1[1][0]
        fx2 = spectrum2[0]
        fy2 = spectrum2[1][0]

        # Convert to numpy arrays.
        x1: ndarray[Any, dtype[Any]] = array(fx1)
        x2: ndarray[Any, dtype[Any]] = array(fx2)
        y1: ndarray[Any, dtype[Any]] = array(fy1)
        y2: ndarray[Any, dtype[Any]] = array(fy2)

        # Sort spectra while maintaining x-y correspondence.
        sort1 = argsort(x1)
        sort2 = argsort(x2)

        # Create sorted views of both arrays.
        x1_sorted = x1[sort1]
        y1_sorted = y1[sort1]
        x2_sorted = x2[sort2]
        y2_sorted = y2[sort2]

        # Concatenates the spectra if there is no overlap.
        if x1_sorted[-1] < x2_sorted[0]:
            logger.error(f'No overlap between two spectra: {spectrum1}, {spectrum2}')
            return [concatenate([x1_sorted, x2_sorted]).tolist(), [concatenate([y1_sorted, y2_sorted]).tolist()]]
        
        # Finds the index of the largest element in the first spectrum that is less than 
        # the first element in the second spectrum. 
        # Defines this as the start of the overlapping region.
        overlap_start_idx = argmax(x1_sorted >= x2_sorted[0]) - 1
        overlap_start = x1_sorted[overlap_start_idx]

        # Finds the index of the smallest element in the second spectrum that is greater than
        # the last element in the first spectrum. 
        # Defines this as the end of the overlapping region.
        overlap_end_idx = argmax(x2_sorted > x1_sorted[-1])
        overlap_end = x2_sorted[overlap_end_idx]

        # Weighted average of the overlapping region.
        y_overlap_weighted_average = []
        for i in range(overlap_start_idx + 1, len(x1_sorted)):
            idx = argmin(abs(x2_sorted - x1_sorted[i]))
            y_overlap_weighted_average.append((y1_sorted[i]*(overlap_end-x1_sorted[i])+
                                    y2_sorted[idx]*(x2_sorted[idx]-overlap_start)) / (overlap_end - overlap_start))

        x2_after = x2_sorted[overlap_end_idx:]
        y1_before = y1_sorted[:overlap_start_idx+1]
        y2_after = y2_sorted[overlap_end_idx:]

        # Combine non-overlapping and overlapping regions.
        x_combined = concatenate([x1_sorted, x2_after])
        y_combined = concatenate([y1_before, y_overlap_weighted_average, y2_after])

        return [x_combined.tolist(), [y_combined.tolist()]]
