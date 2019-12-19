import copy
import datetime
import logging
import os
import yaml

class Config(dict):

    def __init__(self, *config_files, local_required=False, local_warn=False):
        super().__init__(
                config_date = datetime.datetime.now().isoformat(),
                username = os.getlogin()
            )

        self.__logger = logging.getLogger('Config')
        
        self.load_config("./localconfig.yml", conditional=~local_required, warn=local_warn)

        for file in config_files:
            self.load_config(file, conditional=False)

        
    def load_config(self, filename, conditional=False, warn=False):
        """
        Load configuration from yaml file. Any loaded configuration
        is only set if the values don't already exist in CONFIG.

        Keyword arguments:
        filename -- Filename to load from
        conditional -- If True, ignore file if it doesn't exist. If False, fail. (default False)
        """
        if conditional and not os.path.isfile(filename):
            if warn:
                self.__logger.warning('Missing optional file {}'.format(filename))

            return 

        with open(filename) as FILE:
            user_config = yaml.load(FILE, Loader=yaml.FullLoader)
            self.__logger.info("Loading {} configuration values from '{}'.".format(len(user_config), filename))
            self.update(user_config)


        
