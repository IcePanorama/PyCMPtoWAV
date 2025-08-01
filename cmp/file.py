import logging
import os
from cmp.step_size_lookup import StepSizeLookup
from typing import List


class CMPFile:
    """
        Harvester's 22.5 kHz Dialogic (VOX) ADPCM sound files, used for music
        and voice lines.
        See: https://en.wikipedia.org/wiki/Dialogic_ADPCM
        See: https://people.cs.ksu.edu/~tim/vox/dialogic_adpcm.pdf
    """

    def __init__(self, filename: str):
        self._filename: str = filename
        self._size_bytes: int = os.path.getsize(self._filename)
        self._samples: List[int] = []
        self._waveform: List[int] = [0]

        raw_data: bytes
        logging.info(f"Creating CMP file from {filename}")
        with open(self._filename, "rb") as fptr:
            raw_data = fptr.read()

        self._process_data(raw_data)
        self._decode_waveform()

    @property
    def filename(self) -> str:
        return self._filename

    @property
    def waveform(self) -> [int]:
        return self._waveform

    def _process_data(self, data: bytes) -> None:
        """
            Creates sample data from raw binary data.
            See: "Dialogic ADPCM Algorithm", pg. 3
        """
        logging.info("Processing raw binary data.")
        b: int
        for b in data:
            curr: [int] = [(b & 0xF0) >> 4, b & 0xF]
            self._samples.extend(curr)

    def _decode_waveform(self) -> None:
        logging.info("Decoding waveform.")

        s: int
        for s in self._samples:
            ss: int = StepSizeLookup.get_step_size(s)
            bits: List[int] = [
                (s & 1),
                (s & 2) >> 1,
                (s & 4) >> 2,
                (s & 8) >> 3
            ]

            # See: "Dialogic ADPCM Algorithm", pg. 5
            diff: int = ss * bits[2]
            diff += (ss >> 1) * bits[1]
            diff += (ss >> 2) * bits[0]
            diff += (ss >> 3)
            diff *= -1 if bits[3] == 1 else 1
            self._waveform.append(
                max(
                    -2048,
                    min(
                        self._waveform[-1] + diff,
                        2048
                    )
                )
            )

        self._waveform = self._waveform[1:]  # skip filler byte
