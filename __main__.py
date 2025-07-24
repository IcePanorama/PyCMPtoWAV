"""
    PyCMPtoWAV - a python utility for converting Harvester's CMP files into
    WAVs.
"""
import logging
from cmp.file import CMPFile
from wav.file import WaveformAudioFile

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='[PyCMPtoWAV][%(levelname)s] %(message)s')

    cmp = CMPFile("7.cmp")
    wave = WaveformAudioFile(cmp)
    wave.export()
