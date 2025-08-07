import logging
from cmp.step_size_lookup import StepSizeLookup
from typing import List


class CMPFile:
    """
        Harvester's (IMA) ADPCM sound files, used for music and voice lines.
    """

    def __init__(self, filename: str):
        logging.info(f"Creating CMP object from CMP object: {filename}")
        self._filename: str = filename
        self._size: int  # Size of raw ADPCM data in bytes
        self._sampling_rate: int  # in Hz
        # Not 100% sure this is what this is, see note w/ assert below
        self._precision: int
        self._samples: List[int]  # Signed 4-bit ADPCM samples
        self._waveform: List[int]  # Signed 16-bit PCM waveform

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

        self._precision = raw_data[0] | (raw_data[1] << 8)
        logging.debug(f"Precision (b): {self._precision}")
        assert (self._precision == 16)  # Seems to always be 16?
        raw_data = raw_data[2:]

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

    @property
    def sampling_rate(self) -> int:
        """
            The sampling rate of the decoded PCM waveform, in hertz.
        """
        return self._sampling_rate

    @property
    def precision(self) -> int:
        """
            The precision of `self.waveform`, in bits.
        """
        return self._precision

    def _extract_samples(self, data: bytes) -> None:
        """
            Extracts ADPCM sample data from raw binary data.
        """
        self._samples = []
        logging.debug("Extracting ADPCM samples from raw binary data...")
        b: int
        for b in data:
            self._samples.extend([b & 0xF, (b & 0xF0) >> 4])

    def _decode_waveform(self) -> None:
        """
            Converts `self._samples` into a signed N-bit PCM waveform
            (`self._waveform`).
        """
        logging.debug("Decoding PCM waveform...")

        self._waveform = [0]  # default initial value
        bounds: int = 2**(self._precision - 1)  # bounds for clamping
        s: int
        for s in self._samples:
            ss: int = StepSizeLookup.get_step_size(s)
            bits: List[int] = [
                (s & 1),
                (s & 2) >> 1,
                (s & 4) >> 2,
                (s & 8) >> 3
            ]

            # See: https://people.cs.ksu.edu/~tim/vox/dialogic_adpcm.pdf, pg. 5
            diff: int = ss * bits[2]
            diff += (ss >> 1) * bits[1]
            diff += (ss >> 2) * bits[0]
            diff += (ss >> 3)
            diff *= -1 if bits[3] == 1 else 1

            curr: int = self._waveform[-1] + diff
            curr = max(-bounds, min(curr, bounds - 1))
            self._waveform.append(curr)

        self._waveform = self._waveform[1:]  # skip filler byte
