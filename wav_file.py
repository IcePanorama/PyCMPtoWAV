from cmp.file import CMPFile
from io import BufferedWriter
import logging
from typing import List


class WaveformAudioFile:
    """
        Output is a signed, 24-bit PCM WAV.
        See: https://en.wikipedia.org/wiki/WAV
    """
    _BYTE_ORDER: str = "little"
    # _SAMPLE_RATE_HZ: int = 22050  # Harvester's wav files use this sample rate
    _BYTES_PER_SAMPLE: int = 4

    def __init__(self, cmp: CMPFile, filename: str = ""):
        self._sampling_rate: int = cmp.sampling_rate
        self._precision: int = cmp.precision
        self._waveform: List[int] = self._normalize_waveform(cmp.waveform)
        self._filename: str = filename if filename else self._create_filename(
            cmp.filename)

    def _create_filename(self, cmp_filename: str) -> str:
        """
            Removes the extension from `cmp_filename` and replaces it with
            `.wav`.
        """
        ext_idx: int = cmp_filename.find(".")
        if ext_idx == -1:
            return cmp_filename + ".wav"
        return cmp_filename[:ext_idx + 1] + "wav"

    def _normalize_waveform(self, waveform: List[int]) -> List[int]:
        """
            CMP decoded waveform is a signed 12-bit PCM "linear output sample"
            waveform however, we need this value to be normalized according to
            the range specified by `self._BYTES_PER_SAMPLE`.
        """
        UN_MAX: int = (2**self._precision) - 1
        HALF_UN_MAX: int = (UN_MAX + 1) >> 1
        work: List[float] = [((s + HALF_UN_MAX) / UN_MAX) for s in waveform]
        work = [max(0.0, min(s, 1.0)) for s in work]

        UW_MAX: int = (2**(self._BYTES_PER_SAMPLE << 3)) - 1
        HALF_UW_MAX: int = (UW_MAX + 1) >> 1
        return [int(s * UW_MAX - HALF_UW_MAX) for s in work]

    def _write_header(self, fptr: BufferedWriter):
        """ See: https://en.wikipedia.org/wiki/WAV#WAV_file_header """
        """ Master RIFF chunk """
        fptr.write(b"RIFF")
        fptr.seek(4, 1)  # skipping file size for now
        fptr.write(b"WAVE")

        """ Fmt chunk """
        fptr.write(b"fmt ")  # added space is intentional
        fptr.write(0x10.to_bytes(4, self._BYTE_ORDER))  # chunk bloc size
        fptr.write(0x1.to_bytes(2, self._BYTE_ORDER))  # PCM integer format
        # Mono audio (1 channel)
        fptr.write(0x1.to_bytes(2, self._BYTE_ORDER))
        fptr.write(self._sampling_rate.to_bytes(4, self._BYTE_ORDER))

        bpsamp: int = (self._BYTES_PER_SAMPLE << 3)  # bits per sample
        # bits per bloc = nChannels * bits per sample / 8
        bpb: int = (1 * bpsamp) >> 3
        # bytes per sec = freq * bytes per bloc
        bpsec: int = self._sampling_rate * bpb

        fptr.write(bpsec.to_bytes(4, self._BYTE_ORDER))
        fptr.write(bpb.to_bytes(2, self._BYTE_ORDER))
        fptr.write(bpsamp.to_bytes(2, self._BYTE_ORDER))

        """ Data chunk """
        fptr.write(b"data")
        fptr.seek(4, 1)  # skipping sampled data size for now

    def _write_size_data(self, fptr: BufferedWriter):
        """ Exports the header data skipped in `_write_header`. """
        file_size: int = fptr.tell()
        logging.debug(f"Output file size: {file_size} ({file_size:X})")
        fptr.seek(4, 0)
        rem: int = file_size - 8
        fptr.write((file_size - 8).to_bytes(4, self._BYTE_ORDER))

        """ Update sampled data size. """
        fptr.seek(0x28, 0)
        rem = file_size - fptr.tell() - 4
        logging.debug(f"Sampled data size: {rem} ({rem:X})")
        fptr.write(rem.to_bytes(4, self._BYTE_ORDER))

    def export(self):
        """ Writes the associated wav file to the current directory. """
        with open(self._filename, "wb", buffering=0) as fptr:
            self._write_header(fptr)

            sample: int
            for sample in self._waveform:
                fptr.write(sample.to_bytes(self._BYTES_PER_SAMPLE,
                           self._BYTE_ORDER, signed=True))

            self._write_size_data(fptr)
