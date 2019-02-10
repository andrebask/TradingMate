import os
import sys
import inspect
import logging
import datetime as dt

currentdir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from Utils.ConfigurationManager import ConfigurationManager
from Model.Portfolio import Portfolio
from UI.View import View
from Utils.Utils import Callbacks, Actions, Messages
from Model.DatabaseHandler import DatabaseHandler


class TradingMate():

    def __init__(self):
        # Init the configuration manager
        self.configurationManager = ConfigurationManager()
        # Database handler
        self.db_handler = DatabaseHandler(self.configurationManager)
        # Setup the logging
        self.setup_logging()
        # Init the portfolio
        self.portfolio = Portfolio("Portfolio1", self.configurationManager)
        # Init the view
        self.view = View()
        # Register callbacks
        self.register_callbacks()

    def setup_logging(self):
        """
        Setup the global logging settings
        """
        # Define the global logging settings
        debugLevel = logging.DEBUG if self.configurationManager.get_debug_log_active() else logging.INFO
        # If enabled define log file filename with current timestamp
        if self.configurationManager.get_enable_file_log():
            log_filename = self.configurationManager.get_log_filepath()
            time_str = dt.datetime.now().isoformat()
            time_suffix = time_str.replace(':', '_').replace('.', '_')
            home = str(Path.home())
            log_filename = log_filename.replace(
                '{timestamp}', time_suffix).replace('{home}', home)
            os.makedirs(os.path.dirname(log_filename), exist_ok=True)
            logging.basicConfig(filename=log_filename,
                                level=debugLevel,
                                format="[%(asctime)s] %(levelname)s: %(message)s")
        else:
            logging.basicConfig(level=debugLevel,
                                format="[%(asctime)s] %(levelname)s: %(message)s")

    def register_callbacks(self):
        """
        Register all the callback functions
        """
        # TODO instead of a callback, set a timer that calls a getter every x seconds
        self.portfolio.set_callback(
            Callbacks.UPDATE_LIVE_PRICES, self.on_update_live_price)
        # Init the view
        self.view.set_callback(
            Callbacks.ON_CLOSE_VIEW_EVENT, self.on_close_view_event)
        self.view.set_callback(
            Callbacks.ON_MANUAL_REFRESH_EVENT, self.on_manual_refresh_event)
        self.view.set_callback(
            Callbacks.ON_NEW_TRADE_EVENT, self.on_new_trade_event)
        self.view.set_callback(
            Callbacks.ON_SET_AUTO_REFRESH_EVENT, self.on_set_auto_refresh)
        self.view.set_callback(
            Callbacks.ON_OPEN_LOG_FILE_EVENT, self.on_open_portfolio_event)
        self.view.set_callback(
            Callbacks.ON_SAVE_LOG_FILE_EVENT, self.on_save_portfolio_event)
        self.view.set_callback(
            Callbacks.ON_DELETE_LAST_TRADE_EVENT, self.on_delete_last_trade_event)

    def start(self):
        # Read the configured database
        self.db_handler.read_data()
        # Start portfolio
        self.portfolio.start(self.db_handler.get_trades_list())
        # Update the UI
        self._update_share_trading_view(updateHistory=True)
        # This should be the last instruction in this function
        self.view.start()

# Functions

    def _update_share_trading_view(self, updateHistory=False):
        self.view.reset_view(updateHistory)
        # Update the database filepath shown in the share trading frame
        self.view.set_db_filepath(self.db_handler.get_db_filepath())
        # Update history table if required
        if updateHistory:
            logAsList = self.db_handler.get_trades_list()[::-1]  # Reverse order
            self.view.update_share_trading_history_log(logAsList)
        # get the balances from the portfolio and update the view
        cash = self.portfolio.get_cash_available()
        holdingsValue = self.portfolio.get_holdings_value()
        totalValue = self.portfolio.get_total_value()
        pl = self.portfolio.get_portfolio_pl()
        pl_perc = self.portfolio.get_portfolio_pl_perc()
        holdingPL = self.portfolio.get_open_positions_pl()
        holdingPLPC = self.portfolio.get_open_positions_pl_perc()
        # Update the view
        validity = True
        for h in self.portfolio.get_holding_list():
            self.view.update_share_trading_holding(h.get_symbol(), h.get_amount(), h.get_open_price(),
                                                   h.get_last_price(), h.get_cost(), h.get_value(), h.get_profit_loss(), h.get_profit_loss_perc(), h.get_last_price_valid())
            validity = validity and h.get_last_price_valid()
        self.view.update_share_trading_portfolio_balances(
            cash, holdingsValue, totalValue, pl, pl_perc, holdingPL, holdingPLPC, validity)

# EVENTS

    def on_close_view_event(self):
        self.portfolio.stop()
        self.db_handler.write_data()

    def on_manual_refresh_event(self):
        self.portfolio.on_manual_refresh_live_data()

    def on_set_auto_refresh(self, enabled):
        self.portfolio.set_auto_refresh(enabled)

    def on_update_live_price(self):
        self._update_share_trading_view()

    def on_new_trade_event(self, new_trade):
        # Validate trade
        if not self.portfolio.is_trade_valid(new_trade):
            raise RuntimeError('Trade is invalid')
        # Update databse
        self.db_handler.add_trade(new_trade)
        # Reload portfolio
        self.portfolio.reload(self.db_handler.get_trades_list())
        # Update the ui
        self._update_share_trading_view(updateHistory=True)

    def on_delete_last_trade_event(self):
        # Remove trade from database
        self.db_handler.remove_last_trade()
        # Reload portfolio
        self.portfolio.reload(self.db_handler.get_trades_list())
        # Update the UI
        self._update_share_trading_view(updateHistory=True)

    def on_open_portfolio_event(self, filepath):
        # Read database from filepath
        self.db_handler.read_data(filepath)
        # Reload portfolio
        self.portfolio.reload(self.db_handler.get_trades_list())
        # Update the UI
        self.view.reset_view(resetHistory=True)
        self._update_share_trading_view(updateHistory=True)

    def on_save_portfolio_event(self, filepath):
        # Write data into the database
        self.db_handler.write_data(filepath=filepath)
