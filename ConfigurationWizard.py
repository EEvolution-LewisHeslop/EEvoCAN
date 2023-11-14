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

# Creates the parameter subtab
class ParameterTab(customtkinter.CTkScrollableFrame):
    def __init__(self, master: customtkinter.CTkFrame):
        super().__init__(master)

        # Create the Temperature Range Frame for Charging
        self.temperatureRangeFrame = TemperatureRangeFrame(self, "Temperature Range for Charging (degC)", True)
        self.temperatureRangeFrame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        # Create the SoC Range Frame for Charging
        self.socRangeFrame = SocRangeFrame(self, "SoC Range for Charging (%)", True)
        self.socRangeFrame.grid(row=1, column=0, padx=5, pady=(0,5), sticky="nsew")

        # Create the Temperature Range Frame for Discharging
        self.temperatureRangeFrame = TemperatureRangeFrame(self, "Temperature Range for Discharging (degC)", False)
        self.temperatureRangeFrame.grid(row=2, column=0, padx=5, pady=(0,5), sticky="nsew")

        # Create the SoC Range Frame for Discharging
        self.socRangeFrame = SocRangeFrame(self, "SoC Range for Discharging (%)", False)
        self.socRangeFrame.grid(row=3, column=0, padx=5, pady=(0,5), sticky="nsew")

        # Create the voltage range frame
        self.voltageRangeFrame = VoltageRangeFrame(self)
        self.voltageRangeFrame.grid(row=4, column=0, padx=5, pady=(0,5), sticky="nsew")

        # Create the Simple parameter frame for other parameters
        self.simpleParamFrame = SimpleParamsFrame(self)
        self.simpleParamFrame.grid(row=5, column=0, padx=5, pady=(0,5), sticky="nsew")

        # Create the Slave boards parameter frame for slave board configurations
        self.slaveBoardFrame = SlaveBoardFrame(self)
        self.slaveBoardFrame.grid(row=6, column=0, padx=5, pady=(0,5), sticky="nsew")


# Creates the derate charge subtab
class ChargeTab(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        
        # Create update axis button.
        self.updateAxisButton = customtkinter.CTkButton(self, text="Update Axis", command=lambda:ResizeHandler.update_axis(True))
        self.updateAxisButton.grid(row=0, column=0, sticky="w", padx=5, pady=5)

        # Create default Table Values
        values = [['','','','','','','',''],
                  ['','','','','','','',''],
                  ['','','',230,230,'','',''],
                  ['','','','','','','',''],
                  ['','','','','','','',''],
                  ['','','','','','','',''],
                  ['','','','','','','',''],
                  ['','','','','','','',''],
                  ['','','','','','','',''],
                  ['','','','','','','',''],
                  [0,0,0,0,0,0,0,0]]

        # Create Sheet
        self.table = Sheet(self, theme="dark green", data = values)
        self.table.enable_bindings()
        self.table.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        # Assign sheet to resize handler charge table
        ResizeHandler.setTableReference(self.table, True)

        # Create interpolate button
        self.interpolateButton = customtkinter.CTkButton(self, text="Interpolate", command=lambda:self.interpolate_values(self.table))
        self.interpolateButton.grid(row=2, column=0, padx=5, pady=5)

        # Resize
        ResizeHandler.update_axis(True)
        
        # Reset Values
        self.table.set_sheet_data(values)

        # Interpolate Values
        self.interpolate_values(self.table)

    def interpolate_values(self, table: Sheet):
        oldData = table.MT.data
        newData = Interpolation.ScatteredBicubicInterpolation(oldData, len(table.MT._headers), len(table.MT._row_index))
        table.set_sheet_data(newData)
        table.set_all_column_widths(30)

# Creates the derate discharge subtab
class DischargeTab(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        
        # Create update axis button.
        self.updateAxisButton = customtkinter.CTkButton(self, text="Update Axis", command=lambda:ResizeHandler.update_axis(False))
        self.updateAxisButton.grid(row=0, column=0, sticky="w", padx=5, pady=5)

        # Create default Table Values
        values = [[0,0,0,0,0,0,0,0],
                  ['','','','','','','',''],
                  ['','','','','','','',''],
                  ['','','','','','','',''],
                  ['','','','','','','',''],
                  ['','','','','','','',''],
                  ['','','','','','','',''],
                  ['','','','','','','',''],
                  ['','','',460,460,'','',''],
                  ['','','','','','','',''],
                  ['','','','','','','','']]
        
        # Create Sheet
        self.table = Sheet(self, theme="dark green", data = values)
        self.table.enable_bindings()
        self.table.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        # Assign sheet to resize handler charge table
        ResizeHandler.setTableReference(self.table, False)

        # Create interpolate button
        self.interpolateButton = customtkinter.CTkButton(self, text="Interpolate", command=lambda:self.interpolate_values(self.table))
        self.interpolateButton.grid(row=2, column=0, padx=5, pady=5)

        # Resize
        ResizeHandler.update_axis(False)
        
        # Reset Values
        self.table.set_sheet_data(values)

        # Interpolate Values
        self.interpolate_values(self.table)

    def interpolate_values(self, table: Sheet):
        oldData = table.MT.data
        newData = Interpolation.ScatteredBicubicInterpolation(oldData, len(table.MT._headers), len(table.MT._row_index))
        table.set_sheet_data(newData)
        table.set_all_column_widths(30)

### Parameter Tab Frames ###

class TemperatureRangeFrame(customtkinter.CTkFrame):
    def __init__(self, master, labelText, isCharge=False):
        super().__init__(master)
        
        self.grid_columnconfigure(3, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Create the frame heading.
        self.configure(fg_color="darkslategray", corner_radius=6)
        self.frameHeading = customtkinter.CTkLabel(self, text=labelText, corner_radius=6)
        self.frameHeading.grid(row=0, column=0, columnspan=2, pady=5, sticky="w")

        # Create the resolution entry label
        self.resolutionEntryLabel = customtkinter.CTkLabel(self, text="Configure Length", corner_radius=6)
        self.resolutionEntryLabel.grid(row=1, column=0, pady=5, sticky="w")

        # Create the resolution entry box
        self.textVariable = customtkinter.StringVar(self, "8")
        self.resolutionEntryBox = customtkinter.CTkEntry(self, textvariable=self.textVariable)
        self.resolutionEntryBox.grid(row=1, column=1, pady=5, sticky="e")

        # Create the temperature range table frame
        self.tableFrame = customtkinter.CTkScrollableFrame(self, orientation="horizontal", height=30)
        self.tableFrame.grid(row=2, column=0, columnspan=4, padx=5, sticky="new")

        # Create the temperature range table
        value = [[-10, 0, 10, 20, 30, 40, 50, 60]]
        self.table = CTkTable(master=self.tableFrame, values=value, write=True, hover_color="green", width=40)
        self.table.grid(row=0, column=0)

        # Set the reference to the axis in the resizer
        ResizeHandler.setAxisReference(self.table, False, isCharge)

        # Create the resize button
        self.resizeButton = customtkinter.CTkButton(self, text="Resize", command=lambda:ResizeHandler.resizeTable(self.textVariable.get(), False, isCharge))
        self.resizeButton.grid(row=1, padx=5, column=2, sticky="w")

        # Create the clear button
        self.resizeButton = customtkinter.CTkButton(self, width=50, text="Clear", command=lambda:self.table.update_values([['']]))
        self.resizeButton.grid(row=1, column=3, sticky="w")

        # Create the interpolate button
        self.interpolateButton = customtkinter.CTkButton(self, text="Interpolate", command=lambda:self.table.update_values([Interpolation.LinearFill(self.table.get_row(0))]))
        self.interpolateButton.grid(row=3, column=0, padx=5, pady=5, sticky="w")

class SocRangeFrame(customtkinter.CTkFrame):
    def __init__(self, master, labelText, isCharge=False):
        super().__init__(master)
        
        self.grid_columnconfigure(3, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create the frame heading.
        self.configure(fg_color="darkslategray", corner_radius=6)
        self.frameHeading = customtkinter.CTkLabel(self, text=labelText, corner_radius=6)
        self.frameHeading.grid(row=0, column=0, columnspan=2, pady=5, sticky="w")

        # Create the resolution entry label
        self.resolutionEntryLabel = customtkinter.CTkLabel(self, text="Configure Length", corner_radius=6)
        self.resolutionEntryLabel.grid(row=1, column=0, pady=5, sticky="w")

        # Create the resolution entry box
        self.textVariable = customtkinter.StringVar(self, "11")
        self.resolutionEntryBox = customtkinter.CTkEntry(self, textvariable=self.textVariable)
        self.resolutionEntryBox.grid(row=1, column=1, pady=5, sticky="e")

        # Create the soc range table frame
        self.tableFrame = customtkinter.CTkScrollableFrame(self, orientation="horizontal", height=30)
        self.tableFrame.grid(row=2, column=0, columnspan=4, padx=5, sticky="new")

        # Create the soc range table
        value = [[0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]]
        self.table = CTkTable(master=self.tableFrame, values=value, write=True, hover_color="green", width=40)
        self.table.grid(row=0, column=0)

        # Set the reference to the axis in the resizer
        ResizeHandler.setAxisReference(self.table, True, isCharge)

        # Create the resize button
        self.resizeButton = customtkinter.CTkButton(self, text="Resize", command=lambda:ResizeHandler.resizeTable(self.textVariable.get(), True, isCharge))
        self.resizeButton.grid(row=1, padx=5, column=2, sticky="w")

        # Create the clear button
        self.resizeButton = customtkinter.CTkButton(self, width=50, text="Clear", command=lambda:self.table.update_values([['']]))
        self.resizeButton.grid(row=1, column=3, sticky="w")

        # Create the interpolate button
        self.interpolateButton = customtkinter.CTkButton(self, text="Interpolate", command=lambda:self.table.update_values([Interpolation.LinearFill(self.table.get_row(0))]))
        self.interpolateButton.grid(row=3, column=0, padx=5, pady=5, sticky="w")

class SimpleParamsFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        self.configure(fg_color="darkslategray", corner_radius=6)
        self.frameHeading = customtkinter.CTkLabel(self, text="Basic Parameter Configuration", corner_radius=6)
        self.frameHeading.grid(row=0, column=0, columnspan=2, pady=5, sticky="w")

        # Add min cell voltage entry.
        self.minCellVoltageLimit = customtkinter.StringVar(self, "3.2")
        self.minCellVoltageLimitLabel = customtkinter.CTkLabel(self, text="Minimum Cell Voltage Limit (V)")
        self.minCellVoltageLimitLabel.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.minCellVoltageLimitTextEntry = customtkinter.CTkEntry(self, textvariable=self.minCellVoltageLimit)
        self.minCellVoltageLimitTextEntry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Add max cell voltage entry.
        self.maxCellVoltageLimit = customtkinter.StringVar(self, "4.35")
        self.maxCellVoltageLimitLabel = customtkinter.CTkLabel(self, text="Maximum Cell Voltage Limit (V)")
        self.maxCellVoltageLimitLabel.grid(row=2, column=0, padx=5, pady=(0,5), sticky="w")
        self.maxCellVoltageLimitTextEntry = customtkinter.CTkEntry(self, textvariable=self.maxCellVoltageLimit)
        self.maxCellVoltageLimitTextEntry.grid(row=2, column=1, padx=5, pady=(0,5), sticky="w")

        # Add min cell temperature entry.
        self.minCellTemperatureLimit = customtkinter.StringVar(self, "-30")
        self.minCellTemperatureLimitLabel = customtkinter.CTkLabel(self, text="Minimum Cell Temperature Limit (degC)")
        self.minCellTemperatureLimitLabel.grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.minCellTemperatureLimitTextEntry = customtkinter.CTkEntry(self, textvariable=self.minCellTemperatureLimit)
        self.minCellTemperatureLimitTextEntry.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        # Add max cell temperature entry.
        self.maxCellTemperatureLimit = customtkinter.StringVar(self, "60")
        self.maxCellTemperatureLimitLabel = customtkinter.CTkLabel(self, text="Maximum Cell Temperature Limit (degC)")
        self.maxCellTemperatureLimitLabel.grid(row=4, column=0, padx=5, pady=(0,5), sticky="w")
        self.maxCellTemperatureLimitTextEntry = customtkinter.CTkEntry(self, textvariable=self.maxCellTemperatureLimit)
        self.maxCellTemperatureLimitTextEntry.grid(row=4, column=1, padx=5, pady=(0,5), sticky="w")

        # Add max discharging current limit.
        self.maxDischargingCurrentLimit = customtkinter.StringVar(self, "2000")
        self.maxDischargingCurrentLimitLabel = customtkinter.CTkLabel(self, text="Maximum Discharging Current Limit (A)")
        self.maxDischargingCurrentLimitLabel.grid(row=5, column=0, padx=5, pady=5, sticky="w")
        self.maxDischargingCurrentLimitTextEntry = customtkinter.CTkEntry(self, textvariable=self.maxDischargingCurrentLimit)
        self.maxDischargingCurrentLimitTextEntry.grid(row=5, column=1, padx=5, pady=5, sticky="w")

        # Add max charging current limit.
        self.maxChargingCurrentLimit = customtkinter.StringVar(self, "510")
        self.maxChargingCurrentLimitLabel = customtkinter.CTkLabel(self, text="Maximum Charging Current Limit (A)")
        self.maxChargingCurrentLimitLabel.grid(row=6, column=0, padx=5, pady=(0,5), sticky="w")
        self.maxChargingCurrentLimitTextEntry = customtkinter.CTkEntry(self, textvariable=self.maxChargingCurrentLimit)
        self.maxChargingCurrentLimitTextEntry.grid(row=6, column=1, padx=5, pady=(0,5), sticky="w")

        # Add max charging current limit - charger.
        self.maxChargingCurrentLimitCharger = customtkinter.StringVar(self, "250")
        self.maxChargingCurrentLimitChargerLabel = customtkinter.CTkLabel(self, text="Maximum Charging Current Limit on Charger (A)")
        self.maxChargingCurrentLimitChargerLabel.grid(row=7, column=0, padx=5, pady=(0,5), sticky="w")
        self.maxChargingCurrentLimitChargerTextEntry = customtkinter.CTkEntry(self, textvariable=self.maxChargingCurrentLimitCharger)
        self.maxChargingCurrentLimitChargerTextEntry.grid(row=7, column=1, padx=5, pady=(0,5), sticky="w")
        
        # Add soft discharging current limit.
        self.softDischargingCurrentLimit = customtkinter.StringVar(self, "1200")
        self.softDischargingCurrentLimitLabel = customtkinter.CTkLabel(self, text="Soft Discharging Current Limit (A)")
        self.softDischargingCurrentLimitLabel.grid(row=8, column=0, padx=5, pady=5, sticky="w")
        self.softDischargingCurrentLimitTextEntry = customtkinter.CTkEntry(self, textvariable=self.softDischargingCurrentLimit)
        self.softDischargingCurrentLimitTextEntry.grid(row=8, column=1, padx=5, pady=5, sticky="w")

        # Add soft charging current limit.
        self.softChargingCurrentLimit = customtkinter.StringVar(self, "245")
        self.softChargingCurrentLimitLabel = customtkinter.CTkLabel(self, text="Soft Charging Current Limit (A)")
        self.softChargingCurrentLimitLabel.grid(row=9, column=0, padx=5, pady=(0,5), sticky="w")
        self.softChargingCurrentLimitTextEntry = customtkinter.CTkEntry(self, textvariable=self.softChargingCurrentLimit)
        self.softChargingCurrentLimitTextEntry.grid(row=9, column=1, padx=5, pady=(0,5), sticky="w")

        # Add customer discharging current limit.
        self.customerDischargingCurrentLimit = customtkinter.StringVar(self, "1080")
        self.customerDischargingCurrentLimitLabel = customtkinter.CTkLabel(self, text="Customer Discharging Current Limit (A)")
        self.customerDischargingCurrentLimitLabel.grid(row=10, column=0, padx=5, pady=5, sticky="w")
        self.customerDischargingCurrentLimitTextEntry = customtkinter.CTkEntry(self, textvariable=self.customerDischargingCurrentLimit)
        self.customerDischargingCurrentLimitTextEntry.grid(row=10, column=1, padx=5, pady=5, sticky="w")

        # Add customer charging current limit.
        self.customerChargingCurrentLimit = customtkinter.StringVar(self, "140")
        self.customerChargingCurrentLimitLabel = customtkinter.CTkLabel(self, text="Customer Charging Current Limit (A)")
        self.customerChargingCurrentLimitLabel.grid(row=11, column=0, padx=5, pady=(0,5), sticky="w")
        self.customerChargingCurrentLimitTextEntry = customtkinter.CTkEntry(self, textvariable=self.customerChargingCurrentLimit)
        self.customerChargingCurrentLimitTextEntry.grid(row=11, column=1, padx=5, pady=(0,5), sticky="w")

        # Add number of drive motors.
        self.driveMotorCount = customtkinter.StringVar(self, "1")
        self.driveMotorCountLabel = customtkinter.CTkLabel(self, text="Number of drive motors")
        self.driveMotorCountLabel.grid(row=12, column=0, padx=5, pady=5, sticky="w")
        self.driveMotorCountTextEntry = customtkinter.CTkEntry(self, textvariable=self.driveMotorCount)
        self.driveMotorCountTextEntry.grid(row=12, column=1, padx=5, pady=5, sticky="w")

        # Add charge capacity.
        self.chargeCapacity = customtkinter.StringVar(self, "158.8")
        self.chargeCapacityLabel = customtkinter.CTkLabel(self, text="Charge Capacity (Ah)")
        self.chargeCapacityLabel.grid(row=13, column=0, padx=5, pady=5, sticky="w")
        self.chargeCapacityTextEntry = customtkinter.CTkEntry(self, textvariable=self.chargeCapacity)
        self.chargeCapacityTextEntry.grid(row=13, column=1, padx=5, pady=5, sticky="w")

        # Add customer 0 soc.
        self.customerZeroSoc = customtkinter.StringVar(self, "10")
        self.customerZeroSocLabel = customtkinter.CTkLabel(self, text="Customer 0% SoC (% of true SoC)")
        self.customerZeroSocLabel.grid(row=14, column=0, padx=5, pady=(0,5), sticky="w")
        self.customerZeroSocTextEntry = customtkinter.CTkEntry(self, textvariable=self.customerZeroSoc)
        self.customerZeroSocTextEntry.grid(row=14, column=1, padx=5, pady=(0,5), sticky="w")

        # Add customer 100 soc.
        self.customerFullSoc = customtkinter.StringVar(self, "95")
        self.customerFullSocLabel = customtkinter.CTkLabel(self, text="Customer 100% SoC (% of true SoC)")
        self.customerFullSocLabel.grid(row=15, column=0, padx=5, pady=(0,5), sticky="w")
        self.customerFullSocTextEntry = customtkinter.CTkEntry(self, textvariable=self.customerFullSoc)
        self.customerFullSocTextEntry.grid(row=15, column=1, padx=5, pady=(0,5), sticky="w")

        # Add end of charge soc.
        self.endChargeSoc = customtkinter.StringVar(self, "100")
        self.endChargeSocLabel = customtkinter.CTkLabel(self, text="End of charge SoC (%)")
        self.endChargeSocLabel.grid(row=16, column=0, padx=5, pady=(0,5), sticky="w")
        self.endChargeSocTextEntry = customtkinter.CTkEntry(self, textvariable=self.endChargeSoc)
        self.endChargeSocTextEntry.grid(row=16, column=1, padx=5, pady=(0,5), sticky="w")

        # Add obc charge current limits.
        self.obcChargeAcCurrentLimit = customtkinter.StringVar(self, "32")
        self.obcChargeAcCurrentLimitLabel = customtkinter.CTkLabel(self, text="OBC Charging AC Current Limit (A)")
        self.obcChargeAcCurrentLimitLabel.grid(row=17, column=0, padx=5, pady=5, sticky="w")
        self.obcChargeAcCurrentLimitTextEntry = customtkinter.CTkEntry(self, textvariable=self.obcChargeAcCurrentLimit)
        self.obcChargeAcCurrentLimitTextEntry.grid(row=17, column=1, padx=5, pady=5, sticky="w")

        # Add obc charge current limits.
        self.obcChargeDcCurrentLimit = customtkinter.StringVar(self, "40")
        self.obcChargeDcCurrentLimitLabel = customtkinter.CTkLabel(self, text="OBC Charging DC Current Limit (A)")
        self.obcChargeDcCurrentLimitLabel.grid(row=18, column=0, padx=5, pady=5, sticky="w")
        self.obcChargeDcCurrentLimitTextEntry = customtkinter.CTkEntry(self, textvariable=self.obcChargeDcCurrentLimit)
        self.obcChargeDcCurrentLimitTextEntry.grid(row=18, column=1, padx=5, pady=5, sticky="w")

        # Add can message timeout.
        self.canMessageTimeout = customtkinter.StringVar(self, "100")
        self.canMessageTimeoutLimitLabel = customtkinter.CTkLabel(self, text="CAN Message Timeout (ms)")
        self.canMessageTimeoutLimitLabel.grid(row=19, column=0, padx=5, pady=5, sticky="w")
        self.canMessageTimeoutLimitTextEntry = customtkinter.CTkEntry(self, textvariable=self.canMessageTimeout)
        self.canMessageTimeoutLimitTextEntry.grid(row=19, column=1, padx=5, pady=5, sticky="w")

class SlaveBoardFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.grid_columnconfigure(3, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create the frame heading.
        self.configure(fg_color="darkslategray", corner_radius=6)
        self.frameHeading = customtkinter.CTkLabel(self, text="Slave Board Configuration", corner_radius=6)
        self.frameHeading.grid(row=0, column=0, columnspan=2, pady=5, sticky="w")

        # Create the resolution entry label
        self.resolutionEntryLabel = customtkinter.CTkLabel(self, text="Configure Number of Slaves", corner_radius=6)
        self.resolutionEntryLabel.grid(row=1, column=0, pady=5, sticky="w")

        # Create the resolution entry box
        self.textVariable = customtkinter.StringVar(self, "10")
        self.resolutionEntryBox = customtkinter.CTkEntry(self, textvariable=self.textVariable)
        self.resolutionEntryBox.grid(row=1, column=1, pady=5, sticky="e")

        # Create the slave cellcount table frame
        self.tableFrame = customtkinter.CTkScrollableFrame(self, orientation="horizontal", height=60)
        self.tableFrame.grid(row=2, column=0, columnspan=4, padx=5, pady=(0,5), sticky="new")

        # Create the slave cellcount table header
        self.slaveCellCountHeader = customtkinter.CTkLabel(master=self.tableFrame, text="Cells per Slave")
        self.slaveCellCountHeader.grid(row=0, column=0, padx=5, sticky="w")

        # Create the slave cellcount table
        value = [[11, 12, 11, 12, 11, 12, 11, 12, 11, 12]]
        self.table = CTkTable(master=self.tableFrame, values=value, write=True, hover_color="green", width=40)
        self.table.grid(row=1, column=0)

        # Create the resize button
        self.resizeButton = customtkinter.CTkButton(self, text="Resize", command=lambda:self.table.configure(columns=int(self.textVariable.get()), width=40))
        self.resizeButton.grid(row=1, padx=5, column=2, sticky="w")

        # Create the clear button
        self.resizeButton = customtkinter.CTkButton(self, width=50, text="Clear", command=lambda:self.table.update_values([['']]))
        self.resizeButton.grid(row=1, column=3, sticky="w")

        # Add thermistors per slave input
        self.thermistorsPerSlave = customtkinter.StringVar(self, "12")
        self.thermistorsPerSlaveLabel = customtkinter.CTkLabel(self, text="Thermistors per Slave")
        self.thermistorsPerSlaveLabel.grid(row=13, column=0, padx=5, pady=(0,5), sticky="w")
        self.thermistorsPerSlaveTextEntry = customtkinter.CTkEntry(self, textvariable=self.thermistorsPerSlave)
        self.thermistorsPerSlaveTextEntry.grid(row=13, column=1, padx=5, pady=(0,5), sticky="w")

class VoltageRangeFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.grid_columnconfigure(3, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create the frame heading.
        self.configure(fg_color="darkslategray", corner_radius=6)
        self.frameHeading = customtkinter.CTkLabel(self, text="Voltage Range (V)", corner_radius=6)
        self.frameHeading.grid(row=0, column=0, columnspan=2, pady=5, sticky="w")

        # Create the resolution entry label
        self.resolutionEntryLabel = customtkinter.CTkLabel(self, text="Configure Size of Range", corner_radius=6)
        self.resolutionEntryLabel.grid(row=1, column=0, pady=5, sticky="w")

        # Create the resolution entry box
        self.textVariable = customtkinter.StringVar(self, "101")
        self.resolutionEntryBox = customtkinter.CTkEntry(self, textvariable=self.textVariable)
        self.resolutionEntryBox.grid(row=1, column=1, pady=5, sticky="e")

        # Create the slave cellcount table frame
        self.tableFrame = customtkinter.CTkScrollableFrame(self, orientation="horizontal", height=30)
        self.tableFrame.grid(row=2, column=0, columnspan=4, padx=5, pady=(0,5), sticky="new")

        # Create the slave cellcount table
        value = [[3.400, 3.415, 3.431, 3.447, 3.462, 3.478, 3.487, 3.495, 3.504, 3.512, 3.521, 3.530, 3.539, 3.547, 3.556, 3.565, 3.571, 3.578, 3.585, 3.592, 3.598, 3.604, 3.609, 3.614, 3.620, 3.625, 3.628, 3.632, 3.635, 3.638, 3.642, 3.645, 3.648, 3.652, 3.655, 3.658, 3.661, 3.664, 3.667, 3.671, 3.674, 3.679, 3.684, 3.689, 3.694, 3.699, 3.706, 3.713, 3.720, 3.727, 3.734, 3.746, 3.758, 3.770, 3.782, 3.794, 3.806, 3.819, 3.831, 3.844, 3.856, 3.867, 3.877, 3.887, 3.897, 3.907, 3.916, 3.925, 3.935, 3.948, 3.963, 3.974, 3.986, 3.997, 4.009, 4.020, 4.032, 4.044, 4.056, 4.068, 4.080, 4.091, 4.103, 4.114, 4.126, 4.137, 4.146, 4.155, 4.163, 4.172, 4.181, 4.191, 4.202, 4.212, 4.222, 4.233, 4.243, 4.253, 4.263, 4.274, 4.320]]
        self.table = CTkTable(master=self.tableFrame, values=value, write=True, hover_color="green", width=40)
        self.table.grid(row=0, column=0)

        # Create the resize button
        self.resizeButton = customtkinter.CTkButton(self, text="Resize", command=lambda:self.table.configure(columns=int(self.textVariable.get()), width=40))
        self.resizeButton.grid(row=1, padx=5, column=2, sticky="w")

        # Create the clear button
        self.resizeButton = customtkinter.CTkButton(self, width=50, text="Clear", command=lambda:self.table.update_values([['']]))
        self.resizeButton.grid(row=1, column=3, sticky="w")

        # Create the interpolate button
        self.interpolateButton = customtkinter.CTkButton(self, text="Interpolate", command=lambda:self.table.update_values([Interpolation.LinearFill(self.table.get_row(0))]))
        self.interpolateButton.grid(row=3, column=0, padx=5, pady=5, sticky="w")


# Handles the resizing of the x and y values of the derate tables.
class ResizeHandler():
    chargeSocAxis:CTkTable = None
    chargeTemperatureAxis:CTkTable = None
    dischargeSocAxis:CTkTable = None
    dischargeTemperatureAxis:CTkTable = None
    chargeTable:Sheet = None
    dischargeTable:Sheet = None

    @classmethod
    def setAxisReference(cls, axis, isSoc=False, isCharge=False):
        if (isSoc):
            if (isCharge):
                cls.chargeSocAxis = axis
            else:
                cls.dischargeSocAxis = axis
        else:
            if (isCharge):
                cls.chargeTemperatureAxis = axis
            else:
                cls.dischargeTemperatureAxis = axis

    @classmethod
    def setTableReference(cls, table, isCharge=False):
        if (isCharge):
            cls.chargeTable = table
        else:
            cls.dischargeTable = table

    @classmethod
    def update_axis(cls, isCharge=False):
        # Check to see if the soc and temp axis have data everywhere.
        if (isCharge):
            for i in cls.chargeSocAxis.values[0]:
                if (str(i).strip() == ''):
                    print("Failed to update axis: Charge SoC Axis Incomplete")
                    return
            for i in cls.chargeTemperatureAxis.values[0]:
                if (str(i).strip() == ''):
                    print("Failed to update axis: Charge Temperature Axis Incomplete")
                    return
        else:
            for i in cls.dischargeSocAxis.values[0]:
                if (str(i).strip() == ''):
                    print("Failed to update axis: Discharge SoC Axis Incomplete")
                    return
            for i in cls.dischargeTemperatureAxis.values[0]:
                if (str(i).strip() == ''):
                    print("Failed to update axis: Discharge Temperature Axis Incomplete")
                    return
                
        # Update the relevant table.
        if (isCharge):
            cls.chargeTable.headers(newheaders=cls.chargeTemperatureAxis.values[0], redraw=True)
            cls.chargeTable.row_index(newindex=cls.chargeSocAxis.values[0], redraw=True)
            cls.chargeTable.set_sheet_data(data=[[]])
            cls.chargeTable.set_all_column_widths(30)
        else:
            cls.dischargeTable.headers(newheaders=cls.dischargeTemperatureAxis.values[0], redraw=True)
            cls.dischargeTable.row_index(newindex=cls.dischargeSocAxis.values[0], redraw=True)
            cls.dischargeTable.set_sheet_data(data=[[]])
            cls.dischargeTable.set_all_column_widths(30)

    @classmethod
    def resizeTable(cls, value: str, isSoC=False, isCharge=False):
        if (isSoC):
            if (isCharge):
                table = cls.chargeSocAxis
            else:
                table = cls.dischargeSocAxis
        else:
            if (isCharge):
                table = cls.chargeTemperatureAxis
            else:
                table = cls.dischargeTemperatureAxis

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
        # Reconfigure the columns.
        print("Call to configure, redrawing")
        table.configure(columns=newInt, width=40)
        # If we need to update the end number, do that.
        if (retainFinal):
            if (oldColumns < newInt):
                table.insert(0, oldColumns-1, '')
            table.insert(0, table.columns - 1, finalNumber)
        # Update big tables
        cls.update_axis(isCharge)