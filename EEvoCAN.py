# 06/11/2023 - LH - Created EEvoCAN.py
# This will serve as the main entrypoint of the EEvoCAN application.
import customtkinter
import threading
import time

import FrameBuilder
import PrefManager
from HomePage import HomeTab
from BasicComms import BasicTab
from ConfigurationWizard import ConfigurationTab
from SoftwareLoader import SoftwareTab
from TestInterface import TestInterfaceTab
from HwManager import HwManager
from CommandSystem import CommandSystem


# Creates the GUI, and executes GUI commands.
class App(customtkinter.CTk):
    # Builds the window and starts any GUI updater.
    # Takes the hwManager instance for updating gui with can data.
    def __init__(self, hwManager: HwManager, commandSystem: CommandSystem):
        # Create the window
        super().__init__()
        self.title("EEvoCAN")
        self.iconbitmap("resources/icon/icon.ico")
        self.minsize(1200, 600)
        self.geometry(PrefManager.load_prefs('Window', 'geometry'))
        self.resizable(True, True)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Create the tabview
        self.tabView = MainTabView(self, hwManager, commandSystem)
        self.tabView.grid(
            row=0,
            rowspan=2,
            column=1,
            padx=(0, 20),
            pady=(0, 20),
            sticky="nsew")

        # Create the device frame
        self.device_frame = DeviceFrame(self)
        self.device_frame.configure(width=100)
        self.device_frame.grid(
            row=1,
            column=0,
            padx=20,
            pady=(15, 0),
            sticky="nw")

        # Every now and then, capture the screen state location.
        threading.Thread(
            target=lambda:
                PrefManager.save_window_state(self), daemon=True).start()


# Creates a frame that monitors when a device is plugged in etc.
class DeviceFrame(customtkinter.CTkScrollableFrame):
    # Builds the frame and starts any GUI updaters for the frame.
    def __init__(self, master):
        super().__init__(master)

        # Create the header.
        self.device_list_header = customtkinter.CTkLabel(
            self,
            text="Device List:")
        self.device_list_header.grid(row=0, column=0, sticky="nw")

        # Create the list text.
        self.device_list = customtkinter.CTkLabel(
            self,
            text="Waiting for input.")
        self.device_list.grid(row=1, column=0, sticky="nw")

        # Start the list updater thread
        threading.Thread(target=self.device_table_updater, daemon=True).start()

    # The thread that updates the device table every 1s
    def device_table_updater(self):
        i = 0
        while (True):
            try:
                i += 1
                devices = hwManager.get_active_devices()
                deviceText = ""
                if (devices):
                    for device in devices:
                        deviceText += f"{device[0]}, {i}\n"
                    self.device_list.configure(text=deviceText)
                else:
                    i = 0
                    self.device_list.configure(text="No devices.")
                time.sleep(1)
            except Exception as e:
                print(f"Failed to update device list: {e}")
                for thread in threading.enumerate():
                    print(thread.name)
                return


# Creates the Main Tabview which holds
# the various main tabs of the application.
class MainTabView(customtkinter.CTkTabview):
    # Builds the tabview and starts any GUI updaters for the tabs.
    def __init__(
            self,
            master,
            hwManager: HwManager,
            commandSystem: CommandSystem):
        # Create the tabview
        super().__init__(master)
        # Build the tabs
        FrameBuilder.tab_builder(
            self,
            title="Home",
            tabContent=HomeTab)
        FrameBuilder.tab_builder(
            self,
            title="Basic Comms",
            tabContent=BasicTab,
            hwManager=hwManager,
            commandSystem=commandSystem)
        FrameBuilder.tab_builder(
            self,
            title="Configuration Wizard",
            tabContent=ConfigurationTab)
        FrameBuilder.tab_builder(
            self,
            title="Software Loader",
            tabContent=SoftwareTab,
            commandSystem=commandSystem)
        FrameBuilder.tab_builder(
            self,
            title="Test Interfaces",
            tabContent=TestInterfaceTab)
        # Select the home tab
        self.set("Home")


# Main Application Startup Logic
hwManager = HwManager()
commandSystem = CommandSystem(hwManager)
customtkinter.set_default_color_theme("green")
customtkinter.set_appearance_mode("dark")
app = App(hwManager, commandSystem)
app.mainloop()
