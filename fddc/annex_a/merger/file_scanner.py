import glob
import os
import logging
from typing import List, Sequence

from dataclasses import dataclass

from fddc.regex import substitute

logger = logging.getLogger('fddc.annex_a.merger.file_scanner')


@dataclass
class ScanSource:
    include: str
    root: str = "."
    sort_keys: Sequence[str] = None

@dataclass
class FileSource:
    filename: str
    sourcename: str = None
    sort_key: str = None
    root: str = None


def find_input_files(source: ScanSource) -> List[FileSource]:
    """
    Processes a single item in the input config.
    """

    # Build complete globbing path based on root and include pattern
    root = os.path.abspath(source.root)
    file_glob = os.path.join(root, source.include)

    logger.debug("Resolving files using {}".format(file_glob))

    # Search for files and build absolute paths to the files
    files = glob.glob(file_glob, recursive=True)
    files = [os.path.abspath(file) for file in files]

    output = []
    for filename in files:
        sourcename = os.path.relpath(filename, root)

        # Build sort-keys
        sort_key = sourcename
        if source.sort_keys is not None:
            for sk in source.sort_keys:
                sort_key = substitute(sk, sort_key, sort_key)

        output.append(FileSource(filename=filename, sourcename=sourcename, sort_key=sort_key, root=root))
    return output
