from typing import Any, List

from loguru import logger
from numpy import argsort, array, concatenate, dtype, interp, ndarray
from overrides import override

from horiba_sdk.core.stitching.spectra_stitch import SpectraStitch


class LinearSpectraStitch(SpectraStitch):
    """Stitches a list of spectra using a linear model"""

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
        new_stitch = LinearSpectraStitch([self.stitched_spectra(), other_stitch.stitched_spectra()])
        return new_stitch

    @override
    def stitched_spectra(self) -> Any:
        """Returns the raw data of the stitched spectra.

        Returns:
            Any: The stitched spectra.
        """
        return self._stitched_spectrum

    def _stitch_spectra(self, spectrum1: List[List[float]], spectrum2: List[List[float]]) -> List[List[float]]:
        fx1 = spectrum1[0]
        fy1 = spectrum1[1][0]
        fx2 = spectrum2[0]
        fy2 = spectrum2[1][0]

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

        # Calculate true overlap region
        x1_min, x1_max = x1_sorted[0], x1_sorted[-1]
        x2_min, x2_max = x2_sorted[0], x2_sorted[-1]

        overlap_start = max(x1_min, x2_min)
        overlap_end = min(x1_max, x2_max)

        logger.debug(f"Spectrum 1 range: {x1_min} to {x1_max}")
        logger.debug(f"Spectrum 2 range: {x2_min} to {x2_max}")
        logger.debug(f"Overlap region: {overlap_start} to {overlap_end}")

        if overlap_start >= overlap_end:
            logger.error(f'No overlap between spectra: [{x1_min}, {x1_max}] and [{x2_min}, {x2_max}]')
            raise Exception('No overlapping region between spectra')

        # Create masks for overlapping regions using sorted arrays
        mask1 = (x1_sorted >= overlap_start) & (x1_sorted <= overlap_end)
        mask2 = (x2_sorted >= overlap_start) & (x2_sorted <= overlap_end)

        # Interpolate second spectrum onto first spectrum's x points in overlap region
        y2_interp = interp(x1_sorted[mask1], x2_sorted[mask2], y2_sorted[mask2])

        # Average the overlapping region
        y_combined_overlap = (y1_sorted[mask1] + y2_interp) / 2

        # Combine non-overlapping and overlapping regions
        x_combined = concatenate((x1_sorted[~mask1], x1_sorted[mask1], x2_sorted[~mask2]))
        y_combined = concatenate((y1_sorted[~mask1], y_combined_overlap, y2_sorted[~mask2]))

        # Ensure final result is sorted
        sort_indices = argsort(x_combined)
        x_combined = x_combined[sort_indices]
        y_combined = y_combined[sort_indices]

        return [x_combined.tolist(), [y_combined.tolist()]]
