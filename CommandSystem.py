import time
import struct
from tkinter import filedialog
import can
import canopen
from HwManager import HwManager
from collections import deque


# Command System creates commands and helpers
# and has "process_command" function
# which takes a string command and executes it.
class CommandSystem():
    def __init__(self, hwManager: HwManager):
        self.hwManager = hwManager
        self.helpers = Helpers(hwManager)
        self.commands = Commands(self.helpers)
        self.log = deque([], 1000)
        self.logChangedCallbacks = []

    # Calls a the command based on the provided command text.
    def process_command(self, commandText: str):
        # Basic processing just call a command with args.
        # Currently doesnt handle quotes TODO
        commandText = commandText.strip()
        commandParts = commandText.split(' ')
        try:
            commandName = commandParts[0].strip()
            command = self.commands.__getattribute__(commandName)
            commandParts.pop(0)
        except Exception:
            error = f"Unrecognized command: {commandName}"
            self.update_log((commandText, False, error, None))
            return
        try:
            result, response, output = command(commandParts)
            self.update_log((commandText, result, response, output))
        except Exception as e:
            error = ("Unhandled error in command execution of "
                     f"\"{commandName}\":\n{str(e)}")
            self.update_log((commandText, False, error, None))
            return (False, error, None)
        return result

    # Adds logLine (Command, Result, Response, Output) to the log
    # and calls the subscribed callbacks
    def update_log(self, logLine):
        self.log.appendleft(logLine)
        for callback in self.logChangedCallbacks:
            try:
                callback()
            except Exception as e:
                print(f"Error in log changed callback {callback}:\n{e}")

    # Adds a callback to be called when the log changes.
    def add_log_changed_callback(self, callback: callable):
        self.logChangedCallbacks.append(callback)


# Contains common operations performed within commands.
class Helpers():
    def __init__(self, hwManager: HwManager):
        self.hwManager = hwManager

    # Checks to see if enough args were provided and returns
    # and unpackable array based on given mandatory and optional counts.
    def process_args(self, args: list, mandatory, optional):
        argsCount = len(args)
        maxArgs = mandatory + optional
        args.insert(0, "OK")
        if (argsCount < mandatory):
            args[0] = (f"Too few arguments: Expected minimum of {mandatory} "
                       f"arguments but found {argsCount}.")
        if (argsCount > maxArgs):
            args = args[:maxArgs+1]
            args[0] = (f"Too many arguments: Expected maximum of {maxArgs} "
                       f"arguments but found {argsCount}.")
        if (argsCount < mandatory + optional):
            fillOptionalArgs = [None] * (maxArgs - (argsCount))
            args.extend(fillOptionalArgs)
        return args

    # Tries to get a network by id.
    def get_network_by_id(self, networkId):
        # Check to see if a networkId was specified,
        # if not, use the active network.
        networkObject = None
        if (networkId is None):
            if (self.hwManager.activeNetwork is None):
                error = "No network specified and no default network assigned."
                return (error, None)
            else:
                networkId = 1
        try:
            networkObject = self.hwManager.networkList[networkId-1]
            return ("OK", networkObject[3])
        except Exception:
            error = "Specified network not available."
            return (error, None)

    # Tries to get a node by id on a given network.
    def get_node_on_network_by_id(self, network: canopen.Network, nodeId):
        try:
            node = network.nodes[nodeId-1]
            return ("OK", node)
        except Exception:
            error = "Node not found on given network."
            return (error, None)

    # Gets the memory info from the given memory identifier.
    def get_memory_info(self, mem):
        #                Start    End      Len      Page     Pad   RW    BL_ID
        match mem:
            case "APP":
                result = [0x10000, 0x3FFFF, 0x30000, 0x1000,  0xFF, "WO", 0x01]
            case "APPDATA":
                result = [0x40000, 0x41FFF, 0x2000,  0x1000,  0x00, "RW", 0x02]
            case "PRODDATA":
                result = [0x7F000, 0x7FFFF, 0x1000,  0x1000,  0x00, "RW", 0x03]
            case "FRAM":
                result = [0x0,     0x0FFF,  0x1000,  0x1000,  0x00, "RW", 0x04]
            case "default":
                result = None
        if not result:
            error = "Available memories are: APP, APPDATA, PRODDATA, FRAM"
        return (error, result)

    # Converts the given hexFileContents into byteList;
    # a dictionary where the indexer is the byte address
    # and the value is the byte at that address.
    def hex_file_to_byte_array(self, hexFileContents):
        hex_code = hexFileContents.split('\n')
        hex_code_len = len(hex_code)
        if hex_code_len == 0:
            raise ValueError("Not enough data: {}".format(hex_code_len))
        line_no = 0
        finished = False
        address_msb = -1
        tot_byte_count = 0
        byteList = {}
        while line_no <= hex_code_len and not finished:
            line = hex_code[line_no]
            byte_count = int(line[1:3], 16)
            address = int(line[3:7], 16)
            type_ = int(line[7:9], 16)
            data = line[9:-2]
            checksum = int(line[-2:], 16)
            # Handling different types
            if type_ == 0x00:
                if address_msb == -1:
                    error = "Data received before new section started"
                    raise ValueError(error)
                byte_address = address_msb + address
                for byte in range(byte_count):
                    byte_data = data[byte*2:(byte*2)+2]
                    byteList[byte_address] = int(byte_data, 16)
                    byte_address += 1
                    tot_byte_count += 1
            elif type_ == 0x01:
                finished = True
            elif type_ == 0x02:
                address_msb = int(data, 16) << 4
                print(f"Type 02: data = {data}, "
                      f"address_msb = {address_msb:08x}")
            elif type_ == 0x03:
                print(f"Type 03: Byte count = {byte_count}, "
                      f"address = {address}, type = {type_}, "
                      f"data = {data}, checksum = {checksum}")
            elif type_ == 0x04:
                address_msb = int(data, 16) << 16
                print(f"Type 04: data = {data}, "
                      f"address_msb = {address_msb:08x}")
            elif type_ == 0x05:
                print(f"Type 05: data = {data}. "
                      "This is where the program execution will start. "
                      "We can ignore this.")
            else:
                finished = True
                raise ValueError(f"Error: Unexpected type ({type_})")
            line_no += 1
        return sorted(byteList)


# Contains all available commands.
class Commands():
    def __init__(self, helpers: Helpers):
        self.helpers = helpers

    # Echos any arguments back as a string.
    # Useful for checking that the command system is working.
    def echo(self, args):
        return (True, " ".join(args), " ".join(args))

    # Forcefully searches for nodes on the given or default networkId.
    def search(self, args):
        errStr = "Search unsuccessful: "
        # Process arguments.
        args = self.helpers.process_args(args, 0, 1)
        error, networkId = args
        if (error != "OK"):
            return (False, errStr + error, None)
        # Get the network associated with by given networkId.
        error, network = self.helpers.get_network_by_id(networkId)
        if (error != "OK"):
            return (False, errStr + error, None)
        # Start search.
        network.scanner.search()
        # We may need to wait a short while here to allow all nodes to respond.
        time.sleep(0.05)
        # Process scanner results.
        for node_id in network.scanner.nodes:
            network.add_node(node_id)
        if (len(network.scanner.nodes) > 0):
            result = f"Success. Found: {network.scanner.nodes}."
            return (True, result, network.scanner.nodes)
        else:
            return (False, errStr + "No nodes found.", None)

    # Sdo read based on the use of SdoServer
    def sdo_r(self, args):
        errStr = "SDO read operation unsuccessful: "
        # Process arguments.
        args = self.helpers.process_args(args, 3, 1)
        error, nodeId, index, subindex, networkId = args
        if (error != "OK"):
            return (False, errStr + error, None)
        # Get the network associated with by given networkId.
        error, network = self.helpers.get_network_by_id(networkId)
        if (error != "OK"):
            return (False, errStr + error, None)
        # Get the node on the network by given nodeId.
        error, node = self.helpers.get_node_on_network_by_id(
            network=network,
            nodeId=nodeId)
        if (error != "OK"):
            return (False, errStr + error, None)
        # Send the SDO
        try:
            # Read
            data = node.sdo.upload(index, subindex)
            response = (f"Success. Read {data} from node {nodeId} "
                        f"on network {networkId} at index {index} "
                        f"and subindex {subindex}.")
            return (True, response, data)
        except Exception as e:
            return (False, errStr + f"{e}", None)

    # Tries to sdo write given data to the given address
    # by nodeId index subindex on the given networkId.
    def sdo_w(self, args):
        errStr = "SDO write operation unsuccessful: "
        # Process arguments.
        args = self.helpers.process_args(args, 4, 1)
        error, nodeId, index, subindex, data, networkId = args
        if (error != "OK"):
            return (False, errStr + error, None)
        # Get the network associated with by given networkId.
        error, network = self.helpers.get_network_by_id(networkId)
        if (error != "OK"):
            return (False, errStr + error, None)
        # Get the node on the network by given nodeId.
        error, node = self.helpers.get_node_on_network_by_id(
            network=network,
            nodeId=nodeId)
        if (error != "OK"):
            return (False, errStr + error, None)
        # Send the SDO
        try:
            # Write sdo
            node.sdo.download(index, subindex, data)
            result = (f"Success. Wrote {data} to node {nodeId} on network "
                      f"{networkId} at index {index} and subindex {subindex}.")
            return (True, result, True)
        except Exception as e:
            return (False, errStr + f"{e}", None)

    def backdoor(self, args):
        errStr = "Backdoor unseccessful: "
        # Process arguments.
        args = self.helpers.process_args(args, 0, 1)
        error, networkId = args
        if (error != "OK"):
            return (False, errStr + error, None)
        # Get the network associated with by given networkId.
        error, network = self.helpers.get_network_by_id(networkId)
        if (error != "OK"):
            return (False, errStr + error, None)
        # Send backdoor.
        message = can.Message(
            arbitration_id=0x0055,
            data=[0x46, 0xB3, 0x2E, 0x49, 0xB7, 0x6F, 0x03, 0xCB])
        bus: can.BusABC = network.bus
        bus.send(message)
        return (True, "Success. Backdoor sent.", True)

    # Attempts to begin a bootloader session on
    # a given node on an optionally given network.
    def bts(self, args):
        errStr = "Bootloader entry attempt unseccessful: "
        # Process arguments.
        args = self.helpers.process_args(args, 1, 1)
        error, nodeId, networkId = args
        if (error != "OK"):
            return (False, errStr + error, None)
        cmd = (0x01 << 8) | 0x0005
        data = bytearray(struct.pack('>H', cmd))
        return self.sdo_w([nodeId, 0x5FF0, 1, data, networkId])

    # Attempts to exit a bootloader session on
    # a given node on an optionally given network.
    def bte(self, args):
        errStr = "Bootloader exit attempt unseccessful: "
        # Process arguments.
        args = self.helpers.process_args(args, 1, 1)
        error, nodeId, networkId = args
        if (error != "OK"):
            return (False, errStr + error, None)
        return self.sdo_w([nodeId, 0x5FF0, 1, 0x0002, networkId])

    # Reads a memory space from a given memory area into
    # a hexfile at the given path or returns read data directly.
    def upload(self, args):
        errStr = "Upload unseccessful: "
        # Process arguments.
        args = self.helpers.process_args(args, 2, 2)
        error, nodeId, memorySpace, hexfilename, networkId = args
        if (error != "OK"):
            return (False, errStr + error, None)
        # Get the memory info for the given space.
        error, memInfo = self.helpers.get_memory_info(memorySpace)
        if not memInfo:
            return (False, errStr + error, None)
        # Assign read variables from meminfo.
        # deviceStartAddress = memInfo[0]
        # deviceEndAddress = memInfo[1]
        # deviceLength = memInfo[2]
        # pageLength = memInfo[3]
        # pad = memInfo[4]
        access = memInfo[5]
        blMemId = memInfo[6]
        # Check read access.
        if (access != "RO" and access != "RW"):
            return (False, errStr + "Unable to read this memory space!", None)
        # Set read ready signal in application.
        cmd = (blMemId << 8) | 0x0005
        cmd_bytes = bytearray(struct.pack('>H', cmd))
        result, error, output = self.sdo_w(
            [nodeId, 0x5FF0, 1, cmd_bytes, networkId])
        if (not result):
            return result, errStr + error
        # Read the domain as a block of bytes.
        result, error, output = self.sdo_r([nodeId, 0x5FF0, 2])
        if (not result):
            return result, errStr + error
        # The first 4 bytes is the length of the data.
        expLength = output[0:3]
        dataBytes = output[4:]
        actLength = len(dataBytes)
        print(f"Expected amount of data = {expLength}, "
              f"actual amount of data = {actLength}")
        # If no filename is passed, just return the output,
        # else save to file. TODO
        return (True, error, output)

    # Offers a file selection prompt and downloads the
    # selected hex file to the controller.
    def download(self, args):
        errStr = "Download unseccessful: "
        # Process arguments.
        args = self.helpers.process_args(args, 2, 1)
        error, nodeId, memorySpace, networkId = args
        if (error != "OK"):
            return (False, errStr + error, None)
        # Get the memory info for the given space.
        error, memInfo = self.helpers.get_memory_info(memorySpace)
        if not memInfo:
            return (False, errStr + error, None)
        # Assign read variables from meminfo
        deviceStartAddress = memInfo[0]
        # deviceEndAddress = memInfo[1]
        # deviceLength = memInfo[2]
        pageLength = memInfo[3]
        pad = memInfo[4]
        access = memInfo[5]
        blMemId = memInfo[6]
        # Check write access
        if (access != "WO" and access != "RW"):
            errStr += "Unable to write to this memory space!"
            return (False, errStr, None)
        # Prompt for filename
        hexfileName = filedialog.askopenfilename()
        # Check that a file was selected.
        if (hexfileName is None):
            errStr += "Unable to open file."
            return (False, errStr, None)
        # Read the file contents.
        with open(hexfileName) as file:
            fileContent = file.readlines()
        # Convert filecontents to ordered byte value dictionary
        # with address as key.
        try:
            hexByteArray: dict = self.hex_file_to_byte_array(self, fileContent)
        except Exception as e:
            errStr += f"File was not of hex type: {e}"
            return (False, errStr, None)
        # Try to send the write ready signal.
        cmd = (blMemId << 8) | 0x0004
        cmd_bytes = bytearray(struct.pack('>H', cmd))
        result, error, output = self.sdo_w(
            [nodeId, 0x5FF0, 1, cmd_bytes, networkId])
        if (not result):
            errStr += (f"Attempt to set memory ({memorySpace}, {blMemId})"
                       f"into write mode (0x04) failed with result: {result}")
            return (False, errStr, None)
        # Pad out hex array to 4kB boundary.
        paddedMaxAddr = hexByteArray.keys[-1]
        while (paddedMaxAddr + 1 - deviceStartAddress) % pageLength != 0:
            paddedMaxAddr += 1
            hexByteArray[paddedMaxAddr] = pad
        # Send the data in 4kB blocks.
        byteList = []
        i = hexByteArray.keys[0]
        while i <= paddedMaxAddr:
            byteList.append(hexByteArray.get(i, pad))
            if len(byteList) >= pageLength:
                data = ' '.join(map(str, byteList))
                sdoResponse = self.sdo_w([nodeId, 0x5FF0, 2, data, networkId])
                result, error, output = sdoResponse
                if (not result):
                    errStr += ("Attempt to write Application memory to"
                               f"domain object failed with result: {result}")
                    return (False, errStr, None)
                # Clear byteList for the next 4kB
                byteList = []
            i += 1
        # Check that bytelist is empty now, or else we didn't send everything.
        if byteList and i != paddedMaxAddr:
            errStr += "We've not sent all the data to the bootloader"
            return (False, errStr, None)
        errStr += (f"Successfully wrote file {hexfileName}"
                   f"to the memory space {memorySpace}.")
        return (True, errStr, True)
