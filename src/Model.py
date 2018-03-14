from .TaskThread import TaskThread
from .Utils import *

import sys
from enum import Enum
import xml.etree.ElementTree as ET
import threading
import time
import sys
import urllib.request
import json

# Globals
CONFIG_FILE_PATH = "data/config_private.xml" # Change this to data/config.xml
WEB_POLLING_SECONDS = 15 #Seconds

class LivePricesWebThread(TaskThread):

    def __init__(self, model, updatePeriod):
        TaskThread.__init__(self, updatePeriod)
        self.model = model
        self.read_configuration()

    def read_configuration(self):
        try:
            self.configValues = ET.parse(CONFIG_FILE_PATH).getroot()
            self.alphaVantageAPIKey = self.configValues.find("ALPHAVANTAGE_API_KEY").text
            self.alphaVantageBaseURL = self.configValues.find("ALPHAVANTAGE_BASE_URL").text
            # add other config parameters
        except Exception as e:
            print("Model:read_configuration() {0}".format(e))
            sys.exit(1)

    def task(self):
        priceDict = {}
        for symbol in self.model.get_holdings().keys():
            priceDict[symbol] = self.fetch_price_data(symbol)
        if not self._finished.isSet():
            self.model.update_live_price(priceDict)

    def build_url(self, aLength, aSymbol, anInterval, anApiKey):
        function = "function=" + aLength
        symbol = "symbol=" + aSymbol
        interval = "interval=" + anInterval
        apiKey = "apikey=" + anApiKey
        url = self.alphaVantageBaseURL + function + "&" + symbol + "&" + interval + "&" + apiKey
        return url

    def fetch_price_data(self, symbol):
        try:
            url = self.build_url("TIME_SERIES_INTRADAY", symbol, "1min", self.alphaVantageAPIKey)
            request = urllib.request.urlopen(url)
            content = request.read()
            data = json.loads(content.decode('utf-8'))
            timeSerie = data["Time Series (1min)"]
            last = next(iter(timeSerie.values()))
            value = float(last["4. close"])
        except Exception as e:
            print("Model: fetch_price_data(): {0}".format(e))
            value = 0 # TODO manage the exception

        return value

class Model():

    def __init__(self):
        self.read_configuration() # From config.xml file
        self.callbacks = {} # DataStruct containing the callbacks
        self.holdings = {} # DataStruct containing the current holdings
        self.cashAvailable = 0 # Available cash in the portfolio [GBP]
        self.lastLiveData = {} # Buffer to store the latest live data fetched from the web api
        self.livePricesThread = LivePricesWebThread(self, self.webPollingPeriod)
        self.read_database()
        self.update_portfolio()

# INTERNAL FUNCTIONS

    def read_configuration(self):
        self.dbFilePath = "data/config.xml"
        self.webPollingPeriod = 15
        try:
            self.configValues = ET.parse(CONFIG_FILE_PATH).getroot()
            self.dbFilePath = self.configValues.find("TRADING_LOG_PATH").text
            self.webPollingPeriod = int(self.configValues.find("ALPHAVANTAGE_POLLING_PERIOD").text)
        except Exception as e:
            print("Model: read_configuration(): {0}".format(e))

    def read_database(self):
        try:
            self.tradingLogXMLTree = ET.parse(self.dbFilePath)
            self.log = self.tradingLogXMLTree.getroot()
        except Exception as e:
            print("Model: read_database(): {0}".format(e))
            sys.exit(1)

    def update_portfolio(self):
        for row in self.log:
            action = row.find("action").text
            amount = int(row.find("amount").text)
            symbol = row.find("symbol").text

            if action == Actions.DEPOSIT.name or action == Actions.DIVIDEND.name:
                self.cashAvailable += amount
            elif action == Actions.WITHDRAW.name:
                self.cashAvailable -= amount
            elif action == Actions.BUY.name:
                if symbol not in self.holdings:
                    self.holdings[symbol] = amount
                else:
                    self.holdings[symbol] += amount
            elif action == Actions.SELL.name:
                self.holdings[symbol] -= amount

# GETTERS

    def get_log_as_list(self):
        # return a list of Dict with the log data
        listOfEntries = []
        for row in self.log:
            d = {}
            d["date"] = row.find('date').text
            d["action"] = row.find('action').text
            d["symbol"] = row.find('symbol').text
            d["amount"] = row.find('amount').text
            d["price"] = row.find('price').text
            d["fee"] = row.find('fee').text
            d["stamp_duty"] = row.find('stamp_duty').text
            listOfEntries.append(d)
        return listOfEntries
                             
    def get_holdings(self):
        # Returns a dict {symbol: amount} for each current holding  
        return self.holdings

    def get_holding_open_price(self, symbol):
        # Return the average price paid to open the current positon of the requested stock
        sum = 0
        count = 0
        for row in self.log:
            if row.find("symbol").text == symbol and row.find("action").text == Actions.BUY.name:
                sum += float(row.find("price").text)
                count += 1
        avg = sum / count
        return round(avg, 4)

    def get_cash_available(self):
        return self.cashAvailable

    def get_live_data(self):
        return self.lastLiveData
    
# INTERFACES

    def start(self):
        self.livePricesThread.start()

    def stop_application(self):
        self.livePricesThread.shutdown()

    def add_log_entry(self, logEntry):
        self.log.append(logEntry)
        self.tradingLogXMLTree.write(self.dbFilePath)
    
    def remove_log_entry(self, logEntry):
        self.log.remove(logEntry)
        self.tradingLogXMLTree.write(self.dbFilePath)

    def set_callback(self, id, callback):
        self.callbacks[id] = callback

    def update_live_price(self, priceDict):
        self.lastLiveData = priceDict # Store locally
        self.callbacks[Callbacks.UPDATE_LIVE_PRICES](priceDict) # Call callback
    
