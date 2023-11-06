# 06/11/2023 - LH - Created EEvoCAN.py
# This will serve as the main entrypoint of the EEvoCAN application.
# In the beginning it will be used to test the Python CAN library for this application.
import customtkinter
import can
import threading
import time

# Creates the GUI, and executes GUI commands.
class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("EEvoCAN")
        self.geometry("400x150")
        self.grid_columnconfigure((0, 1), weight=1)

        self.button = customtkinter.CTkButton(self, text="Send Message", command=HwHandler.send_message)
        self.button.grid(row=0, column=0, padx=20, pady=20, sticky="ew", columnspan=2)
        self.text = customtkinter.CTkLabel(self, text="Waiting for input.")
        self.text.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="w")
        self.checkbox_2 = customtkinter.CTkCheckBox(self, text="Send Test SDO Write")
        self.checkbox_2.grid(row=1, column=1, padx=20, pady=(0, 20), sticky="w")

        threading.Thread(target=self.device_table_updater, daemon=True).start()
    
    def device_table_updater(self):
        i = 0
        while (True):
            i += 1
            deviceList = HwHandler.get_devices()
            if (deviceList):
                self.text.configure(text=f"{deviceList[0]}, {i}")
            else:
                i = 0
                self.text.configure(text="No devices connected.")
            time.sleep(0.5)

# Hardware Handler Logic
class HwHandler():

    searching = True
    deviceids = []

    def send_message():
        if (HwHandler.deviceids):
            print(f"Message sent on {HwHandler.deviceids[0]} device.")

    def get_devices():
        return HwHandler.deviceids
    
    def start_auto_search():
        if (HwHandler.searching):
            threading.Thread(target=HwHandler.background_searcher, daemon=True).start()

    def background_searcher():
        while(HwHandler.searching):            
            HwHandler.find_device()
            time.sleep(0.5)

    def find_device():
        print("Searching for devices.")
        from can.interfaces.ixxat import get_ixxat_hwids
        newHwids = get_ixxat_hwids()
        for hwid in HwHandler.deviceids:
            if (hwid not in newHwids):
                # Clear any hwids that are no longer present
                HwHandler.deviceids.remove(hwid)
        for hwid in newHwids:
            if (hwid not in HwHandler.deviceids):
                # Add new hwids
                HwHandler.deviceids.append(hwid)

# Main Application Logic
HwHandler.start_auto_search()
app = App()
app.mainloop()