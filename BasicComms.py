import customtkinter
from DbcFrame import DbcFrame
from RawCANFrame import RawCANFrame
from HwManager import HwManager
import tk_tools
import canopen

# Creates the basic tab
class BasicTab(customtkinter.CTkFrame):
    hwManager:HwManager = None
    sendNetwork:canopen.Network = None
    def __init__(self, master: customtkinter.CTkFrame, hwManager:HwManager):
        super().__init__(master)
        self.hwManager = hwManager
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=100)
        self.grid_rowconfigure(2, weight=1)
        
        # Create the connect button, later this will be a dropdown with available networks.
        self.connectButton = customtkinter.CTkButton(self, text="Connect", command=self.connect_network)
        self.connectButton.grid(row=0, column=0, padx=2, pady=2, columnspan=2, sticky="w")
                
        # Create the send button, this sends the test message.
        self.connectButton = customtkinter.CTkButton(self, text="Send", command=self.send_test_message)
        self.connectButton.grid(row=0, column=1, padx=2, pady=2, columnspan=2, sticky="w")

        # Create the four frames:
        self.rawCANFrame = RawCANFrame(self)
        self.rawCANFrame.grid(row=1, column=0, padx=2, pady=2, sticky="nsew")

        self.dbcFrame = DbcFrame(self)
        self.dbcFrame.grid(row=1, column=1, padx=2, pady=2, sticky="nsew")

        self.cliFrame = CliFrame(self)
        self.cliFrame.grid(row=2, column=0, padx=2, pady=2, sticky="nsew")

        self.buttonD = GaugeFrame(self)
        self.buttonD.grid(row=2, column=1, padx=2, pady=2, sticky="nsew")
    
    def connect_network(self):
        print("Connecting basic comms tab to network")
        if (self.hwManager.devMode):
            self.sendNetwork = self.hwManager.networkList[1][3]
        self.dbcFrame.network = self.hwManager.networkList[0][3]
        self.rawCANFrame.network = self.hwManager.networkList[0][3]
        self.rawCANFrame.assign_listener()
        self.dbcFrame.refresh_dbc_sheet(False)

    def send_test_message(self):
        # If we're in debugmode, try to send a test message.
        if isinstance(self.sendNetwork, canopen.Network):            
            message = self.dbcFrame.db.get_message_by_name('DashInfo')
            data = message.encode({'StateOfCharge': 100.0, 'ChargingFlag': 0, 'BatteryFaultFlag': 1, 'BatteryTemperature':21, 'Current':75})
            self.sendNetwork.send_message(message.frame_id, data, False)

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

