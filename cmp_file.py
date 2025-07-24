import logging
import os


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

        raw_data: bytes
        logging.info(f"Creating CMP file from {filename}")
        with open(self._filename, "rb") as fptr:
            raw_data = fptr.read()

        self._process_data(raw_data)
        print(self._samples)

    def _process_data(self, data: bytes) -> None:
        """
            Creates sample data from raw binary data.
            See: "Dialogic ADPCM Algorithm", pg. 3
        """
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
