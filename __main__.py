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
bytes_per_samples: int = 4
output_filename: str = ""
exe_name: str = sys.argv[0]
improper_usage_err_msg: str = f"Improper usage. Try: `python {exe_name} " \
    + "path/to/file.cmp`"


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

    fmt: str = "  {:30} {}"
    print("Options:")
    print(fmt.format("-B <n>, --bytes-per-sample <n>",
          "Set output bytes per sample to <n> bytes (default: 4)"))
    print(fmt.format("-D, --debug", "Enable debug output"))
    print(fmt.format("-h, --help", "Print this help message"))
    print(fmt.format("-o <fname>, --output <fname>",
          "Set output filename to <fname>"))
    print(fmt.format("-v, --version", "Print version information"))


def extract_files(files: List[int]) -> None:
    """ Extracts files using a list of paths. """
    if not args:
        raise RuntimeError(improper_usage_err_msg)

    for arg in args:
        logging.info(f"Processing {arg}...")
        cmp = CMPFile(arg)
        wave = WaveformAudioFile(cmp, bytes_per_sample=bytes_per_samples,
                                 filename=output_filename)
        wave.export()


def process_command_line_args(args: List[str]) -> int:
    """
        Process command line arugments and return the number of arguments
        recieved. Probably more elegant ways to go about this, but it works.
    """
    args_len: int = len(args)
    i: int = 0
    global bytes_per_samples
    global output_filename
    while (i < args_len):
        a: str = args[i]
        if (a == "-v") or (a == "--version"):
            print_ver_info()
            exit(0)
        elif (a == "-h") or (a == "--help"):
            print_help(exe_name)
            exit(0)
        elif (a == "-B") or (a == "--bytes-per-sample"):
            if (i + 1 >= args_len):
                raise RuntimeError(improper_usage_err_msg)
            logging.debug(f"Bytes per sample set to {args[i + 1]} bytes.")
            bytes_per_samples = int(args[i + 1])
            i += 1
        elif (a == "-D") or (a == "--debug"):
            logging.getLogger().setLevel(level=logging.DEBUG)
        elif (a == "-o") or (a == "--output"):
            if (i + 1 >= args_len):
                raise RuntimeError(improper_usage_err_msg)
            output_filename = args[i + 1]
            i += 1
        else:
            break
        i += 1
    return i


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='[PyCMPtoWAV][%(levelname)s] %(message)s')

    args: List[str] = sys.argv[1:]
    if not args:
        logging.error(improper_usage_err_msg)
        exit(-1)

    i: int = 0
    try:
        i = process_command_line_args(args)
        args = args[i:] if not output_filename else args[i:1]
        extract_files(args)
    except BaseException as e:
        logging.error(e)
        exit(-1)
