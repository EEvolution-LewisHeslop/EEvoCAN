import customtkinter
from DbcFrame import DbcFrame

import tk_tools

# Creates the basic tab
class BasicTab(customtkinter.CTkFrame):
    def __init__(self, master: customtkinter.CTkFrame):
        super().__init__(master)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Create the four frames:
        self.RawCANFrame = RawCANFrame(self)
        self.RawCANFrame.grid(row=0, column=0, padx=2, pady=2, sticky="nsew")

        self.dbcFrame = DbcFrame(self)
        self.dbcFrame.grid(row=0, column=1, padx=2, pady=2, sticky="nsew")

        self.CliFrame = CliFrame(self)
        self.CliFrame.grid(row=1, column=0, padx=2, pady=2, sticky="nsew")

        self.buttonD = GaugeFrame(self)
        self.buttonD.grid(row=1, column=1, padx=2, pady=2, sticky="nsew")

class GaugeFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(fg_color="darkslategray", corner_radius=6)
        
        # Set the weights
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Create the section header
        self.gaugesLabel = customtkinter.CTkLabel(self, text="Gauges Frame")
        self.gaugesLabel.grid(row=0, column=0, columnspan=3, padx=20, pady=10, sticky="w")

        # Create Battery Voltage Gauge
        self.gauge1 = tk_tools.Gauge(self, max_value=100.0,
                       label='Bat Voltage', unit='V', bg="darkslategray")
        self.gauge1.grid(row=1, column=0, padx=5, pady=5)
        self.gauge1.set_value(25)
        self.gauge1._canvas.configure(bg="darkslategray", highlightthickness=0)    

        # Create Battery Current Gauge
        self.gauge2 = tk_tools.Gauge(self, max_value=100.0,
            label='Bat Current', unit='A', bg="darkslategray")
        self.gauge2.grid(row=1, column=1, padx=5, pady=5)
        self.gauge2.set_value(50)
        self.gauge2._canvas.configure(bg="darkslategray", highlightthickness=0)

        # Create Battery SoC Gauge
        self.gauge3 = tk_tools.Gauge(self, max_value=100.0,
            label='SoC', unit='%', bg="darkslategray")
        self.gauge3.grid(row=1, column=2, padx=5, pady=5)
        self.gauge3.set_value(75)
        self.gauge3._canvas.configure(bg="darkslategray", highlightthickness=0)

        # Create the CreateGauge Button
        self.createGauge = customtkinter.CTkButton(self, text="Create Gauge")
        self.createGauge.grid(row=2, columnspan=3, padx=5, pady=5)        

class CliFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        # Set the weights
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Create the section header
        self.CliLabel = customtkinter.CTkLabel(self, text="CLI Frame")
        self.CliLabel.grid(row=0, column=0, padx=20, pady=10, sticky="w")

        # Create the CLI log
        self.cliText = customtkinter.CTkTextbox(self)
        self.cliText.grid(row=1, column=0, columnspan=2, padx=5, pady=(0,5), sticky="nsew")
        # Add the default text
        self.cliText.configure(state='normal')
        self.cliText.insert('end', "Waiting for Commands...")
        self.cliText.configure(state='disabled')

        # Create the entry for the CLI
        self.cliEntry = customtkinter.CTkTextbox(self, height=30)
        self.cliEntry.grid(row=2, column=0, columnspan=2, padx=5, pady=(0,5), sticky="ew")

        # Create the send button.
        self.cliSend = customtkinter.CTkButton(self, height=30, text="Send")
        self.cliSend.grid(row=2, column=1, padx=5, pady=(0,5))

class RawCANFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        # Set the weights
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Create the section header.
        self.rawCANLabel = customtkinter.CTkLabel(self, text="Raw CAN Data")
        self.rawCANLabel.grid(row=0, column=0, padx=20, pady=10, sticky="w")

        # Create logging LED
        self.led0 = tk_tools.Led(self, size=40, bg="#333333")
        self.led0.grid(row=0, column=1, padx=10, pady=0)
        self.led0.to_green(False)

        # Create the logging button.
        self.logCANButton = customtkinter.CTkButton(self, text="Log CAN", command=lambda:self.load_dbc(self.sheet))
        self.logCANButton.grid(row=0, column=2, padx=20, pady=10)

        # Create the raw CAN viewer.
        self.canText = customtkinter.CTkTextbox(self)
        self.canText.grid(row=1, column=0, columnspan=3 , padx=5, pady=(0,5), sticky="nsew")
        # Add the default text
        self.canText.configure(state='normal')
        self.canText.insert('end', "Waiting for CAN...")
        self.canText.configure(state='disabled')