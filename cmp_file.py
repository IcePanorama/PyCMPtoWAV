import logging


class CMPFile:
    """
        Harvester's 22.5 kHz Dialogic (VOX) ADPCM sound files, used for music
        and voice lines.
    """
    _SAMPLE_RATE_HERTZ: int = 22500

    def __init__(self, filename: str):
        self._filename: str = filename
        logging.info(f"Creating CMP file from {filename}")
        self._data: bytes
        with open(self._filename, "rb") as fptr:
            self._data = fptr.read()
