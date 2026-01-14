from typing import Any

from loguru import logger
from numpy import argmax, argsort, array, concatenate, dtype, ndarray
from overrides import override

from horiba_sdk.core.stitching.spectra_stitch import SpectraStitch


class YDisplacementSpectraStitch(SpectraStitch):
    """Stiches a list of spectra using a linear model"""

    def __init__(self, spectra_list: list[list[list[float]]], y_displacement_count: int) -> None:
        """Constructs a linear stitch of spectra.

        .. warning:: The spectra in the list must overlap

        Parameters
            spectra_list : list[list[list[float]]] list of spectra to stitch in the form [[x1_values, y1_values],
            [x2_values, y2_values], etc].
            y_displacement_count : int The amount of displacement in the y direction for the second spectrum
        """
        self._y_displacement_count = y_displacement_count
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
        new_stitch = YDisplacementSpectraStitch([self.stitched_spectra(), other_stitch.stitched_spectra()])
        return new_stitch

    @override
    def stitched_spectra(self) -> Any:
        """Returns the raw data of the stitched spectra.

        Returns:
            Any: The stitched spectra.
        """
        return self._stitched_spectrum

    def _stitch_spectra(self, spectrum1: list[list[float]], spectrum2: list[list[float]]) -> list[list[float]]:
        # Adds a common offset to intensity values on the second spectrum.
        # Then performs a simple stitch always keeping the values from the first spectrum in the overlap region.
        # This stitching method can handle both spectra and images (2D arrays).
        fx1, fy1 = spectrum1
        fx2, fy2 = spectrum2

        # Convert to numpy arrays.
        x1: ndarray[Any, dtype[Any]] = array(fx1)
        x2: ndarray[Any, dtype[Any]] = array(fx2)
        y1: ndarray[Any, dtype[Any]] = array(fy1)
        y2: ndarray[Any, dtype[Any]] = array(fy2)
        
        # Sort spectra while maintaining x-y correspondence.
        sort1 = argsort(x1)
        sort2 = argsort(x2)

        # Create sorted views of both arrays. Also handles 2D arrays of intensity values for images.
        x1_sorted = x1[sort1]
        y1_sorted = array([y1i[sort1] for y1i in y1])
        x2_sorted = x2[sort2]
        # y2_sorted = array([y2i[sort2] for y2i in y2])

        # Adds offset to the second spectrum's intensity values.
        y2_displaced = y2 + self._y_displacement_count

        # Concatenates the spectra if there is no overlap.
        if x1_sorted[-1] < x2_sorted[0]:
            logger.error(f'No overlap between two spectra: {spectrum1}, {spectrum2}')
            return [concatenate([x1_sorted, x2_sorted]).tolist(), 
                    concatenate([y1_sorted, y2_displaced], axis=1).tolist()]
        
        # Finds the index of the smallest element in the second spectrum.
        # that is greater than the last element in the first spectrum.
        overlap_end_idx = argmax(x2_sorted > x1_sorted[-1])

        # Trims x2_sorted and y2_sorted to only include elements after the overlap. 
        # Also handles 2D arrays of intensity values for images.
        x2_after_overlap = x2_sorted[overlap_end_idx:]
        y2_after_overlap = y2_displaced[:, overlap_end_idx:]

        # Concatenate the spectra. Also handles 2D arrays for images.
        x_stitched = concatenate([x1_sorted, x2_after_overlap])
        y_stitched = concatenate([y1_sorted, y2_after_overlap],axis=1)

        return [x_stitched.tolist(), y_stitched.tolist()]
