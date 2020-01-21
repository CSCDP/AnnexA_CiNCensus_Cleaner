import glob
import os
import logging
from fddc.regex import substitute

logger = logging.getLogger('fddc.annex_a.merger.file_scanner')


def find_input_files(root, include, sort_keys=None, **args):
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

        output.append({
            "filename": filename,
            "sourcename": sourcename,
            "sort_key": sort_key,
            "sort_keys": sort_keys,
            "root": root,
            "input_cfg": {
                "root": root,
                "include": include,
                **args
            }})

    return output