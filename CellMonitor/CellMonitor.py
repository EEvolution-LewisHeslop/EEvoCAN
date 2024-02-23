from HwManager import HwManager
from CommandSystem import CommandSystem
import customtkinter
import canopen
from tksheet import Sheet
import time
import threading
from statistics import mean
import tk_tools
import os
import datetime

# Creates the basic tab
class CellMonitorTab(customtkinter.CTkFrame):
    hwManager: HwManager = None
    sendNetwork: canopen.Network = None
    monitoringActive = False
    network = None
    mcuCount = 0
    voltages = {}
    temperatures = {}
    logging = False
    loggingRequested = False
    snapshotRequested = False
    logPath = "logs/testinterfaces"
    logFile = None
    def __init__(
            self,
            master: customtkinter.CTkFrame,
            hwManager: HwManager,
            commandSystem: CommandSystem):
        super().__init__(master)
        self.hwManager = hwManager
        if (len(self.hwManager.networkList) > 0):
            self.network = self.hwManager.networkList[0][3]
        self.grid_rowconfigure(3, weight=1)
        self.grid_rowconfigure(4, weight=1)

        # Create Toggle
        self.monitorToggle = customtkinter.CTkSwitch(self, text="Enable Monitoring", command=lambda:self.toggle_monitoring())
        self.monitorToggle.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky='nw')

        # Create Start Logging Button
        self.startLoggingButton = customtkinter.CTkButton(self, text="Start Logging", command=lambda:self.requestLogging())
        self.startLoggingButton.grid(row=0, column=2, padx=5, pady=5, sticky='nw')
                
        # Create Stop Logging Button
        self.stopLoggingButton = customtkinter.CTkButton(self, text="Stop Logging", command=lambda:self.stopLogging())
        self.stopLoggingButton.grid(row=0, column=3, padx=5, pady=5, sticky='nw')

        # Create Logging LED
        self.loggingLedLabel = customtkinter.CTkLabel(self, text="Logging:")
        self.loggingLedLabel.grid(row=0, column=4, padx=5, pady=5, sticky='nw')
        self.loggingLed = tk_tools.Led(self, size=40, bg="#2b2b2b")
        self.loggingLed.grid(row=0, column=4, padx=70, pady=5, sticky='nw')
        self.loggingLed.to_green(False)

        # Create Snapshot Button
        self.snapshotButton = customtkinter.CTkButton(self, text="Request Snapshot", command=lambda:self.requestSnapshot())
        self.snapshotButton.grid(row=0, column=5, padx=5, pady=5, sticky='nw')

        # Create MCU Count Readout
        self.mcuCountLabel = customtkinter.CTkLabel(self, text="MCU Count:")
        self.mcuCountLabel.grid(row=1, column=0, padx=5, sticky='nw')
        self.mcuCountValue = customtkinter.CTkLabel(self, text="-")
        self.mcuCountValue.grid(row=2, column=0, padx=5, sticky='nw')

        # Create Min Cell Voltage Readout
        self.minCellVoltageLabel = customtkinter.CTkLabel(self, text="Minimum Cell Voltage:")
        self.minCellVoltageLabel.grid(row=1, column=1, padx=5, sticky='nw')
        self.minCellVoltage = customtkinter.CTkLabel(self, text="-")
        self.minCellVoltage.grid(row=2, column=1, padx=5, sticky='nw')
        
        # Create Min Cell Temperature Readout
        self.minCellTemperatureLabel = customtkinter.CTkLabel(self, text="Minimum Cell Temperature:")
        self.minCellTemperatureLabel.grid(row=1, column=2, padx=5, sticky='nw')
        self.minCellTemperature = customtkinter.CTkLabel(self, text="-")
        self.minCellTemperature.grid(row=2, column=2, padx=5, sticky='nw')

        # Create Max Cell Voltage Readout
        self.maxCellVoltageLabel = customtkinter.CTkLabel(self, text="Maximum Cell Voltage:")
        self.maxCellVoltageLabel.grid(row=1, column=3, padx=5, sticky='nw')
        self.maxCellVoltage = customtkinter.CTkLabel(self, text="-")
        self.maxCellVoltage.grid(row=2, column=3, padx=5, sticky='nw')

        # Create Max Cell Temperature Readout
        self.maxCellTemperatureLabel = customtkinter.CTkLabel(self, text="Maximum Cell Temperature:")
        self.maxCellTemperatureLabel.grid(row=1, column=4, padx=5, sticky='nw')
        self.maxCellTemperature = customtkinter.CTkLabel(self, text="-")
        self.maxCellTemperature.grid(row=2, column=4, padx=5, sticky='nw')

        # Create Average Cell Voltage Readout
        self.averageCellVoltageLabel = customtkinter.CTkLabel(self, text="Average Cell Voltage:")
        self.averageCellVoltageLabel.grid(row=1, column=5, padx=5, sticky='nw')
        self.averageCellVoltage = customtkinter.CTkLabel(self, text="-")
        self.averageCellVoltage.grid(row=2, column=5, padx=5, sticky='nw')

        # Create Average Cell Temperature Readout
        self.averageCellTemperatureLabel = customtkinter.CTkLabel(self, text="Average Cell Temperature:")
        self.averageCellTemperatureLabel.grid(row=1, column=6, padx=5, sticky='nw')
        self.averageCellTemperature = customtkinter.CTkLabel(self, text="-")
        self.averageCellTemperature.grid(row=2, column=6, padx=5, sticky='nw')

        # Create Battery Total Voltage Readout
        self.batteryTotalVoltageLabel = customtkinter.CTkLabel(self, text="Battery Total Voltage:")
        self.batteryTotalVoltageLabel.grid(row=1, column=7, padx=5, sticky='nw')
        self.batteryTotalVoltage = customtkinter.CTkLabel(self, text="-")
        self.batteryTotalVoltage.grid(row=2, column=7, padx=5, sticky='nw')

        # Create Cell Voltage Deviation Readout
        self.cellVoltageDeviationLabel = customtkinter.CTkLabel(self, text="Cell Voltage Deviation:")
        self.cellVoltageDeviationLabel.grid(row=1, column=8, padx=5, sticky='nw')
        self.cellVoltageDeviation = customtkinter.CTkLabel(self, text="-")
        self.cellVoltageDeviation.grid(row=2, column=8, padx=5, sticky='nw')

        # Resize columns
        col_count, row_count = self.grid_size()
        for col in range(col_count):
            self.grid_columnconfigure(col, weight=1, minsize=20)

        # Create Voltage Sheet
        self.voltageSheet = Sheet(self, theme="dark green")
        self.voltageSheet.MT.default_column_width = 70
        self.voltageSheet.enable_bindings()
        self.voltageSheet.grid(
            row=3,
            column=0,
            columnspan=col_count,
            sticky="nsew",
            padx=5,
            pady=(0, 5))
        self.voltageSheet.headers(
            newheaders=["MCU 1"])
        self.voltageSheet.edit_bindings(False)

        # Create Temperature Sheet
        self.temperatureSheet = Sheet(self, theme="dark green")
        self.temperatureSheet.MT.default_column_width = 70
        self.temperatureSheet.enable_bindings()
        self.temperatureSheet.grid(
            row=4,
            column=0,
            columnspan=col_count,
            sticky="nsew",
            padx=5,
            pady=(0, 5))
        self.temperatureSheet.headers(
            newheaders=["MCU 1"])
        self.temperatureSheet.edit_bindings(False)

    def requestLogging(self):
        self.loggingRequested = True

    def stopLogging(self):
        self.logging = False

    def requestSnapshot(self):
        self.snapshotRequested = True

    # Switches on and off (todo) the monitoring of cells.
    def toggle_monitoring(self):
        if (self.monitoringActive):
            # TODO: We are monitoring already, switch it off.
            print("Not implemented.")
        else:
            # Loop through all of the relevant voltage ids and register relevant callbacks.
            self.monitoringActive = True
            voltageRange = range(0x010, 0x104)
            for id in voltageRange:
                mcuNumber = int(id / 16)
                cellIndexes = [((id % 16) * 3) + x for x in range(3)]
                if (self.network is not None):
                    self.network.subscribe(
                        can_id=id,
                        callback=lambda can_id, data, timestamp, m=mcuNumber, c=cellIndexes:
                            self.voltage_callback(can_id, data, timestamp, m, c))
            # Loop through all of the relevant temperature ids and register relevant callbacks.
            TemperatureRange = range(0x411, 0x503)
            for id in TemperatureRange:
                lastDigit = hex(id)[-1]
                if (lastDigit == '1' or lastDigit == '2'):
                    mcuNumber = int(id / 16) - 64
                    cellIndexes = [(((id % 16) - 1) * 6) + x for x in range(6)]
                    if (self.network is not None):
                        self.network.subscribe(
                            can_id=id,
                            callback=lambda x, y, z, m=mcuNumber, c=cellIndexes:
                                self.temperature_callback(x, y, z, m, c))
            # Add the required rows
            for row in range(12):
                self.voltageSheet.insert_row(redraw=False)
                self.temperatureSheet.insert_row(redraw=False)

            # Periodically update UI.
            threading.Thread(target=lambda:self.sheet_updater(), daemon=True).start()
    
    # Updates the fields at the top periodically
    def sheet_updater(self):
        while(True):
            # Wait before updating again.
            time.sleep(0.05)

            # Update MCU Count Readout
            self.mcuCountValue.configure(text=f"{self.mcuCount}")

            # Get all cell voltages
            allVoltages = []
            for value in self.voltages.values():
                allVoltages.extend(value)
            cellVoltages = [voltage for voltage in allVoltages if voltage > 0.1 and voltage < 7]

            # Get all cell temperatures
            allTemperatures = []
            for value in self.temperatures.values():
                allTemperatures.extend(value)
            cellTemperatures = [temperature for temperature in allTemperatures if temperature > -40 and temperature < 85]

            # Check that there are some values available
            if (len(cellVoltages) < 1 or len(cellTemperatures) < 1):
                continue
            
            # See if logging has been requested
            if (self.loggingRequested):
                self.loggingRequested = False
                self.logging = True
                self.create_logfile(self.mcuCount)

            # See if we are logging
            if (self.logging):
                self.loggingLed.to_green(True)
                self.log(cellVoltages, cellTemperatures)

            # See if we've been asked to take a snapshot
            if (self.snapshotRequested):
                self.snapshotRequested = False
                self.create_snapshot(self.mcuCount, cellVoltages, cellTemperatures)

            # Update Min Cell Voltage Readout
            self.minCellVoltage.configure(text=f"{min(cellVoltages)}")
            
            # Update Min Cell Temperature Readout
            self.minCellTemperature.configure(text=f"{min(cellTemperatures)}")

            # Update Max Cell Voltage Readout
            self.maxCellVoltage.configure(text=f"{max(cellVoltages)}")

            # Update Max Cell Temperature Readout
            self.maxCellTemperature.configure(text=f"{max(cellTemperatures)}")

            # Update Average Cell Voltage Readout
            self.averageCellVoltage.configure(text=f"{mean(cellVoltages)}")

            # Update Average Cell Temperature Readout
            self.averageCellTemperature.configure(text=f"{mean(cellTemperatures)}")

            # Update Battery Total Voltage Readout
            self.batteryTotalVoltage.configure(text=f"{sum(cellVoltages)}")

            # Update Cell Voltage Deviation Readout
            self.cellVoltageDeviation.configure(text=f"{max(cellVoltages)-min(cellVoltages)}")

    def create_logfile(self, mcuCount):
        if (not os.path.isdir(self.logPath)):
            # Create the dir
            os.mkdir(self.logPath)
        # Create the file
        self.logFile = datetime.datetime.now().strftime("CELL_LOG_%y_%m_%d_%H_%M_%S")
        file = open(os.path.join(self.logPath, self.logFile))
        # Create the header
        headerString = "Time,"
        for mcu in range(1, mcuCount+1):
            for cell in range(1, 13):
                headerString += f"Module {mcu} Cell {cell} Voltage,"
        for mcu in range(1, mcuCount+1):
            for cell in range(1, 13):
                headerString += f"Module {mcu} Cell {cell} Temperature,"
        headerString += "Modules Connected,"
        headerString += "Battery Temperature,"
        headerString += "Battery Minimum Cell Voltage,"
        headerString += "Battery Maximum Cell Voltage,"
        headerString += "Battery Average Cell Voltage,"
        headerString += "Battery Total Voltage,"
        headerString += "Cell Voltage Deviation"
        file.write(headerString)
        file.close()

    def log(self, cellVoltages, cellTemperatures):
        # open the file
        file = open(os.path.join(self.logPath, self.logFile))
        # Create the row
        rowString = datetime.time.isoformat(timespec='milliseconds')
        rowString += ','
        for voltage in cellVoltages:
            rowString += f"{voltage},"
        for temperature in cellTemperatures:
            rowString += f"{temperature}"
        rowString += f"{self.mcuCount},"
        rowString += f"{mean(cellTemperatures)}"
        rowString += f"{min(cellVoltages)}"
        rowString += f"{max(cellVoltages)}"
        rowString += f"{mean(cellVoltages)}"
        rowString += f"{sum(cellVoltages)}"
        rowString += f"{max(cellVoltages)-min(cellVoltages)}"
        file.write(rowString)
        file.close()

    def create_snapshot(self, mcuCount, cellVoltages, cellTemperatures):
        if (not os.path.isdir(self.logPath)):
            # Create the dir
            os.mkdir(self.logPath)
        # Create the file
        snapFile = datetime.datetime.now().strftime("CELL_SNAP_%y_%m_%d_%H_%M_%S")
        file = open(os.path.join(self.logPath, snapFile))
        # Create the header
        headerString = "Time,"
        for mcu in range(1, mcuCount+1):
            for cell in range(1, 13):
                headerString += f"Module {mcu} Cell {cell} Voltage,"
        for mcu in range(1, mcuCount+1):
            for cell in range(1, 13):
                headerString += f"Module {mcu} Cell {cell} Temperature,"
        headerString += "Modules Connected,"
        headerString += "Battery Temperature,"
        headerString += "Battery Minimum Cell Voltage,"
        headerString += "Battery Maximum Cell Voltage,"
        headerString += "Battery Average Cell Voltage,"
        headerString += "Battery Total Voltage,"
        headerString += "Cell Voltage Deviation"
        rowString = datetime.time.isoformat(timespec='milliseconds')
        rowString += ','
        for voltage in cellVoltages:
            rowString += f"{voltage},"
        for temperature in cellTemperatures:
            rowString += f"{temperature}"
        rowString += f"{self.mcuCount},"
        rowString += f"{mean(cellTemperatures)}"
        rowString += f"{min(cellVoltages)}"
        rowString += f"{max(cellVoltages)}"
        rowString += f"{mean(cellVoltages)}"
        rowString += f"{sum(cellVoltages)}"
        rowString += f"{max(cellVoltages)-min(cellVoltages)}"
        file.write(headerString)
        file.write(rowString)
        file.close()   

    # Extends the headers of the two sheets to the given mcu number length
    def update_headers(self, mcuNumber):
        try:
            while self.voltageSheet.get_total_columns() < mcuNumber:
                self.voltageSheet.insert_column(redraw=False)
            while self.temperatureSheet.get_total_columns() < mcuNumber:
                self.temperatureSheet.insert_column(redraw=False)
            headers = [f"MCU {x}" for x in range(1, (mcuNumber + 1))]
            self.voltageSheet.headers(
                newheaders=headers, redraw=False)
            self.temperatureSheet.headers(
                newheaders=headers, redraw=False)
            print(f"Extended headers to {mcuNumber}")
        except Exception as e:
            print(e)

    # Callback raised when monitoring is active and a voltage message is received.
    def voltage_callback(
            self,
            can_id,
            data,
            timestamp,
            mcuNumber,
            cellIndexes):
        try:
            if (mcuNumber > self.mcuCount):
                self.mcuCount = mcuNumber
                self.update_headers(mcuNumber)
            # Update the cell voltage dictionary.
            cells = self.voltages.get(mcuNumber)
            if (cells is None):
                cells = [7] * 12
            for cell in cellIndexes:
                cells[cell] = ((data[(cell % 3 * 2) + 1] << 8) + data[cell % 3 * 2]) / 10000.0
                if (mcuNumber == self.mcuCount and cell == cellIndexes[-1]):
                    self.voltageSheet.set_cell_data(cell, mcuNumber-1, value=cells[cell], redraw=True)
                else:
                    self.voltageSheet.set_cell_data(cell, mcuNumber-1, value=cells[cell], redraw=False)
            self.voltages.update({mcuNumber:cells})
        except Exception as e:
            print(e)

    # Callback raised when monitoring is active and a temperature message is received.
    def temperature_callback(
            self,
            can_id,
            data,
            timestamp,
            mcuNumber,
            cellIndexes):
        try:
            # Update the cell temperature dictionary.
            cells = self.temperatures.get(mcuNumber)
            if (cells is None):
                cells = [87] * 12
            for cell in cellIndexes:
                cells[cell] = ((data[(cell % 6)]) / 2.0) - 40
                if (mcuNumber == self.mcuCount and cell == cellIndexes[-1]):
                    self.temperatureSheet.set_cell_data(cell, mcuNumber-1, value=cells[cell], redraw=True)
                else:
                    self.temperatureSheet.set_cell_data(cell, mcuNumber-1, value=cells[cell], redraw=False)
            self.temperatures.update({mcuNumber:cells})
        except Exception as e:
            print(e)