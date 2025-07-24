import logging
import os
from cmp.step_size_lookup import StepSizeLookup


class CMPFile:
    """
        Harvester's 22.5 kHz Dialogic (VOX) ADPCM sound files, used for music
        and voice lines.
        See: https://en.wikipedia.org/wiki/Dialogic_ADPCM
        See: https://people.cs.ksu.edu/~tim/vox/dialogic_adpcm.pdf
    """
    _SAMPLE_RATE_HERTZ: int = 22500

    def __init__(self, filename: str):
        self._filename: str = filename
        self._size_bytes: int = os.path.getsize(self._filename)
        self._samples: [int] = []
        self._waveform: [int] = [0]

        raw_data: bytes
        logging.info(f"Creating CMP file from {filename}")
        with open(self._filename, "rb") as fptr:
            raw_data = fptr.read()

        self._process_data(raw_data)
        self._decode_waveform()

    def _process_data(self, data: bytes) -> None:
        """
            Creates sample data from raw binary data.
            See: "Dialogic ADPCM Algorithm", pg. 3
        """
        logging.info("Processing raw binary data.")
        b: int
        for b in data:
            curr: [int] = [(b & 0xFF) >> 4, b & 0xF]
            curr = [self._sample_to_signed_int(s) for s in curr]
            self._samples.extend(curr)

    def _sample_to_signed_int(self, sample: int) -> int:
        """
            Converts unsigned 4-bit int to a signed one.
            See: "Dialogic ADPCM Algorithm", pg. 3
        """
        out: int = sample & 7  # 3 LSBs = magnitude
        sign: int = (sample & 8) >> 3  # MSB = sign
        return out if sign == 0 else -out

    def _decode_waveform(self) -> None:
        logging.info("Decoding waveform.")

        s: int
        for s in self._samples:
            ss: int = StepSizeLookup.get_step_size(StepSizeLookup.get_key(s))
            bits: [int] = [s & 1, s & 2, s & 4, s & 8]

            # See: "Dialogic ADPCM Algorithm", pg. 5
            diff: int = ss * bits[2]
            diff += (ss >> 1) * bits[1]
            diff += (ss >> 2) * bits[0]
            diff += (ss >> 3)
            diff *= -1 if bits[3] == 1 else 1
            self._waveform.append(self._waveform[-1] + diff)
            logging.debug(f"Curr waveform val: {self._waveform[-1]}")
