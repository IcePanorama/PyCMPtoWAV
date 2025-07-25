from cmp.file import CMPFile
from io import BufferedWriter
import logging


class WaveformAudioFile:
    """
        Output is a signed, 24-bit PCM WAV.
        See: https://en.wikipedia.org/wiki/WAV
    """
    _BYTE_ORDER = "little"
    _SAMPLE_RATE_HZ: int = 22050  # Harvester's wav files use this sample rate
    _BYTES_PER_SAMPLE = 3

    def __init__(self, cmp: CMPFile, filename: str = ""):
        self._cmp = cmp
        self._filename: str
        if filename:
            self._filename = filename
        else:
            self._filename = self._create_filename(cmp.filename)

    def _create_filename(self, cmp_filename: str) -> str:
        ext_idx: int = cmp_filename.find(".")
        if ext_idx == -1:
            return cmp_filename + ".wav"
        name: str = cmp_filename[:ext_idx + 1] + "wav"
        return name

    def _write_header(self, fptr: BufferedWriter):
        """
            See: https://en.wikipedia.org/wiki/WAV#WAV_file_header
        """
        # bits per sample
        bpsamp: int = self._BYTES_PER_SAMPLE * 8
        # bits per bloc = nChannels * bits per sample / 8
        bpb: int = (1 * bpsamp) >> 3
        # bytes per sec = freq * bytes per bloc
        bpsec: int = self._SAMPLE_RATE_HZ * bpb

        """ Master RIFF chunk """
        fptr.write(b"RIFF")
        fptr.seek(4, 1)  # skipping file size for now
        fptr.write(b"WAVE")

        """ Fmt chunk """
        fptr.write(b"fmt ")  # added space is intentional
        # chunk bloc size
        fptr.write(0x10.to_bytes(4, self._BYTE_ORDER))
        # PCM integer format
        fptr.write(0x1.to_bytes(2, self._BYTE_ORDER))
        # Mono audio (1 channel)
        fptr.write(0x1.to_bytes(2, self._BYTE_ORDER))
        fptr.write(self._SAMPLE_RATE_HZ.to_bytes(4, self._BYTE_ORDER))
        fptr.write(bpsec.to_bytes(4, self._BYTE_ORDER))
        fptr.write(bpb.to_bytes(2, self._BYTE_ORDER))
        fptr.write((bpsamp).to_bytes(2, self._BYTE_ORDER))

        """ Data chunk """
        fptr.write(b"data")
        fptr.seek(4, 1)  # skipping sampled data size for now

    def _write_size_data(self, fptr: BufferedWriter):
        """
            Need to now export the data we skipped in `_write_header`.
        """
        file_size: int = fptr.tell()
        logging.debug(f"File size: {file_size} ({file_size:X})")
        fptr.seek(4, 0)  # file size
        rem: int = file_size - 8
        logging.debug("Remaining file size after RIFF header: " +
                      f"{file_size - 8}")
        fptr.write((file_size - 8) .to_bytes(4, self._BYTE_ORDER))
        fptr.seek(0x28, 0)  # Sampled data size
        rem = file_size - fptr.tell() + 4
        logging.debug(f"Sampled data size: {rem}")
        fptr.write(rem.to_bytes(4, self._BYTE_ORDER))

    def export(self):
        with open(self._filename, "wb") as fptr:
            self._write_header(fptr)
            sample: int
            for sample in self._cmp.waveform:
                fptr.write(sample.to_bytes(
                    self._BYTES_PER_SAMPLE, self._BYTE_ORDER, signed=True))

            self._write_size_data(fptr)
