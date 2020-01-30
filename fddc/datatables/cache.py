import logging

import pandas as pd
from typing import Dict, Any


logger = logging.getLogger('fddc.datatables.cache')


class ExcelFileSource:
    """
    A utility class for saving reloading of Excel files when reading multiple sheets
    """
    __file_map: Dict[Any, pd.ExcelFile] = dict()

    def get_file(self, filename: str) -> pd.ExcelFile:
        """
        Returns a cached or new ExcelFile if the filename has never been loaded before
        :param filename:
        :return:
        """
        if filename in self.__file_map:
            logger.debug(f"Fetching {filename} from cache.")
        else:
            logger.debug(f"Creating new ExcelFile for {filename}.")
        return self.__file_map.setdefault(filename, pd.ExcelFile(filename))
