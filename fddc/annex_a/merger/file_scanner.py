import glob
import os
import logging
from typing import List, Sequence

from dataclasses import dataclass

from fddc.regex import substitute

logger = logging.getLogger('fddc.annex_a.merger.file_scanner')


@dataclass
class FileSource:
    filename: str
    sourcename: str
    sort_key: str
    root: str


def find_input_files(root: str, include: str, sort_keys: Sequence[str] = None) -> List[FileSource]:
    """
    Processes a single item in the input config.
    """

    # Build complete globbing path based on root and include pattern
    root = os.path.abspath(root)
    file_glob = os.path.join(root, include)

    logger.debug("Resolving files using {}".format(file_glob))

    # Search for files and build absolute paths to the files
    files = glob.glob(file_glob, recursive=True)
    files = [os.path.abspath(file) for file in files]

    output = []
    for filename in files:
        sourcename = os.path.relpath(filename, root)

        # Build sort-keys
        if sort_keys is None:
            sort_key = sourcename
        else:
            sort_key = sourcename
            for sk in sort_keys:
                sort_key = substitute(sk, sort_key, sort_key)

        output.append(FileSource(filename=filename, sourcename=sourcename, sort_key=sort_key, root=root))
    return output
