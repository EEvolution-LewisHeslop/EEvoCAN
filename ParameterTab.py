import customtkinter
from CTkTable import CTkTable

from ResizeHandler import ResizeHandler
from Interpolation import Interpolation


# Creates the parameter subtab
class ParameterTab(customtkinter.CTkScrollableFrame):
    def __init__(self, master: customtkinter.CTkFrame):
        super().__init__(master)

        # Create the Temperature Range Frame for Charging
        self.temperatureRangeFrame = RangeFrame(
            self,
            "Temperature Range for Charging (degC)",
            [[-10, 0, 10, 20, 30, 40, 50, 60]],
            True,
            True,
            False)

        self.temperatureRangeFrame.grid(
            row=0,
            column=0,
            padx=5,
            pady=5,
            sticky="nsew")

        # Create the SoC Range Frame for Charging
        self.socRangeFrame = RangeFrame(
            self,
            "SoC Range for Charging (%)",
            [[0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]],
            True,
            True,
            True)
        self.socRangeFrame.grid(
            row=1,
            column=0,
            padx=5,
            pady=(0, 5),
            sticky="nsew")

        # Create the Temperature Range Frame for Discharging
        self.temperatureRangeFrame = RangeFrame(
            self,
            "Temperature Range for Discharging (degC)",
            [[-10, 0, 10, 20, 30, 40, 50, 60]],
            True,
            False,
            False)
        self.temperatureRangeFrame.grid(
            row=2,
            column=0,
            padx=5,
            pady=(0, 5),
            sticky="nsew")

        # Create the SoC Range Frame for Discharging
        self.socRangeFrame = RangeFrame(
            self,
            "SoC Range for Discharging (%)",
            [[0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]],
            True,
            False,
            True)
        self.socRangeFrame.grid(
            row=3,
            column=0,
            padx=5,
            pady=(0, 5),
            sticky="nsew")

        # Create the voltage range frame
        self.voltageRangeFrame = RangeFrame(
            self,
            "Voltage Range (V)",
            [[3.400, 3.415, 3.431, 3.447, 3.462,
              3.478, 3.487, 3.495, 3.504, 3.512,
              3.521, 3.530, 3.539, 3.547, 3.556,
              3.565, 3.571, 3.578, 3.585, 3.592,
              3.598, 3.604, 3.609, 3.614, 3.620,
              3.625, 3.628, 3.632, 3.635, 3.638,
              3.642, 3.645, 3.648, 3.652, 3.655,
              3.658, 3.661, 3.664, 3.667, 3.671,
              3.674, 3.679, 3.684, 3.689, 3.694,
              3.699, 3.706, 3.713, 3.720, 3.727,
              3.734, 3.746, 3.758, 3.770, 3.782,
              3.794, 3.806, 3.819, 3.831, 3.844,
              3.856, 3.867, 3.877, 3.887, 3.897,
              3.907, 3.916, 3.925, 3.935, 3.948,
              3.963, 3.974, 3.986, 3.997, 4.009,
              4.020, 4.032, 4.044, 4.056, 4.068,
              4.080, 4.091, 4.103, 4.114, 4.126,
              4.137, 4.146, 4.155, 4.163, 4.172,
              4.181, 4.191, 4.202, 4.212, 4.222,
              4.233, 4.243, 4.253, 4.263, 4.274, 4.320]])
        self.voltageRangeFrame.grid(
            row=4,
            column=0,
            padx=5,
            pady=(0, 5),
            sticky="nsew")

        # Create the Simple parameter frame for other parameters
        self.simpleParamFrame = SimpleParamsFrame(self)
        self.simpleParamFrame.grid(
            row=5,
            column=0,
            padx=5,
            pady=(0, 5),
            sticky="nsew")

        # Create the Slave boards parameter frame
        # for slave board configurations
        self.slaveBoardFrame = SlaveBoardFrame(self)
        self.slaveBoardFrame.grid(
            row=6,
            column=0,
            padx=5,
            pady=(0, 5),
            sticky="nsew")


# Parameter Tab Range Frame
class RangeFrame(customtkinter.CTkFrame):
    def __init__(
            self,
            master,
            labelText,
            values,
            setReference=False,
            isCharge=False,
            isSoc=False):
        super().__init__(master)

        self.grid_columnconfigure(3, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Create the frame heading.
        self.configure(fg_color="darkslategray", corner_radius=6)
        self.frameHeading = customtkinter.CTkLabel(
            self,
            text=labelText,
            corner_radius=6)
        self.frameHeading.grid(
            row=0,
            column=0,
            columnspan=2,
            pady=5,
            sticky="w")

        # Create the resolution entry label
        self.resolutionEntryLabel = customtkinter.CTkLabel(
            self,
            text="Configure Length",
            corner_radius=6)
        self.resolutionEntryLabel.grid(
            row=1,
            column=0,
            pady=5,
            sticky="w")

        # Create the resolution entry box
        self.textVariable = customtkinter.StringVar(self, len(values[0]))
        self.resolutionEntryBox = customtkinter.CTkEntry(
            self,
            textvariable=self.textVariable)
        self.resolutionEntryBox.grid(row=1, column=1, pady=5, sticky="e")
        self.textVariable.trace_add(
            'write',
            lambda var_name, var_index, trace_mode:
                inputValidator(
                    var_name,
                    var_index,
                    trace_mode,
                    self.textVariable,
                    float))

        # Create the range table frame
        self.tableFrame = customtkinter.CTkScrollableFrame(
            self,
            orientation="horizontal",
            height=30)
        self.tableFrame.grid(
            row=2,
            column=0,
            columnspan=4,
            padx=5,
            sticky="new")

        # Create the range table
        self.table = CTkTable(
            master=self.tableFrame,
            values=values,
            write=True,
            hover_color="green",
            width=40)
        self.table.grid(row=0, column=0)

        # Set the reference to the axis in the resizer
        # and decide how resize button will work.
        if (setReference):
            ResizeHandler.setAxisReference(self.table, isSoc, isCharge)
            self.resizeButton = customtkinter.CTkButton(
                self,
                text="Resize",
                command=lambda: ResizeHandler.resizeTable(
                    self.textVariable.get(),
                    isSoc,
                    isCharge))
        else:
            self.resizeButton = customtkinter.CTkButton(
                self,
                text="Resize",
                command=lambda: self.table.configure(
                    columns=int(self.textVariable.get()),
                    width=40))
        self.resizeButton.grid(row=1, padx=5, column=2, sticky="w")

        # Create validators for table cells.
        for cell in self.table.frame.values():
            if isinstance(cell, customtkinter.CTkEntry):
                tableTextVariable = customtkinter.StringVar(self)
                tableTextVariable.set(cell.get())
                cell.configure(textvariable=tableTextVariable)
                tableTextVariable.trace_add(
                    'write',
                    lambda v_name, v_index, trace_mode, tv=tableTextVariable:
                        inputValidator(
                            v_name,
                            v_index,
                            trace_mode,
                            tv,
                            float))

        # Create the clear button
        self.resizeButton = customtkinter.CTkButton(
            self,
            width=50,
            text="Clear",
            command=lambda: self.table.update_values([['']]))
        self.resizeButton.grid(row=1, column=3, sticky="w")

        # Create the interpolate button
        self.interpolateButton = customtkinter.CTkButton(
            self,
            text="Interpolate",
            command=lambda: self.table.update_values(
                [Interpolation.LinearFill(self.table.get_row(0))]))
        self.interpolateButton.grid(
            row=3,
            column=0,
            padx=5,
            pady=5,
            sticky="w")


# Parameter Tab Simple Parameter Frame
class SimpleParamsFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        # Create a dictionary of simple parameters
        # against their string variables and indentation,
        # currently this is based on hardcoded values. TODO
        paramDict = {
            "Minimum Cell Voltage Limit (V)": (customtkinter.StringVar(self, "3.2"), True),
            "Maximum Cell Voltage Limit (V)": (customtkinter.StringVar(self, "4.35"), False),
            "Minimum Cell Temperature Limit (degC)": (customtkinter.StringVar(self, "-30"), True),
            "Maximum Cell Temperature Limit (degC)": (customtkinter.StringVar(self, "60"), False),
            "Maximum Discharging Current Limit (A)": (customtkinter.StringVar(self, "2000"), True),
            "Maximum Charging Current Limit (A)": (customtkinter.StringVar(self, "510"), False),
            "Maximum Charging Current Limit on Charger (A)": (customtkinter.StringVar(self, "250"), False),
            "Soft Discharging Current Limit (A)": (customtkinter.StringVar(self, "1200"), True),
            "Soft Charging Current Limit (A)": (customtkinter.StringVar(self, "245"), False),
            "Customer Discharging Current Limit (A)": (customtkinter.StringVar(self, "1080"), True),
            "Customer Charging Current Limit (A)": (customtkinter.StringVar(self, "140"), False),
            "Number of drive motors": (customtkinter.StringVar(self, "1"), True),
            "System Capacity (Ah)": (customtkinter.StringVar(self, "158.8"), True),
            "Customer 0% SoC (% of true SoC)": (customtkinter.StringVar(self, "10"), False),
            "Customer 100% SoC (% of true SoC)": (customtkinter.StringVar(self, "95"), False),
            "End of charge SoC (%)": (customtkinter.StringVar(self, "100"), False),
            "OBC Charging AC Current Limit (A)": (customtkinter.StringVar(self, "32"), True),
            "OBC Charging DC Current Limit (A)": (customtkinter.StringVar(self, "40"), False),
            "CAN Message Timeout (ms)": (customtkinter.StringVar(self, "100"), True),
            }

        # Configure the frame.
        self.configure(fg_color="darkslategray", corner_radius=6)
        self.frameHeading = customtkinter.CTkLabel(
            self,
            text="Basic Parameter Configuration",
            corner_radius=6)
        self.frameHeading.grid(
            row=0,
            column=0,
            columnspan=2,
            pady=5,
            sticky="w")

        # Add Items from the dict as elements in the frame.
        for index, (key, value) in enumerate(paramDict.items()):
            self.simple_param_builder(value[0], key, value[1], index+1)

    # Builds a simple param.
    def simple_param_builder(
            self,
            stringVar: customtkinter.StringVar,
            labelText,
            doubleSpace=False,
            gridRow=0):
        if (doubleSpace):
            padyValue = 5
        else:
            padyValue = (0, 5)
        label = customtkinter.CTkLabel(self, text=labelText)
        label.grid(row=gridRow, column=0, padx=5, pady=padyValue, sticky="w")
        textEntry = customtkinter.CTkEntry(self, textvariable=stringVar)
        textEntry.grid(row=gridRow,
                       column=1,
                       padx=5,
                       pady=padyValue,
                       sticky="w")
        stringVar.trace_add(
            'write',
            lambda var_name, var_index, trace_mode: inputValidator(
                var_name,
                var_index,
                trace_mode,
                stringVar,
                float))


# Parater Tab Slave Board Configuration Frame
class SlaveBoardFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.grid_columnconfigure(3, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Create the frame heading.
        self.configure(fg_color="darkslategray", corner_radius=6)
        self.frameHeading = customtkinter.CTkLabel(
            self,
            text="Slave Board Configuration",
            corner_radius=6)
        self.frameHeading.grid(
            row=0,
            column=0,
            columnspan=2,
            pady=5,
            sticky="w")

        # Create the resolution entry label
        self.resolutionEntryLabel = customtkinter.CTkLabel(
            self,
            text="Configure Number of Slaves",
            corner_radius=6)
        self.resolutionEntryLabel.grid(row=1, column=0, pady=5, sticky="w")

        # Create the resolution entry box
        self.textVariable = customtkinter.StringVar(self, "10")
        self.resolutionEntryBox = customtkinter.CTkEntry(
            self,
            textvariable=self.textVariable)
        self.resolutionEntryBox.grid(row=1, column=1, pady=5, sticky="e")
        self.textVariable.trace_add(
            'write',
            lambda var_name, var_index, trace_mode: inputValidator(
                var_name,
                var_index,
                trace_mode,
                self.textVariable,
                float))

        # Create the slave cellcount table frame
        self.tableFrame = customtkinter.CTkScrollableFrame(
            self,
            orientation="horizontal",
            height=60)
        self.tableFrame.grid(
            row=2,
            column=0,
            columnspan=4,
            padx=5,
            pady=(0, 5),
            sticky="new")

        # Create the slave cellcount table header
        self.slaveCellCountHeader = customtkinter.CTkLabel(
            master=self.tableFrame,
            text="Cells per Slave")
        self.slaveCellCountHeader.grid(row=0, column=0, padx=5, sticky="w")

        # Create the slave cellcount table
        value = [[11, 12, 11, 12, 11, 12, 11, 12, 11, 12]]
        self.table = CTkTable(
            master=self.tableFrame,
            values=value,
            write=True,
            hover_color="green",
            width=40)
        self.table.grid(row=1, column=0)

        # Create validators for table cells.
        for cell in self.table.frame.values():
            if isinstance(cell, customtkinter.CTkEntry):
                tableTextVariable = customtkinter.StringVar(self)
                tableTextVariable.set(cell.get())
                cell.configure(textvariable=tableTextVariable)
                tableTextVariable.trace_add(
                    'write',
                    lambda var_name,
                    var_index, trace_mode,
                    tv=tableTextVariable: inputValidator(
                        var_name,
                        var_index,
                        trace_mode,
                        tv,
                        float))

        # Create the resize button
        self.resizeButton = customtkinter.CTkButton(
            self,
            text="Resize",
            command=lambda: self.table.configure(
                columns=int(self.textVariable.get()),
                width=40))
        self.resizeButton.grid(row=1, padx=5, column=2, sticky="w")

        # Create the clear button.
        self.resizeButton = customtkinter.CTkButton(
            self,
            width=50,
            text="Clear",
            command=lambda: self.table.update_values([['']]))
        self.resizeButton.grid(row=1, column=3, sticky="w")

        # Add thermistors per slave input.
        self.thermistorsPerSlave = customtkinter.StringVar(self, "12")
        self.thermistorsPerSlaveLabel = customtkinter.CTkLabel(
            self,
            text="Thermistors per Slave")
        self.thermistorsPerSlaveLabel.grid(
            row=13,
            column=0,
            padx=5,
            pady=(0, 5),
            sticky="w")
        self.thermistorsPerSlaveTextEntry = customtkinter.CTkEntry(
            self,
            textvariable=self.thermistorsPerSlave)
        self.thermistorsPerSlaveTextEntry.grid(
            row=13,
            column=1,
            padx=5,
            pady=(0, 5),
            sticky="w")
        self.thermistorsPerSlave.trace_add(
            'write',
            lambda var_name, var_index, trace_mode: inputValidator(
                var_name,
                var_index,
                trace_mode,
                self.thermistorsPerSlave,
                float))


def inputValidator(
        v_name,
        v_index,
        trace_mode,
        stringVar: customtkinter.StringVar,
        typeToCheck):
    if (typeToCheck is float):
        # Validate user input.
        text = stringVar.get()
        if text is None:
            return
        trimmed = text.replace(" ", "")
        try:
            trimmed = float(trimmed)
            return float("{:.3f}".format(trimmed))
        except ValueError:
            if (trimmed != "-" and trimmed != "."):
                print("Entry input was non-numeric.")
                stringVar.set('')
