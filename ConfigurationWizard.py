import os
from tkinter import filedialog
import customtkinter
from tksheet import Sheet
from ParameterTab import ParameterTab
from Interpolation import Interpolation
from DerateTab import DerateTab


# Creates the configuration tab
class ConfigurationTab(customtkinter.CTkFrame):
    def __init__(self, master: customtkinter.CTkFrame):
        super().__init__(master)

        self.grid_rowconfigure(index=0, weight=0)
        self.grid_rowconfigure(index=1, weight=100)
        self.grid_columnconfigure(index=0, weight=1)
        self.grid_columnconfigure(index=1, weight=1)
        self.grid_columnconfigure(index=2, weight=1)
        self.grid_columnconfigure(index=3, weight=1)
        self.grid_columnconfigure(index=4, weight=1)
        self.grid_columnconfigure(index=5, weight=1)

        # Add the load buttons
        self.loadFromHex = customtkinter.CTkButton(
            self,
            text="Load From Config hex",
            command=self.load_from_hex)
        self.loadFromHex.grid(
            row=0,
            column=0,
            padx=(0, 5),
            pady=5,
            sticky='ew')
        self.loadFromDCF = customtkinter.CTkButton(
            self,
            text="Load From DCF",
            command=self.load_from_dcf)
        self.loadFromDCF.grid(
            row=0,
            column=1,
            padx=5,
            pady=5,
            sticky='ew')
        self.loadFromConfig = customtkinter.CTkButton(
            self,
            text="Load From Config.h",
            command=self.load_from_config)
        self.loadFromConfig.grid(
            row=0,
            column=2,
            padx=(0, 5),
            pady=5,
            sticky='ew')

        # Add the generate buttons
        self.generateHex = customtkinter.CTkButton(
            self,
            text="Generate Config hex",
            command=self.generate_hex)
        self.generateHex.grid(
            row=0,
            column=3,
            padx=(0, 5),
            pady=5,
            sticky='ew')
        self.generateDCF = customtkinter.CTkButton(
            self,
            text="Generate DCF",
            command=self.generate_dcf)
        self.generateDCF.grid(
            row=0,
            column=4,
            padx=(0, 5),
            pady=5,
            sticky='ew')
        self.generateConfig = customtkinter.CTkButton(
            self,
            text="Generate Cofgig.h",
            command=self.generate_config)
        self.generateConfig.grid(
            row=0,
            column=5,
            padx=(0, 5),
            pady=5,
            sticky='ew')

        # Add the main tabview.
        self.tabView = ConfigurationTabView(self)
        self.tabView.grid(row=1, column=0, columnspan=6, sticky="nsew")

    # Grabs the config info from the various tabs
    # and generates a hex file in a user selected location.
    def generate_hex(self):
        for tab in self.tabView.children:
            print(tab.index)

    # Grabs the config info from the various tabs
    # and generates a dcf file in a user selected location.
    def generate_dcf(self):
        for tab in self.tabView.children:
            print(tab.index)

    # Grabs the config info from the various tabs
    # and generates a config.h file in a user selected location.
    def generate_config(self):
        # Get the current config window data as a dictionary of names
        # and tuples in the format (value, datatype)
        config = self.get_config()

        # Get the save as location.
        file = filedialog.asksaveasfile(mode='w', defaultextension=".h")

        # Create default part of the config.h
        startPath = os.path.join(os.getcwd(), "resources\\confighstart")
        start = open(startPath).readlines()
        endPath = os.path.join(os.getcwd(), "resources\\confighend")
        end = open(endPath).readlines()
        middle = []

        # Go through the config entries
        # and create lines of a config.h based on them.
        for parameterKey, parameterValue in config.items():
            parameterLine = ""
            dataType = parameterValue[1]
            variableName = parameterValue[2]
            alias = parameterKey
            if (type(parameterValue[0]) is list):
                x = parameterValue[0][0]
                if (type(x) is list):
                    if len(parameterValue[0]) == 1:
                        # It's a single row of a 2D array,
                        # probably just a quirk of the table.
                        arrayContent = parameterValue[0][0]
                        rowString = ', '.join(list(map(str, arrayContent)))
                        parameterLine = (f"const {dataType} {variableName}"
                                         f"[{len(parameterValue[0][0])}] = "
                                         f"{{ {rowString} }};"
                                         f"// Alias:{alias}")
                    else:
                        # Parameter is 2d array.
                        rowLines = []
                        for row in parameterValue[0]:
                            rowString = ', '.join(list(map(str, row)))
                            rowLines.append(rowString)
                        yLength = len(parameterValue[0])
                        xLength = len(parameterValue[0][0])
                        tableContent = ' }, { '.join(rowLines)
                        parameterLine = (f"const {dataType} {variableName}"
                                         f"[{yLength}][{xLength}] = "
                                         f"{{ {{ {tableContent} }} }};"
                                         f" // Alias:{alias}")
                else:
                    # Parameter is array.
                    arrayLength = len(parameterValue[0])
                    arrayContent = ', '.join(list(map(str, parameterValue[0])))
                    parameterLine = (f"const {dataType} {variableName}"
                                     f"[{arrayLength}] = {{ {arrayContent} }};"
                                     " // Alias:{alias}")
            else:
                # Parameter is singular.
                parameterLine = (f"const {dataType} {variableName} = "
                                 f"{parameterValue[0]}; // Alias:{alias}")
            middle.append(parameterLine)

        # Join the fileparts.
        start.extend(middle)
        start.extend(end)

        # Write the file to the given filelocation
        file.write('\n'.join(start))
        file.close()

    # Takes a dcf file from a user prompt
    # and updates the UI based on the details inside.
    def load_from_hex(self):
        print("loading from hex")

    # Takes a dcf file from a user prompt
    # and updates the UI based on the details inside.
    def load_from_dcf(self):
        print("loading from dcf")

    # Takes a config.h file from a user prompt
    # and updates the UI based on the details inside.
    def load_from_config(self):
        print("loading from config")

    # Grabs the data from the configuration tabs and collates it.
    def get_config(self):
        from ParameterTab import DataTypesEnum
        chargeDerateTable = self.tabView.chargeTab.table.get_sheet_data()
        chargeTempRange = self.tabView.chargeTab.table.MT._headers
        chargeSocRange = self.tabView.chargeTab.table.MT._row_index
        dischargeDerateTable = self.tabView.dischargeTab.table.get_sheet_data()
        dischargeTempRange = self.tabView.dischargeTab.table.MT._headers
        dischargeSocRange = self.tabView.dischargeTab.table.MT._row_index
        parameterData = self.tabView.parameterTab.get_parameters()
        parameterData.update({
            "Charge Table":
                (chargeDerateTable,
                 DataTypesEnum.float.name,
                 'derateChargingLookup'),
            "Discharge Table":
                (dischargeDerateTable,
                 DataTypesEnum.float.name,
                 'derateDischargingLookup'),
            "Charge Temp Axis":
                (chargeTempRange,
                 DataTypesEnum.float.name,
                 'derateChargingTemperatureAxis'),
            "Charge SoC Axis":
                (chargeSocRange,
                 DataTypesEnum.float.name,
                 'derateChargingSoCAxis'),
            "Discharge Temp Axis":
                (dischargeTempRange,
                 DataTypesEnum.float.name,
                 'derateDischargingTemperatureAxis'),
            "Discharge SoC Axis":
                (dischargeSocRange,
                 DataTypesEnum.float.name,
                 'derateDischargingSoCAxis'),
            })
        return parameterData


# Creates the ConfigurationTabView which holds
# the various configuration tabs of the application.
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
        self.chargeTab = DerateTab(
             tab_2,
             [['', '', '', '', '', '', '', ''],
              ['', '', '', '', '', '', '', ''],
              ['', '', '', 230, 230, '', '', ''],
              ['', '', '', '', '', '', '', ''],
              ['', '', '', '', '', '', '', ''],
              ['', '', '', '', '', '', '', ''],
              ['', '', '', '', '', '', '', ''],
              ['', '', '', '', '', '', '', ''],
              ['', '', '', '', '', '', '', ''],
              ['', '', '', '', '', '', '', ''],
              [0, 0, 0, 0, 0, 0, 0, 0]],
             True)
        self.chargeTab.grid(row=0, column=0, sticky="nsew")
        self.dischargeTab = DerateTab(
             tab_3,
             [[0, 0, 0, 0, 0, 0, 0, 0],
              ['', '', '', '', '', '', '', ''],
              ['', '', '', '', '', '', '', ''],
              ['', '', '', '', '', '', '', ''],
              ['', '', '', '', '', '', '', ''],
              ['', '', '', '', '', '', '', ''],
              ['', '', '', '', '', '', '', ''],
              ['', '', '', '', '', '', '', ''],
              ['', '', '', 460, 460, '', '', ''],
              ['', '', '', '', '', '', '', ''],
              ['', '', '', '', '', '', '', '']],
             False)
        self.dischargeTab.grid(row=0, column=0, sticky="nsew")
        # Expand the tab content
        self.parameterTab.grid_columnconfigure(0, weight=1)
        self.parameterTab.grid_rowconfigure(0, weight=1)

    def interpolate_values(self, table: Sheet):
        oldData = table.MT.data
        newData = Interpolation.ScatteredBicubicInterpolation(
             oldData,
             len(table.MT._headers),
             len(table.MT._row_index))
        table.set_sheet_data(newData)
        table.set_all_column_widths(30)
