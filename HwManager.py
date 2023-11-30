# 23/2023 - LH - Second iteration of HwManager.py
# Previous iteration used a brute force search for new devices.
# It led to a lot of random memory issues with the underlying device drivers.
# This time we will do things more sensibly, by watching for usb events.
import can
import canopen
import ctypes
import time
from usbmonitor import USBMonitor
from usbmonitor.attributes import ID_MODEL


# Keeps a track of the connected CAN devices
# and creates canopen networks for the buses that are created.
# Networks are stored in networkList
# as (device_id, device_info, interface, network, bus)
class HwManager():
    activeNetwork = None
    networkList = []
    deviceCounts = {
        'ixxat': 0,
        'kvaser': 0,
        'pcan': 0,
        'simplycan': 0}
    availableInterfaces = []
    devMode = False

    # Constructor for HwManager class.
    def __init__(self):
        # See what interface types are available.
        self.availableInterfaces = self.get_available_device_types()

        # Create the USBMonitor instance
        self.monitor = USBMonitor()

        # See what devices are already connected.
        self.start_connected_devices()

        # Start the device monitor.
        self.monitor.start_monitoring(
            on_connect=lambda id, info: self.device_connected(
                id,
                info),
            on_disconnect=lambda id, info: self.device_disconnected(
                id,
                info))

        # If there are only 2 channels connected and kvaser is avaialable;
        # connect virtual channels.
        availableConfigs = can.detect_available_configs(
            ['kvaser', 'ixxat', 'pcan'])
        devModeChannelCount = len(availableConfigs) == 2
        if ('kvaser' in self.availableInterfaces and devModeChannelCount):
            self.connect_virtual_devices()

    def connect_virtual_devices(self):
        print("WARNING - Kvaser drivers installed and only 2 channels found, "
              "enabling Dev Mode.")
        self.create_network("Virtual0", None, 'kvaser', 0)
        self.create_network("Virtual1", None, 'kvaser', 1)
        self.devMode = True

    # Returns a list of available device types.
    def get_available_device_types(self):
        foundDeviceTypes = []

        # Check for Kvaser CANLIB Drivers.
        try:
            from can.interfaces.kvaser import canlib
            connectedKvaserDevices = ctypes.c_void_p()
            canlib.canGetNumberOfChannels(ctypes.byref(connectedKvaserDevices))
            foundDeviceTypes.append('kvaser')
        except Exception:
            pass

        # Check for PCAN Drivers
        try:
            from can.interfaces.pcan.basic import PCANBasic
            PCANBasic()
            # TODO: Count the number of pcan devices on startup.
            foundDeviceTypes.append('pcan')
        except Exception:
            pass

        # Check for Ixxat VCI Drivers
        try:
            from can.interfaces.ixxat import get_ixxat_hwids
            len(get_ixxat_hwids())
            foundDeviceTypes.append('ixxat')
        except Exception:
            pass

        return foundDeviceTypes

    # Check if any devices are already connected;
    # and if they are, create the relevant buses for them.
    def start_connected_devices(self):
        # Get a list of the connected CAN devices:
        connectedDevices = self.monitor.get_available_devices()
        for key, value in connectedDevices.items():
            try:
                self.device_connected(key, value)
            except Exception as e:
                print(e)

    # Called when a USB device is connected;
    # checks for drivers, creates interface.
    def device_connected(self, device_id, device_info):
        # A device was connected, check what type it was.
        interface = ''
        if ("VCI" in device_info[ID_MODEL]):
            time.sleep(1)
            interface = 'ixxat'
        elif ("Kvaser" in device_info[ID_MODEL]):
            interface = 'kvaser'
            # Kvaser driver takes a while to move the channel ids
            # of the virtual channels.
            time.sleep(1)
        elif ("PCAN" in device_info[ID_MODEL]):
            interface = 'pcan'

        # Check that the drivers for this interface type are available
        # then create the network.
        if (not interface):
            return
        if (interface in self.availableInterfaces):
            try:
                self.create_network(
                    device_id,
                    device_info,
                    interface,
                    self.deviceCounts[interface])
            except Exception as e:
                print(f"Failed to start network: {e}")
        else:
            print(f"Device of type {interface} was connected "
                  "but no drivers were found.")

    # Called when a USB device is disconnected, shuts down the network
    # and bus and removes them from the list.
    def device_disconnected(self, device_id, device_info):
        # Identify the object in the network list
        # that corresponds to the disconnected device.
        for network in self.networkList:
            if (network[0] == device_id):
                networkToShutdown = network
        try:
            networkToShutdown[3].disconnect()
            self.deviceCounts[network[2]] -= 1
            self.networkList.remove(networkToShutdown)
            del networkToShutdown
            print("Network Shutdown")
        except Exception as e:
            print(f"Failed to shutdown: {e}")

    # Creates a network of type interface at channel
    # with default bitrate of 500kb/s.
    def create_network(self, device_id, device_info, interface, channel):
        # Create the bus and start a network with it.
        network = canopen.Network()
        network.connect(bustype=interface, channel=channel, bitrate=500000)
        bus = network.bus

        # Add the bus to the list.
        networkObject = (device_id, device_info, interface, network, bus)
        self.networkList.append(networkObject)
        if (self.networkList[0] is networkObject):
            self.activeNetwork = self.networkList[0]

        # Increment the count of currently connected devices
        # for this interface type.
        self.deviceCounts[interface] += 1

        # Notify the user of the added device.
        print(f"Added network of type: {interface}, "
              f"at channel {channel} for type.")

    def get_active_devices(self):
        return self.networkList
