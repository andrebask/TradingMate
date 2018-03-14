from .Utils import Actions

import tkinter as tk
from tkinter import ttk

class AddTradeDialogWindow(tk.Toplevel):

    def __init__(self, master, confirmCallback):
        tk.Toplevel.__init__(self)
        self.master = master
        self.confirmCallback = confirmCallback
        self.transient(self.master)
        self.title("Add Trade")
        self.geometry("+%d+%d" % (self.master.winfo_rootx()+400, self.master.winfo_rooty()+100))
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.grab_set()
        self.focus_set()

        self.create_UI()

    def create_UI(self):
        # Define the labels on the left hand column
        ttk.Label(self, text="Date:").grid(row=0, sticky="w", padx=5, pady=5)
        ttk.Label(self, text="Action:").grid(row=1, sticky="w", padx=5, pady=5)
        ttk.Label(self, text="Symbol:").grid(row=2, sticky="w", padx=5, pady=5)
        ttk.Label(self, text="Amount:").grid(row=3, sticky="w", padx=5, pady=5)
        ttk.Label(self, text="Price [p] :").grid(row=4, sticky="w", padx=5, pady=5)
        ttk.Label(self, text="Fee [£] :").grid(row=5, sticky="w", padx=5, pady=5)
        ttk.Label(self, text="Stamp Duty [%] :").grid(row=6, sticky="w", padx=5, pady=5)

        # Define the date entry widget
        self.dateSelected = tk.StringVar()
        eDate = ttk.Entry(self, textvariable=self.dateSelected)
        eDate.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        # Define an option menu for the action
        self.actionSelected = tk.StringVar()
        menuList = [a.name for a in Actions]
        eAction = ttk.OptionMenu(self, self.actionSelected, menuList[0], *menuList, command=self.on_action_selected)
        eAction.grid(row=1, column=1, sticky="w", padx=5, pady=5)
       
        self.symbolSelected = tk.StringVar()
        self.eSymbol = ttk.Entry(self, textvariable=self.symbolSelected)
        self.eSymbol.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        self.amountSelected = tk.StringVar()
        self.eAmount = ttk.Entry(self, textvariable=self.amountSelected)
        self.eAmount.grid(row=3, column=1, sticky="w", padx=5, pady=5)

        self.priceSelected = tk.StringVar()
        self.ePrice = ttk.Entry(self, textvariable=self.priceSelected)
        self.ePrice.grid(row=4, column=1, sticky="w", padx=5, pady=5)

        self.feeSelected = tk.StringVar()
        self.eFee = ttk.Entry(self, textvariable=self.feeSelected)
        self.eFee.grid(row=5, column=1, sticky="w", padx=5, pady=5)

        self.stampDutySelected = tk.StringVar()
        self.eStampDuty = ttk.Entry(self, textvariable=self.stampDutySelected)
        self.eStampDuty.grid(row=6, column=1, sticky="w", padx=5, pady=5)

        cancelButton = ttk.Button(self, text="Cancel", command=self.destroy)
        cancelButton.grid(row=7, column=0, sticky="e", padx=5, pady=5)
        addButton = ttk.Button(self, text="Add", command=self.add_new_trade)
        addButton.grid(row=7, column=1, sticky="e", padx=5, pady=5)

        # Make the mas ter thread block execution until this window is closed
        self.master.wait_window(self)

    def on_action_selected(self, selection):
        if selection == Actions.BUY.name:
            self.eSymbol.config(state='enabled')
            self.eAmount.config(state='enabled')
            self.ePrice.config(state='enabled')
            self.eFee.config(state='enabled')
            self.eStampDuty.config(state='enabled')
        elif selection == Actions.SELL.name:
            self.eSymbol.config(state='enabled')
            self.eAmount.config(state='enabled')
            self.ePrice.config(state='enabled')
            self.eFee.config(state='enabled')
            self.eStampDuty.config(state='disabled')
        elif selection == Actions.DEPOSIT.name:
            self.eSymbol.config(state='disabled')
            self.eAmount.config(state='enabled')
            self.ePrice.config(state='disabled')
            self.eFee.config(state='disabled')
            self.eStampDuty.config(state='disabled')
        elif selection == Actions.DIVIDEND.name:
            self.eSymbol.config(state='enabled')
            self.eAmount.config(state='enabled')
            self.ePrice.config(state='disabled')
            self.eFee.config(state='disabled')
            self.eStampDuty.config(state='disabled')
        elif selection == Actions.WITHDRAW.name:
            self.eSymbol.config(state='disabled')
            self.eAmount.config(state='enabled')
            self.ePrice.config(state='disabled')
            self.eFee.config(state='disabled')
            self.eStampDuty.config(state='disabled')

    def add_new_trade(self):
        # Get selected data and call callback
        newTrade = {}
        newTrade["date"] = self.dateSelected.get()
        newTrade["action"] = self.actionSelected.get()
        newTrade["symbol"] = self.symbolSelected.get()
        newTrade["amount"] = self.amountSelected.get()
        newTrade["price"] = self.priceSelected.get()
        newTrade["fee"] = self.feeSelected.get()
        newTrade["stamp_duty"] = self.stampDutySelected.get()
        self.confirmCallback(newTrade)
        self.destroy()
