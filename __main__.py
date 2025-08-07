"""
    PyCMPtoWAV - a python utility for converting Harvester's CMP files into
    WAVs.
"""
import logging
from cmp.file import CMPFile
from wav_file import WaveformAudioFile
from sys import argv
from typing import List

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='[PyCMPtoWAV][%(levelname)s] %(message)s')
    args: List[str] = argv[1:]
    if not args:
        logging.error("Improper usage. Usage: `python " +
                      f"{argv[0]} path/to/file.cmp`")

    for arg in args:
        logging.info(f"Processing {arg}...")

        try:
            cmp = CMPFile(arg)
            wave = WaveformAudioFile(cmp)
            wave.export()
        except RuntimeError as e:
            logging.error(e)
            exit(-1)
