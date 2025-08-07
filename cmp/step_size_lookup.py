from typing import List


class StepSizeLookup:
    """ An interface for quickly looking up CMP (IMA) ADPCM step sizes. """
    _ADJUST_FACT: List[int] = [-1, -1, -1, -1, 2, 4, 6, 8]
    """
    # NOTE: Might need still this if we find any files whose precision isn't
    # 16-bits. These values are for Dialogic/ADPCM files.
    # See: https://people.cs.ksu.edu/~tim/vox/dialogic_adpcm.pdf, pg. 6
    # See: https://wiki.multimedia.cx/index.php/Dialogic_IMA_ADPCM
    _STEP_SIZES: List[int] = [
        16, 17, 19, 21, 23, 25, 28, 31, 34, 37, 41, 45, 50, 55, 60, 66, 73, 80,
        88, 97, 107, 118, 130, 143, 157, 173, 190, 209, 230, 253, 279, 307,
        337, 371, 408, 449, 494, 544, 598, 658, 724, 796, 876, 963, 1060, 1166,
        1282, 1411, 1552
    ]
    """
    # See: https://wiki.multimedia.cx/index.php/IMA_ADPCM#Decoding_Tables
    _STEP_SIZES: List[int] = [
        7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 19, 21, 23, 25, 28, 31, 34, 37,
        41, 45, 50, 55, 60, 66, 73, 80, 88, 97, 107, 118, 130, 143, 157, 173,
        190, 209, 230, 253, 279, 307, 337, 371, 408, 449, 494, 544, 598, 658,
        724, 796, 876, 963, 1060, 1166, 1282, 1411, 1552, 1707, 1878, 2066,
        2272, 2499, 2749, 3024, 3327, 3660, 4026, 4428, 4871, 5358, 5894, 6484,
        7132, 7845, 8630, 9493, 10442, 11487, 12635, 13899, 15289, 16818,
        18500, 20350, 22385, 24623, 27086, 29794, 32767
    ]
    _NUM_STEP_SIZES: int = len(_STEP_SIZES)

    def __init__(self):
        self._curr_step_size_idx: int = 0

    def get_step_size(self, sample: int) -> int:
        """
            Returns the current step size from the lookup table given `sample`.
        """
        old: int = self._curr_step_size_idx
        self._curr_step_size_idx += StepSizeLookup._ADJUST_FACT[sample & 7]
        self._curr_step_size_idx = \
            max(
                0,
                min(
                    self._curr_step_size_idx,
                    StepSizeLookup._NUM_STEP_SIZES - 1
                )
            )

        return StepSizeLookup._STEP_SIZES[old]
