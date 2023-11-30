import customtkinter
from DbcFrame import DbcFrame
from RawCANFrame import RawCANFrame
from GaugeFrame import GaugeFrame
from CliFrame import CliFrame
from HwManager import HwManager
from CommandSystem import CommandSystem
import canopen
import threading
import time


# Creates the basic tab
class BasicTab(customtkinter.CTkFrame):
    hwManager: HwManager = None
    sendNetwork: canopen.Network = None

    def __init__(
            self,
            master: customtkinter.CTkFrame,
            hwManager: HwManager,
            commandSystem: CommandSystem):
        super().__init__(master)
        self.hwManager = hwManager
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=100)
        self.grid_rowconfigure(2, weight=1)

        # Create the connect button,
        # later this will be a dropdown with available networks. TODO
        self.connectButton = customtkinter.CTkButton(
            self,
            text="Connect",
            command=self.connect_network)
        self.connectButton.grid(
            row=0,
            column=0,
            padx=2,
            pady=2,
            columnspan=2,
            sticky="w")

        # Create the send button, this sends the test message.
        self.connectButton = customtkinter.CTkButton(
            self,
            text="Send",
            command=self.send_test_message)
        self.connectButton.grid(
            row=0,
            column=1,
            padx=2,
            pady=2,
            columnspan=2,
            sticky="w")

        defaultNetwork = None
        if (len(self.hwManager.networkList) > 0):
            defaultNetwork = self.hwManager.networkList[0][3]
        if (self.hwManager.devMode):
            self.sendNetwork = self.hwManager.networkList[1][3]

        # Create the four frames:
        self.rawCANFrame = RawCANFrame(self, defaultNetwork)
        self.rawCANFrame.grid(row=1, column=0, padx=2, pady=2, sticky="nsew")

        self.dbcFrame = DbcFrame(self, defaultNetwork)
        self.dbcFrame.grid(row=1, column=1, padx=2, pady=2, sticky="nsew")

        self.cliFrame = CliFrame(self, hwManager, commandSystem)
        self.cliFrame.grid(row=2, column=0, padx=2, pady=2, sticky="nsew")

        self.buttonD = GaugeFrame(self, defaultNetwork, self.dbcFrame.db)
        self.buttonD.grid(row=2, column=1, padx=2, pady=2, sticky="nsew")

    def connect_network(self):
        print("Connecting basic comms tab to network")
        self.dbcFrame.network = self.hwManager.networkList[0][3]
        self.rawCANFrame.network = self.hwManager.networkList[0][3]
        self.rawCANFrame.assign_listener()
        self.dbcFrame.refresh_dbc_sheet(False)

    def send_test_message(self):
        # If we're in debugmode, try to send a test message.
        if isinstance(self.sendNetwork, canopen.Network):
            thread = threading.Thread(
                target=self.test_message_generator,
                daemon=True)
            thread.start()

    def test_message_generator(self):
        i = 0
        while (True):
            time.sleep(0.1)
            i += 1
            if (i <= 9):
                message = self.dbcFrame.db.get_message_by_name('DashInfo')
                data = message.encode(
                    {'StateOfCharge': i*10,
                     'ChargingFlag': 1,
                     'BatteryFaultFlag': 1,
                     'BatteryTemperature': i*3,
                     'Current': i*20})
                self.sendNetwork.send_message(message.frame_id, data, False)
            else:
                i = 0
