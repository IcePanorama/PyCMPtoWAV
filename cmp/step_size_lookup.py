class StepSizeLookup:
    """
        An interface for looking up CPM step sizes.
        See: https://people.cs.ksu.edu/~tim/vox/dialogic_adpcm.pdf, pg. 6
    """
    # Used to index into our adjustment factor lookup table. "Values greater
    # than 3 will increase the size step. Values less than 4 decrease the step
    # size."
    _ADJUST_FACT_LOOKUP_KEY: {int, int} = {
        7: 8,
        6: 6,
        5: 4,
        4: 2,
        3: -1,
        2: -1,
        1: -1,
        0: -1
    }

    _STEP_SIZES: [int] = [
        16, 17, 19, 21, 23, 25, 28, 31, 34, 37, 41, 45, 50, 55, 60, 66, 73, 80,
        88, 97, 107, 118, 130, 143, 157, 173, 190, 209, 230, 253, 279, 307,
        337, 371, 408, 449, 494, 544, 598, 658, 724, 796, 876, 963, 1060, 1166,
        1282, 1411, 1552
    ]
    _curr_step_size_idx: int = 0

    @staticmethod
    def get_key(sample: int) -> int:
        """
            Given a 4-bit signed sample, this returns the adjusment factor for
            indexing the lookup table.
        """
        return StepSizeLookup._ADJUST_FACT_LOOKUP_KEY[sample & 7]

    @staticmethod
    def get_step_size(adj_fact: int) -> int:
        """
            Returns the current step size from the lookup table given an
            adjustment factor, `adj_fact`.
        """
        StepSizeLookup._curr_step_size_idx += adj_fact
        StepSizeLookup._curr_step_size_idx %= len(StepSizeLookup._STEP_SIZES)
        return StepSizeLookup._STEP_SIZES[StepSizeLookup._curr_step_size_idx]
