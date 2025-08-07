import logging
from cmp.step_size_lookup import StepSizeLookup
from typing import List


class CMPFile:
    """
        Harvester's ADPCM sound files, used for music and voice lines.
        See: https://en.wikipedia.org/wiki/Dialogic_ADPCM
        See: https://people.cs.ksu.edu/~tim/vox/dialogic_adpcm.pdf
    """

    def __init__(self, filename: str):
        logging.info(f"Creating CMP object from file: {filename}")
        self._filename: str = filename
        self._size: int  # Size of raw ADPCM data in bytes
        self._sampling_rate: int  # in Hz
        self._samples: List[int]  # 4-bit ADPCM samples
        self._waveform: List[int]  # 12-bit PCM waveform

        logging.debug("Reading data from file...")
        raw_data: bytes
        with open(self._filename, "rb") as fptr:
            raw_data = fptr.read()

        logging.debug("Verifying file signature...")
        sig: str = "".join(chr(c) for c in raw_data[:4])
        raw_data = raw_data[4:]
        if (sig != "FCMP"):
            raise RuntimeError(f"'{filename}' is not a CMP file "
                               + f"(file signature: `{sig:4}`).")

        def le_bytes_to_int(b: List[int]) -> int:
            """
                Converts list of 4 bytes into a 32-bit int, treating the data
                as being little-endian. Receiving a list less than 4 in length
                is treated as an unhandled exception.
            """
            assert (len(b) == 4)
            return b[0] | (b[1] << 8) | (b[2] << 16) | (b[3] << 24)

        self._size = le_bytes_to_int(raw_data[:4])
        raw_data = raw_data[4:]
        logging.debug(f"Raw ADPCM size (B): {self._size} (0x{self._size:08X})")

        self._sampling_rate = le_bytes_to_int(raw_data[:4])
        raw_data = raw_data[4:]
        logging.debug(f"Sampling rate (Hz): {self._sampling_rate}")

        self._extract_samples(raw_data)
        self._decode_waveform()

    @property
    def filename(self) -> str:
        return self._filename

    @property
    def waveform(self) -> [int]:
        """
            Signed 12-bit PCM "linear output sample" waveform.
        """
        return self._waveform

    def _extract_samples(self, data: bytes) -> None:
        """
            Extracts ADPCM sample data from raw binary data.
            See: "Dialogic ADPCM Algorithm", pg. 3
        """
        self._samples = []
        logging.debug("Extracting ADPCM samples from raw binary data...")
        b: int
        for b in data:
            curr: [int] = [(b & 0xF0) >> 4, b & 0xF]
            self._samples.extend(curr)

    def _decode_waveform(self) -> None:
        logging.debug("Decoding PCM waveform...")

        self._waveform = [0]
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

            curr: int = self._waveform[-1] + diff
            curr = max(-2**11, min(curr, (2**11) - 1))
            self._waveform.append(curr)

        self._waveform = self._waveform[1:]  # skip filler byte
