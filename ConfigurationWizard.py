import customtkinter
from tksheet import Sheet
from CTkTable import CTkTable
from Interpolation import Interpolation

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
            self.chargeTab = ChargeTab(tab_2)
            self.chargeTab.grid(row=0, column=0, sticky="nsew")
            self.dischargeTab = DischargeTab(tab_3)
            self.dischargeTab.grid(row=0, column=0, sticky="nsew")

            # Expand the tab content
            self.parameterTab.grid_columnconfigure(0, weight=1)
            self.parameterTab.grid_rowconfigure(0, weight=1)
            self.chargeTab.grid_columnconfigure(0, weight=1)
            self.chargeTab.grid_rowconfigure(0, weight=1)
            self.dischargeTab.grid_columnconfigure(0, weight=1)
            self.dischargeTab.grid_rowconfigure(0, weight=1)

# Creates the parameter subtab
class ParameterTab(customtkinter.CTkScrollableFrame):
    def __init__(self, master: customtkinter.CTkFrame):
        super().__init__(master)

        # Create the Temperature Range Frame
        self.temperatureRangeFrame = TemperatureRangeFrame(self)
        self.temperatureRangeFrame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        # Create the SoC Range Frame
        self.socRangeFrame = SocRangeFrame(self)
        self.socRangeFrame.grid(row=1, column=0, padx=5, pady=(0,5), sticky="nsew")

# Creates the derate charge subtab
class ChargeTab(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        # Create default Table Values
        values = [['','',''],
                  ['',230,''],
                  ['','',''],]

        # Create Sheet
        self.table = Sheet(self, theme="dark green", data = values)
        self.table.enable_bindings()
        self.table.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Assign sheet to resize handler charge table
        ResizeHandler.setTableReference(self.table, True)

        # Create interpolate button
        self.interpolateButton = customtkinter.CTkButton(self, text="Interpolate", command=lambda:self.interpolate_values(self.table))
        self.interpolateButton.grid(row=1, column=0, padx=5, pady=5)

    def interpolate_values(self, table: Sheet):
        newData = Interpolation.ScatteredBicubicInterpolation(table.data)
        table.set_sheet_data(Interpolation.ScatteredBicubicInterpolation(table.data))

# Creates the derate discharge subtab
class DischargeTab(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        # Create Table
        values = [['','',''],
                  ['',460,''],
                  ['','',''],]
        
        # Create Sheet
        self.table = Sheet(self, theme="dark green", data = values)
        self.table.enable_bindings()
        self.table.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Assign sheet to resize handler charge table
        ResizeHandler.setTableReference(self.table, False)

        # Create interpolate button
        self.interpolateButton = customtkinter.CTkButton(self, text="Interpolate", command=lambda:self.interpolate_values(self.table))
        self.interpolateButton.grid(row=1, column=0, padx=5, pady=5)

    def interpolate_values(self, table: Sheet):
        newData = Interpolation.ScatteredBicubicInterpolation(table.data)
        table.set_sheet_data(Interpolation.ScatteredBicubicInterpolation(table.data))

### Parameter Tab Frames ###

class TemperatureRangeFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        self.grid_columnconfigure(3, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Create the frame heading.
        self.configure(fg_color="darkslategray", corner_radius=6)
        self.frameHeading = customtkinter.CTkLabel(self, text="Temperature Range", corner_radius=6)
        self.frameHeading.grid(row=0, column=0, pady=5, sticky="w")

        # Create the resolution entry label
        self.resolutionEntryLabel = customtkinter.CTkLabel(self, text="Configure Length", corner_radius=6)
        self.resolutionEntryLabel.grid(row=1, column=0, pady=5, sticky="w")

        # Create the resolution entry box
        self.textVariable = customtkinter.StringVar(self, "3")
        #self.textVariable.trace_add("write", self.resizeCallback)
        self.resolutionEntryBox = customtkinter.CTkEntry(self, textvariable=self.textVariable)
        self.resolutionEntryBox.grid(row=1, column=1, pady=5, sticky="e")

        # Create the temperature range table frame
        self.tableFrame = customtkinter.CTkScrollableFrame(self, orientation="horizontal", height=30)
        self.tableFrame.grid(row=2, column=0, columnspan=4, padx=5, sticky="new")

        # Create the temperature range table
        value = [[-10, '', 55]]
        self.table = CTkTable(master=self.tableFrame, values=value, write=True, hover_color="green", width=40)
        self.table.grid(row=0, column=0)

        # Create the resize button
        self.resizeButton = customtkinter.CTkButton(self, text="Resize", command=lambda:ResizeHandler.resizeTable(self.textVariable.get(), self.table, False))
        self.resizeButton.grid(row=1, padx=5, column=2, sticky="w")

        # Create the clear button
        self.resizeButton = customtkinter.CTkButton(self, width=50, text="Clear", command=lambda:self.table.update_values([['']]))
        self.resizeButton.grid(row=1, column=3, sticky="w")

        # Create the interpolate button
        self.interpolateButton = customtkinter.CTkButton(self, text="Interpolate", command=lambda:self.table.update_values([Interpolation.LinearFill(self.table.get_row(0))]))
        self.interpolateButton.grid(row=3, column=0, padx=5, pady=5, sticky="w")

    def resizeCallback(self, var, index, mode):
        ResizeHandler.resizeTable(self.textVariable.get(), self.table)

class SocRangeFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        self.grid_columnconfigure(3, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create the frame heading.
        self.configure(fg_color="darkslategray", corner_radius=6)
        self.frameHeading = customtkinter.CTkLabel(self, text="SoC Range", corner_radius=6)
        self.frameHeading.grid(row=0, column=0, pady=5, sticky="w")

        # Create the resolution entry label
        self.resolutionEntryLabel = customtkinter.CTkLabel(self, text="Configure Length", corner_radius=6)
        self.resolutionEntryLabel.grid(row=1, column=0, pady=5, sticky="w")

        # Create the resolution entry box
        self.textVariable = customtkinter.StringVar(self, "3")
        #self.textVariable.trace_add("write", self.resizeCallback)
        self.resolutionEntryBox = customtkinter.CTkEntry(self, textvariable=self.textVariable)
        self.resolutionEntryBox.grid(row=1, column=1, pady=5, sticky="e")

        # Create the soc range table frame
        self.tableFrame = customtkinter.CTkScrollableFrame(self, orientation="horizontal", height=30)
        self.tableFrame.grid(row=2, column=0, columnspan=4, padx=5, sticky="new")

        # Create the soc range table
        value = [[0, '', 100]]
        self.table = CTkTable(master=self.tableFrame, values=value, write=True, hover_color="green", width=40)
        self.table.grid(row=0, column=0)

        # Create the resize button
        self.resizeButton = customtkinter.CTkButton(self, text="Resize", command=lambda:ResizeHandler.resizeTable(self.textVariable.get(), self.table, True))
        self.resizeButton.grid(row=1, padx=5, column=2, sticky="w")

        # Create the clear button
        self.resizeButton = customtkinter.CTkButton(self, width=50, text="Clear", command=lambda:self.table.values.clear())
        self.resizeButton.grid(row=1, column=3, sticky="w")

        # Create the interpolate button
        self.interpolateButton = customtkinter.CTkButton(self, text="Interpolate", command=lambda:self.table.update_values([Interpolation.LinearFill(self.table.get_row(0))]))
        self.interpolateButton.grid(row=3, column=0, padx=5, pady=5, sticky="w")

    def resizeCallback(self, var, index, mode):
        ResizeHandler.resizeTable(self.textVariable.get(), self.table, True)

# Handles the resizing of the x and y values of the derate tables.
class ResizeHandler():
    socLength = 3
    temperatureLength = 3
    chargeTable = None
    dischargeTable = None

    @classmethod
    def setTableReference(cls, table, isCharge=False):
        if (isCharge):
            cls.chargeTable = table
            cls.resizeAxis(cls.chargeTable, False)
            cls.resizeAxis(cls.chargeTable, True)
        else:
            cls.dischargeTable = table
            cls.resizeAxis(cls.dischargeTable, False)
            cls.resizeAxis(cls.dischargeTable, True)

    @classmethod
    def resizeAxis(cls, table: Sheet, isXaxis=False):
        # Resize the table.
        if (isXaxis):
            print("Call to resize temperature axis")
            #table.configure(columns=cls.temperatureLength, rows=table.rows, width=40)
            #table.update_values([[]], width=40)
        else:
            print("Call to resize soc axis")
            #table.configure(rows=cls.socLength, columns=table.columns, width=40)
            #table.update_values([[]], width=40)

    @classmethod
    def setSocLength(cls, length):
        cls.socLength = length
        # Update charge and discharge table y-axis sizes.
        cls.resizeAxis(cls.chargeTable, False)
        cls.resizeAxis(cls.dischargeTable, False)

    @classmethod
    def setTemperatureLength(cls, length):
        cls.temperatureLength = length
        # Update charge and discharge table x-axis sizes.
        cls.resizeAxis(cls.chargeTable, True)
        cls.resizeAxis(cls.dischargeTable, True)

    @classmethod
    def resizeTable(cls, value: str, table: CTkTable, isSoC=False):
        # Check the data.
        if (value == ''):
            print(f"Not resizing because \"{value}\" is blank.")
            return
        if (not value.isnumeric()):
            print(f"Not resizing because \"{value}\" is not numeric.")
            return
        newInt = int(value)
        if (newInt < 2):
            print(f"Not resizing because \"{value}\" is too small.")
            return
        if (newInt > 101):
            print(f"Not resizing because \"{value}\" is too large.")
            return
        # Check for number at end.
        retainFinal = False
        oldColumns = table.columns
        finalNumber = str(table.get_row(0)[oldColumns-1])
        if (finalNumber != ''):
            if (finalNumber.isnumeric):
                retainFinal = True
        # Resize the table based on the length.
        if (isSoC):
            cls.setSocLength(newInt)
        else:
            cls.setTemperatureLength(newInt)
        # Reconfigure the columns.
        print("Call to configure, redrawing")
        table.configure(columns=newInt, width=40)
        # If we need to update the end number, do that.
        if (retainFinal):
            if (oldColumns < newInt):
                table.insert(0, oldColumns-1, '')
            table.insert(0, table.columns - 1, finalNumber)