"""
    WaveformAudioFile - An interface for creating WAVs from CMP files.

    Copyright (C) 2025  IcePanorama

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
from cmp.file import CMPFile
from io import BufferedWriter
import logging
from typing import List


class WaveformAudioFile:
    """ See: https://en.wikipedia.org/wiki/WAV """
    _BYTE_ORDER: str = "little"  # needed for `to_bytes`

    def __init__(self, cmp: CMPFile, bytes_per_sample: int = 4,
                 filename: str = ""):
        logging.info(f"Creating WAV object from cmp file: {cmp.filename}")
        self._sampling_rate: int = cmp.sampling_rate
        self._precision: int = cmp.precision
        self._bytes_per_sample: int = bytes_per_sample
        self._filename: str = \
            filename if filename else self._create_filename(cmp.filename)
        logging.debug(f"Output filename: {self._filename}")

        self._waveform: List[int] = self._normalize_waveform(cmp.waveform)

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
            CMP decoded waveform is a signed N-bit PCM "linear output sample"
            waveform however, we need this value to be normalized according to
            the range specified by `self._bytes_per_sample`.
        """
        logging.debug(f"Normalizing input PCM waveform ({self._precision}-bit "
                      + f"-> {self._bytes_per_sample << 3}-bit)")
        UN_MAX: int = (2**self._precision) - 1
        HALF_UN_MAX: int = (UN_MAX + 1) >> 1
        work: List[float] = [((s + HALF_UN_MAX) / UN_MAX) for s in waveform]
        work = [max(0.0, min(s, 1.0)) for s in work]

        UW_MAX: int = (2**(self._bytes_per_sample << 3)) - 1
        HALF_UW_MAX: int = (UW_MAX + 1) >> 1
        return [int(s * UW_MAX - HALF_UW_MAX) for s in work]

    def _write_header(self, fptr: BufferedWriter):
        """ See: https://en.wikipedia.org/wiki/WAV#WAV_file_header """
        logging.debug("Writing header...")

        """ Master RIFF chunk """
        fptr.write(b"RIFF")
        fptr.seek(4, 1)  # skipping file size for now
        fptr.write(b"WAVE")

        """ Fmt chunk """
        fptr.write(b"fmt ")  # added space is intentional
        fptr.write(0x10.to_bytes(4, self._BYTE_ORDER))  # chunk bloc size
        fptr.write(0x01.to_bytes(2, self._BYTE_ORDER))  # PCM integer format
        fptr.write(0x01.to_bytes(2, self._BYTE_ORDER))  # Mono audio
        fptr.write(self._sampling_rate.to_bytes(4, self._BYTE_ORDER))

        bpsamp: int = (self._bytes_per_sample << 3)  # bits per sample
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
        logging.debug("Writing size info in header...")

        file_size: int = fptr.tell()
        logging.debug(f"Output file size (B): {file_size} (0x{file_size:X})")
        fptr.seek(4, 0)
        rem: int = file_size - 8
        fptr.write((file_size - 8).to_bytes(4, self._BYTE_ORDER))

        """ Update sampled data size. """
        fptr.seek(0x28, 0)
        rem = file_size - fptr.tell() - 4
        logging.debug(f"Sampled data size (B): {rem} (0x{rem:X})")
        fptr.write(rem.to_bytes(4, self._BYTE_ORDER))

    def export(self):
        """ Writes the associated wav file to the current directory. """
        logging.info(f"Exporting file: {self._filename}")
        # Disabling buffering as we need to accurate measure size data later
        with open(self._filename, "wb", buffering=0) as fptr:
            self._write_header(fptr)

            logging.debug("Exporting waveform...")
            sample: int
            for sample in self._waveform:
                fptr.write(sample.to_bytes(self._bytes_per_sample,
                           self._BYTE_ORDER, signed=True))

            self._write_size_data(fptr)
