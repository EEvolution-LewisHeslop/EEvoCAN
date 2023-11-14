import customtkinter
from tksheet import Sheet

from ParameterTab import ParameterTab
from ResizeHandler import ResizeHandler
from Interpolation import Interpolation
from DerateTab import DerateTab

# Creates the configuration tab
class ConfigurationTab(customtkinter.CTkFrame):
    def __init__(self, master: customtkinter.CTkFrame):
        super().__init__(master)
        self.tabView = ConfigurationTabView(self)
        self.tabView.grid(row=0, column=0, sticky="nsew")

### Configuration Tab View ###

# Creates the ConfigurationTabView which holds the various configuration tabs of the application.
class ConfigurationTabView(customtkinter.CTkTabview):
    # Builds the tabview and starts any GUI updaters for the tabs.
    def __init__(self, master: customtkinter.CTkFrame):
            # Create the tabview
            super().__init__(master)

            # Build the tabs
            tab_1 = self.add("Parameters")
            tab_2 = self.add("Charge Derate")
            tab_3 = self.add("Discharge Derate")

            # Expand the main area of the tabs
            tab_1.grid_columnconfigure(0, weight=1)
            tab_1.grid_rowconfigure(0, weight=1)
            tab_2.grid_columnconfigure(0, weight=1)
            tab_2.grid_rowconfigure(0, weight=1)
            tab_3.grid_columnconfigure(0, weight=1)
            tab_3.grid_rowconfigure(0, weight=1)

            # Build the tab content
            self.parameterTab = ParameterTab(tab_1)
            self.parameterTab.grid(row=0, column=0, sticky="nsew")
            self.chargeTab = DerateTab(tab_2, [['','','','','','','',''],
                      ['','','','','','','',''],
                      ['','','',230,230,'','',''],
                      ['','','','','','','',''],
                      ['','','','','','','',''],
                      ['','','','','','','',''],
                      ['','','','','','','',''],
                      ['','','','','','','',''],
                      ['','','','','','','',''],
                      ['','','','','','','',''],
                      [0,0,0,0,0,0,0,0]], True)     
            self.chargeTab.grid(row=0, column=0, sticky="nsew")
            self.dischargeTab = DerateTab(tab_3, [[0,0,0,0,0,0,0,0],
                  ['','','','','','','',''],
                  ['','','','','','','',''],
                  ['','','','','','','',''],
                  ['','','','','','','',''],
                  ['','','','','','','',''],
                  ['','','','','','','',''],
                  ['','','','','','','',''],
                  ['','','',460,460,'','',''],
                  ['','','','','','','',''],
                  ['','','','','','','','']], False)
            self.dischargeTab.grid(row=0, column=0, sticky="nsew")

            # Expand the tab content
            self.parameterTab.grid_columnconfigure(0, weight=1)
            self.parameterTab.grid_rowconfigure(0, weight=1)

    def interpolate_values(self, table: Sheet):
        oldData = table.MT.data
        newData = Interpolation.ScatteredBicubicInterpolation(oldData, len(table.MT._headers), len(table.MT._row_index))
        table.set_sheet_data(newData)
        table.set_all_column_widths(30)