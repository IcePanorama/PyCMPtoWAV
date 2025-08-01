from typing import List


class StepSizeLookup:
    """
        An interface for looking up CPM step sizes.
        See: https://people.cs.ksu.edu/~tim/vox/dialogic_adpcm.pdf, pg. 6
    """
    # Used to index into our adjustment factor lookup table. "Values greater
    # than 3 will increase the size step. Values less than 4 decrease the step
    # size."
    _ADJUST_FACT: List[int] = [-1, -1, -1, -1, 2, 4, 6, 8]
    _STEP_SIZES: List[int] = [
        16, 17, 19, 21, 23, 25, 28, 31, 34, 37, 41, 45, 50, 55, 60, 66, 73, 80,
        88, 97, 107, 118, 130, 143, 157, 173, 190, 209, 230, 253, 279, 307,
        337, 371, 408, 449, 494, 544, 598, 658, 724, 796, 876, 963, 1060, 1166,
        1282, 1411, 1552
    ]
    _NUM_STEP_SIZES: int = len(_STEP_SIZES)
    _curr_step_size_idx: int = 0

    @staticmethod
    def get_step_size(sample: int) -> int:
        """
            Returns the current step size from the lookup table given `sample`.
        """
        StepSizeLookup._curr_step_size_idx += \
            StepSizeLookup._ADJUST_FACT[sample & 7]
        StepSizeLookup._curr_step_size_idx = \
            max(0,
                min(StepSizeLookup._curr_step_size_idx,
                    StepSizeLookup._NUM_STEP_SIZES - 1
                    )
                )

        return StepSizeLookup._STEP_SIZES[StepSizeLookup._curr_step_size_idx]
