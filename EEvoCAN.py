# 06/11/2023 - LH - Created EEvoCAN.py
# This will serve as the main entrypoint of the EEvoCAN application.
# In the beginning it will be used to test the Python CAN library for this application.
import customtkinter
import threading
import time

import FrameBuilder
from BasicComms import BasicTab
from ConfigurationWizard import ConfigurationTab
from SoftwareLoader import SoftwareTab
from HwManager import HwManager

### Main Window ###

# Creates the GUI, and executes GUI commands.
class App(customtkinter.CTk):
    # Builds the window and starts any GUI updater, takes the hwManager instance for updating gui with can data
    def __init__(self, hwManager: HwManager):
        # Create the window
        super().__init__()
        self.title("EEvoCAN")
        self.iconbitmap("resources/icon/icon.ico")
        self.geometry("1200x800")
        #self.minsize(800,500)
        self.resizable(True, True)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Create the tabview
        self.tabView = MainTabView(self, hwManager)
        self.tabView.grid(row=0, rowspan=2, column=1, padx=(0,20), pady=(0,20), sticky="nsew")

        # Populate the window
        self.button = customtkinter.CTkButton(self, text="Send Message", command=hwManager.send_message)
        self.button.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        
        # Create the device frame
        self.device_frame = DeviceFrame(self)
        self.device_frame.configure(width=100)
        self.device_frame.grid(row=1, column = 0, padx=20, pady=(15,0), sticky="nw")

### Device Frame ###

# Creates a frame that monitors when a device is plugged in etc.
class DeviceFrame(customtkinter.CTkScrollableFrame):
    # Builds the frame and starts any GUI updaters for the frame.
    def __init__(self, master):
        super().__init__(master)

        # Create the header.
        self.device_list_header = customtkinter.CTkLabel(self, text="Device List:")
        self.device_list_header.grid(row=0, column=0, sticky="nw")

        # Create the list text.
        self.device_list = customtkinter.CTkLabel(self, text="Waiting for input.")
        self.device_list.grid(row=1, column=0, sticky="nw")

        # Start the list updater thread
        threading.Thread(target=self.device_table_updater, daemon=True).start()

    # The thread that updates the device table when devices are plugged in or added.
    def device_table_updater(self):
        i = 0
        while (True):
            try:
                i += 1
                deviceList = hwManager.get_devices()
                deviceText = ""
                if (deviceList):
                    for device in deviceList:
                        deviceText += f"{device}, {i}\n"
                    self.device_list.configure(text=deviceText)
                else:
                    i = 0
                    self.device_list.configure(text="No devices.")
                time.sleep(0.5)
            except:
                print("Failed to update device list.")
                for thread in threading.enumerate(): 
                    print(thread.name)
                return

### Main Tab View ###

# Creates the Main Tabview which holds the various main tabs of the application.
class MainTabView(customtkinter.CTkTabview):
    # Builds the tabview and starts any GUI updaters for the tabs.
    def __init__(self, master, hwManager: HwManager):
            # Create the tabview
            super().__init__(master)

            # Build the tabs
            FrameBuilder.tab_builder(self, title="Basic Comms", tabContent=BasicTab)
            FrameBuilder.tab_builder(self, title="Configuration Wizard", tabContent=ConfigurationTab)
            FrameBuilder.tab_builder(self, title="Software Loader", tabContent=SoftwareTab, hwManager=hwManager)

            # Select the 2nd tab
            self.set("Configuration Wizard")

# Main Application Startup Logic
hwManager = HwManager()
hwManager.start_auto_search()
customtkinter.set_default_color_theme("green")
customtkinter.set_appearance_mode("dark")
app = App(hwManager)
app.after(1, app.wm_state, 'zoomed')
app.mainloop()