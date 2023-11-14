# 07/11/2023 - LH - Created HwManager.py
# This will serve as device manager for EEvoCAN.
# HwManager uses Python-CAN as its back end, but implements a device list getter and automatic device detection.
import can
import threading
import time
import ctypes
from can.interfaces.ixxat.canlib import IXXATBus
#from can.interfaces import pcan

# Hw Manager Class is responsible for maintaining a list of connected devices.
class HwManager():
    searching = True
    availableDeviceTypes = []
    activeDeviceTypes = []
    activeBuses = []
    deviceIds = []

    # Initialises a new hardware manager.
    def __init__(self):
        # Look for what device libraries are available on the system.
        self.availableDeviceTypes = self.get_available_device_types()
        if (len(self.availableDeviceTypes) == 0):
            self.searching = False
            print("Stopped searching because no device drivers are installed.")
            return

    # Returns a list of available device types.
    def get_available_device_types(self):
        foundDeviceTypes = []
        # Check for KVASER CANLIB Drivers
        try:
            from can.interfaces.kvaser import canlib
            kvaserChannelCount = ctypes.c_void_p()     
            canlib.canGetNumberOfChannels(ctypes.byref(kvaserChannelCount))
            # by default there are two virtual channels, so reduce the channel count by this amount.
            kvaserChannelCount.value -= 2
            foundDeviceTypes.append("Kvaser")
            print(f"Kvaser Drivers Found: {int(0 if kvaserChannelCount.value is None else kvaserChannelCount.value)} device(s) connected.")
        except Exception as e:
            print(e, "Kvaser Drivers not found!")

        # Check for Ixxat VCI Drivers
        try:
            from can.interfaces.ixxat import get_ixxat_hwids
            ixxatChannelCount = len(get_ixxat_hwids())
            foundDeviceTypes.append("Ixxat")
            print(f"Ixxat Drivers Found: {ixxatChannelCount} device(s) connected.")
        except:
            print("Ixxat Drivers not found!")

        # Check for PCAN Drivers ##### Warning not implemented #####
        #pcan_devices = pcan
        #foundDeviceTypes.append("PCAN")
        #print(f"PCAN Drivers Found: {pcan_devices} device(s) connected.")
        
        return foundDeviceTypes

    # Sends a message on the last connnected device.
    def send_message(self):
        if (len(self.activeBuses) > 0):
            # Use the first device in the list to send a message.
            bus: can.Bus = self.activeBuses[0]
            msg = can.Message(
            arbitration_id=0xC0FFEE,
            data=[0, 25, 0, 1, 3, 1, 4, 1],
            is_extended_id=True)
            try:
                bus.send(msg)
            except can.CanError:
                print("Message NOT sent")
                print(f"Message sent on {self.deviceIds[0]} device.")
        else:
            print("No device to send message.")

    # Returns the current list of devices.
    def get_devices(self):
        return self.deviceIds
    
    # Returns the current list of buses.
    def get_busses(self):
        return self.activeBuses
    
    # Starts the background searcher thread.
    def start_auto_search(self):
        if (self.searching):
            threading.Thread(target=self.background_searcher, daemon=True).start()

    # Thread that calls find_devices every half a second.
    def background_searcher(self):
        print("New background searcher created.")
        while(self.searching):            
            self.find_devices()
            time.sleep(0.5)

    # Attempts to find devices.
    def find_devices(self):
        print("Searching for devices.")

        # If there are ixxat drivers installed, look for ixxat devices.
        if ("Ixxat" in self.availableDeviceTypes):
            from can.interfaces.ixxat import get_ixxat_hwids
            newHwids = get_ixxat_hwids()
            for hwid in self.deviceIds:
                if (hwid not in newHwids):
                    # Clear any hwids that are no longer present
                    self.deviceIds.remove(hwid)
                    ### Warning, below limits support to one ixxat ###
                    bus: IXXATBus = next((x for x in self.activeBuses if x.bus.channel == 0), None)
                    print(f"Removing {bus.bus._device_info.UniqueHardwareId.AsChar.decode("ascii")}")
                    self.activeBuses.remove(bus)
            for hwid in newHwids:
                if (hwid not in self.deviceIds):
                    # Add new hwids
                    self.deviceIds.append(hwid)
                    bus = IXXATBus(0, unique_hardware_id=hwid)
                    self.activeBuses.append(bus)