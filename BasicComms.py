import customtkinter
from DbcFrame import DbcFrame
from RawCANFrame import RawCANFrame
from GaugeFrame import GaugeFrame
from HwManager import HwManager
import canopen
import threading
import time

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

        self.cliFrame = CliFrame(self, defaultNetwork)
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
            threading.Thread(target=self.test_message_generator, daemon=True).start()     
    
    def test_message_generator(self):
        i = 0
        while (True):
            time.sleep(0.1)
            i+=1
            if (i <=9):
                message = self.dbcFrame.db.get_message_by_name('DashInfo')
                data = message.encode({'StateOfCharge': i*10, 'ChargingFlag': 1, 'BatteryFaultFlag': 1, 'BatteryTemperature':i*3, 'Current':i*20})
                self.sendNetwork.send_message(message.frame_id, data, False)
            else:
                i = 0

class CliFrame(customtkinter.CTkFrame):
    network:canopen.Network
    def __init__(self, master, network=None):
        super().__init__(master)
        self.network = network

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
        self.cliText.insert('end', "Waiting for Commands...\n")
        self.cliText.configure(state='disabled')

        # Create the entry for the CLI
        self.cliEntry = CliEntry(self, height=30, logBox=self.cliText)
        self.cliEntry.grid(row=2, column=0, columnspan=2, padx=5, pady=(0,5), sticky="ew")

        # Create the send button.
        self.cliSend = customtkinter.CTkButton(self, height=30, text="Send")
        self.cliSend.grid(row=2, column=1, padx=5, pady=(0,5))

class CliEntry(customtkinter.CTkTextbox):
    historyIndex = 0
    history = []
    def __init__(self, master, height, logBox:customtkinter.CTkTextbox):
        super().__init__(master, height=height)
        self.logBox = logBox
        
        # Bind enter to send command
        self.bind('<Key>', self.callback)

    def callback(self, event, *args):
        # Get the value on the cursors current row.
        if (event.keysym == 'Up'):
            if (len(self.history) > self.historyIndex):
                # Increase history index and set cli value to that element in history.
                self.historyIndex +=1
                self.set_text_value(self.history[self.historyIndex-1])
            else:
                # Do nothing.
                return "break"
        if (event.keysym == 'Down'):
            if (self.historyIndex > 1):
                # Decrease history index and set cli value to that element in history.
                self.historyIndex -=1
                self.set_text_value(self.history[self.historyIndex-1])
            elif (self.historyIndex == 1):
                # Decrease history index and set cli value to blank.
                self.historyIndex -=1
                self.set_text_value("")
            else:
                # Do nothing
                return "break"
        if (event.keysym == 'Return'):
            # Get the current rowtext.
            index = self.index('insert')
            row, column = index.split('.')
            rowText = self.get(index1=(row +'.0'), index2=(str(int(row)+1)+'.0'))

            # If there was no text, exit early.
            if(rowText.strip() == ""):
                return "break"

            # Add the current text to the history.
            self.history.insert(0, rowText)

            # Set the history index to 0.
            self.historyIndex = 0

            # Set the text to nothing.
            self.set_text_value("")

            # Post command.
            self.post_command(rowText)
            return "break"

    def post_command(self, command):
        # Post the command to the CLI log.
        self.logBox.configure(state='normal')
        self.logBox.insert('end', str(command))
        self.logBox.configure(state='disabled')   
        self.logBox.see("end")

    # Sets the entry text to the given text value.
    def set_text_value(self, text):
        index = self.index('insert')
        row, column = index.split('.')
        self.delete(index1=(row +'.0'), index2=(str(int(row)+1)+'.0'))
        self.insert('end', str(text))
