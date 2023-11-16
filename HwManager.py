# 07/11/2023 - LH - Created HwManager.py
# This will serve as device manager for EEvoCAN.
# HwManager uses Python-CAN as its back end, but implements a device list getter and automatic device detection.
import can
from can.interfaces.ixxat import IXXATBus
from can.interfaces.kvaser import KvaserBus
from canopen import Network
import threading
import time
import ctypes

##### SUPPRESSESS ANNOYING SHUTDOWN WARNING CAUSE THE PACKAGE SAYS THAT UNINITIALISED BUSES ARE "NOT SHUTDOWN" #####
import logging
class IgnoreShutdownWarningFilter(logging.Filter):
    def filter(self, record):
    # Check if the log record contains the specific warning message
        message = record.getMessage()
        return "was not properly shut down" not in message
# Get the logger used by the bus module
logger = logging.getLogger('can.bus')
# Add the filter to the logger
logger.addFilter(IgnoreShutdownWarningFilter())
##### SUPPRESSESS ANNOYING SHUTDOWN WARNING CAUSE THE PACKAGE SAYS THAT UNINITIALISED BUSES ARE "NOT SHUTDOWN" #####


# Hw Manager Class is responsible for maintaining a list of connected devices.
class HwManager():
    searching = True
    availableDeviceTypes = []
    activeDevices = []
    activeCanopenNetworks = []

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
            foundDeviceTypes.append("kvaser")
            print(f"Kvaser Drivers Found: {int(0 if kvaserChannelCount.value is None else kvaserChannelCount.value)} device(s) connected.")
        except Exception as e:
            print(e, "Kvaser Drivers not found!")

        # Check for Ixxat VCI Drivers
        try:
            from can.interfaces.ixxat import get_ixxat_hwids
            ixxatChannelCount = len(get_ixxat_hwids())
            foundDeviceTypes.append("ixxat")
            print(f"Ixxat Drivers Found: {ixxatChannelCount} device(s) connected.")
        except:
            print("Ixxat Drivers not found!")

        # Check for PCAN Drivers ##### TODO #####
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
        return self.activeDevices

    # Starts the background searcher thread.
    def start_auto_search(self):
        if (self.searching):
            threading.Thread(target=self.background_searcher, daemon=True).start()

    # Thread that calls find_devices every second.
    def background_searcher(self):
        print("New background searcher created.")
        while(self.searching):            
            self.update_devices()
            time.sleep(1)

    # Attempts to find devices, and remove any that have disconnected.
    def update_devices(self):
        # Foreach avaibable device type, try to find new devices.
        print("Searching for devices.")
        detected_devices = []
        if ("ixxat" in self.availableDeviceTypes):
            ixxat_devices = self.find_devices_generic("ixxat", 10)
            detected_devices.extend(ixxat_devices)
        if ("kvaser" in self.availableDeviceTypes):
            kvaser_devices = self.find_devices_generic("kvaser", 10)
            # Ignore virtual device(s).
            kvaser_devices = [device for device in kvaser_devices if device.get('serial_number') is not None]
            detected_devices.extend(kvaser_devices)
        # Ignoring devices that already exist in the list of active devices, add the newly found devices and create a canopen networks for them.
        for device in detected_devices:
            if device['serial_number'] not in [d['serial_number'] for d in self.activeDevices]:
                self.activeDevices.append(device)
                # Create and add new CANopen network
                network = Network(device.get('bus'))
                self.activeCanopenNetworks.append((network, device.get('serial_number')))

        # If any devices have been unplugged since last time, remove them.
        self.remove_disconnected_devices(detected_devices)

    # Removes any devices that have now disconnected.
    def remove_disconnected_devices(self, detected_devices):
        # Create a set of detected Serial_numbers for easy comparison
        detected_serial_numbers = {device['serial_number'] for device in detected_devices if device['serial_number']}

        # Find which Serial_numbers are no longer present
        disconnected_serial_numbers = set([d['serial_number'] for d in self.activeDevices]) - detected_serial_numbers

        # Remove disconnected devices from the list of active devices and its canopen network from the list of canopen networks.
        if (len(disconnected_serial_numbers) > 0):
            networksToShutdown = [network for network in self.activeCanopenNetworks if network[1] in disconnected_serial_numbers]
            devicesToShutdown = [device for device in self.activeDevices if device.get('serial_number') in disconnected_serial_numbers]
            for network in networksToShutdown:
                self.shutdown_network(network)
            for device in devicesToShutdown:
                self.shutdown_device(device)
            # self.activeCanopenNetworks = [network for network in self.activeCanopenNetworks if network[1] not in disconnected_serial_numbers]
            # self.activeDevices = [device for device in self.activeDevices if device.get('serial_number') not in disconnected_serial_numbers]
    
    # Removes the device from the device list, TODO, any other cleanup required.
    def shutdown_network(self, network):
        self.activeCanopenNetworks.remove(network)
        print("Shutting down network.")

    # Removes the device from the device list, TODO, any other cleanup required.
    def shutdown_device(self, device_to_remove):
        if device_to_remove:
            # Remove the bus from active buses
            self.activeDevices.remove(device_to_remove)
            print("Shutting down device.")

    # A method finding buses based on a given interfacetype. Because not all buses are structured the same, there are some configurations to do
    def find_devices_generic(self, interface_type, max_channels, **kwargs):
        detected_devices = []
        # Get the interface specific bus classes
        BusClass = {
            'ixxat': IXXATBus,
            'kvaser': KvaserBus
        }.get(interface_type)
        # Get the interface specific attribute name/location for a unique identifier
        busIdAttr = {
            'ixxat': 'bus._device_info.UniqueHardwareId.AsChar',
            'kvaser': 'serial_number'
        }.get(interface_type)

        # If the classtype was unrecognized, error.
        if not BusClass:
            raise ValueError(f"Unsupported interface type: {interface_type}")
        
        # For the given number of channels try to create a bus, if successful add it to the list of detected devices.
        for channel in range(max_channels):
            try:
                bus = None
                with BusClass(channel=channel, **kwargs) as bus:
                    id_value = get_nested_attr(bus, busIdAttr, None)
                    if id_value and hasattr(id_value, 'decode'):
                        id_value = id_value.decode('ascii')  # decode if it's bytes
                    detected_devices.append({
                        'channel': channel,
                        'serial_number': id_value,
                        'bus': bus,
                        'bustype': interface_type
                    })
            except can.CanError:
                continue

        return detected_devices

# Helper for getting attributes that are deeply nested    
def get_nested_attr(obj, attr_path, default=None):
    try:
        for attr in attr_path.split('.'):
            obj = getattr(obj, attr)
        return obj
    except AttributeError:
        return default