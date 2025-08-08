"""
    PyCMPtoWAV - a python utility for converting Harvester's CMP files into
    WAVs.
"""
import logging
import sys
from cmp.file import CMPFile
from typing import List
from wav_file import WaveformAudioFile

CURR_VERSION: str = "v1.0.0b"


def print_ver_info() -> None:
    """ Prints version info, copyright boilerplate to stdout. """
    print(f"PyCMPtoWAV {CURR_VERSION}")

    print("Copyright (C) 2025 IcePanorama")
    print("License GPLv3+: GNU GPL version 3 or later "
          + "<https://gnu.org/licenses/gpl.html>")
    print("This is free software: you are free to change and redistribute it.")
    print("There is NO WARRANTY, to the extent permitted by law.")


def print_help(exe: str) -> None:
    """ Prints help/usage info to stdout. """
    print("Usage:")
    print(f"  python {exe_name} [options] path/to/file.dat [...]\n")

    fmt: str = "  {:13} {}"
    print("Options:")
    print(fmt.format("-h, --help", "Print this help message"))
    print(fmt.format("-v, --version", "Print version information"))
    pass


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='[PyCMPtoWAV][%(levelname)s] %(message)s')

    exe_name: str = sys.argv[0]
    args: List[str] = sys.argv[1:]
    if not args:
        logging.error(f"Improper usage. Usage: `python {exe_name} "
                      + "path/to/file.cmp`")
        exit(-1)

    for a in args:
        if (a == "-v") or (a == "--version"):
            print_ver_info()
        elif (a == "-h") or (a == "--help"):
            print_help(exe_name)

    """
    for arg in args:
        logging.info(f"Processing {arg}...")

        try:
            cmp = CMPFile(arg)
            wave = WaveformAudioFile(cmp)
            wave.export()
        except RuntimeError as e:
            logging.error(e)
            exit(-1)
    """
