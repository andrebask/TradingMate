import os
import sys
import inspect

currentdir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, '{}/src'.format(parentdir))

class MockConfigurationManager():
    def __init__(self):
        pass

    def get_trading_database_path(self):
        return parentdir + "/test_data/trading_log.json"

    def get_alpha_vantage_api_key(self):
        return "MOCK"

    def get_alpha_vantage_base_url(self):
        return "https://www.alphavantage.co/query"

    def get_alpha_vantage_polling_period(self):
        return 1

    def get_debug_log_active(self):
        return False

    def get_enable_file_log(self):
        return False

    def get_log_filepath(self):
        return "/tmp/mock_log.txt"
