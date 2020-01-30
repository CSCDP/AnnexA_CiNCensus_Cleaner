import glob
import os
import logging
from typing import List, Sequence, Union
from dataclasses import dataclass
from fddc.regex import substitute

logger = logging.getLogger('fddc.annex_a.merger.file_scanner')


@dataclass(frozen=True, eq=True)
class ScanSource:
    include: str
    sort_keys: Sequence[str] = None

    @staticmethod
    def coerce(value):
        if isinstance(value, str):
            return ScanSource(value)
        elif isinstance(value, ScanSource):
            return value
        else:
            raise TypeError(f"Cannot coerce {type(value)} to a ScanSource")


@dataclass(frozen=True, eq=True)
class FileSource:
    filename: str
    sort_key: str = None

    @staticmethod
    def coerce(value):
        if isinstance(value, str):
            return FileSource(value)
        elif isinstance(value, FileSource):
            return value
        else:
            raise TypeError(f"Cannot coerce {type(value)} to a FileSource")


def find_input_files(source: Union[ScanSource,str]) -> List[FileSource]:
    """
    Processes a single item in the input config.
    """

    source = ScanSource.coerce(source)

    # Build complete globbing path based on root and include pattern
    file_glob = os.path.abspath(source.include)

    logger.debug("Resolving files using {}".format(file_glob))

    # Search for files and build absolute paths to the files
    files = glob.glob(file_glob, recursive=True)
    files = [os.path.abspath(file) for file in files]

    output = []
    for filename in files:
        # Build sort-keys
        sort_key = filename
        if source.sort_keys is not None:
            for sk in source.sort_keys:
                sort_key = substitute(sk, sort_key, sort_key)

        output.append(FileSource(filename=filename, sort_key=sort_key))
    return output
