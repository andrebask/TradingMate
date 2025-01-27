import os
import sys
import inspect
import json
import logging

currentdir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from Utils.Utils import Utils

class ConfigurationManager():
    """
    Class that loads the configuration and credentials json files exposing
    static methods to provide the configurable parameters
    """

    def __init__(self):
        # Define the config filepath
        self.config_filepath = '{}/.TradingMate/config/config.json'.format(Utils.get_home_path())
        os.makedirs(os.path.dirname(self.config_filepath), exist_ok=True)
        self.config = Utils.load_json_file(self.config_filepath)
        if self.config is None:
            logging.error("Please configure TradingMate: {}".format(self.config_filepath))
            raise RuntimeError("Empty configuration file")
        self.load_credentials()
        logging.info('ConfigurationManager initialised')

    def load_credentials(self):
        """
        Load the credentials file
        """
        try:
            credentials_filepath = self.config['general']['credentials_filepath']
            credentials_filepath = credentials_filepath.replace('{home}', Utils.get_home_path())
        except:
            credentials_filepath = '{}/.TradingMate/config/.credentials'.format(Utils.get_home_path())
            os.makedirs(os.path.dirname(credentials_filepath), exist_ok=True)
            logging.error("credentials filepath parameter not configured! Using default: {}".format(credentials_filepath))

        credentials_json = Utils.load_json_file(credentials_filepath)
        if credentials_json is None:
            logging.warning('Credentials not configured: {}'.format(credentials_filepath))
            credentials_json = {'av_api_key':''}

        self.config['credentials'] = credentials_json


    def get_trading_database_path(self):
        """
        Get the filepath of the trading log file
        """
        return self.config['general']['trading_log_path']

    def get_credentials_path(self):
        """
        Get the filepath of the credentials file
        """
        return self.config['general']['credentials_filepath']

    def get_alpha_vantage_api_key(self):
        """
        Get the alphavantage api key
        """
        return self.config['credentials']['av_api_key']

    def get_alpha_vantage_base_url(self):
        """
        Get the alphavantage API base URI
        """
        return self.config['alpha_vantage']['api_base_uri']

    def get_alpha_vantage_polling_period(self):
        """
        Get the alphavantage configured polling period
        """
        return self.config['alpha_vantage']['polling_period_sec']

    def get_editable_config(self):
        """
        Get a dictionary containing the editable configuration parameters
        """
        return self.config

    def save_settings(self, config):
        """
        Save the edited configuration settings
        """
        # Overwrite settings
        self.config = config
        self.load_credentials()
        # Remove credentials part
        del config['credentials']
        # Write into file
        Utils.write_json_file(self.config_filepath, config)
        logging.info('ConfigurationManater - settings have been saved')
