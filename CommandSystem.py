import time
import struct
from tkinter import filedialog
import can
import canopen
from HwManager import HwManager
from collections import deque

# Command System creates commands and helpers and has "process_command" function which takes a string command and executes it.
class CommandSystem():
    def __init__(self, hwManager:HwManager):
        self.hwManager = hwManager
        self.helpers = Helpers(hwManager)
        self.commands = Commands(self.helpers)
        self.results = deque([],1000)
        self.log = deque([],1000)
        self.output = deque([],1000)
        self.logChangedCallbacks = []

    # Calls a the command based on the provided command text.
    def process_command(self, commandText:str):
        # Basic processing just call a command with args.
        commandParts = commandText.strip().split(' ')
        try:
            commandName = commandParts[0].strip()
            command = self.commands.__getattribute__(commandName)
            commandParts.pop(0)
        except:
            self.results.appendleft(False)
            self.log.appendleft(commandText.strip())
            self.log.appendleft(f"Unrecognized command: {commandName}")
            self.output.appendleft(None)
            self.log_changed()
            return (False, f"Unrecognized command: {commandName}", None)
        try:
            result = command(commandParts)
            self.results.appendleft(result[0])
            self.log.appendleft(commandText.strip())
            self.log.appendleft(result[1])
            self.output.appendleft(result[2])
            self.log_changed()
            
        except Exception as e:        
            self.results.appendleft(False)
            self.log.appendleft(commandText.strip())
            self.log.appendleft(f"Unhandled error in command execution of \"{commandName}\":\n{str(e)}")
            self.output.appendleft(None)
            self.log_changed()  
            return (False, f"Unhandled error in command execution of \"{commandName}\":\n{str(e)}", None)
        return result
    
    # Adds a callback to be called when the log changes.
    def add_log_changed_callback(self, callback:callable):
        self.logChangedCallbacks.append(callback)
    
    # When the log is changed, raises log callbacks.
    def log_changed(self):
        for callback in self.logChangedCallbacks:
            try:
                callback()
            except Exception as e:
                print(f"Error in log changed callback {callback}:\n{e}")


# Contains common operations performed within commands.
class Helpers():
    def __init__(self, hwManager:HwManager):
        self.hwManager = hwManager

    # Checks to see if enough args were provided and returns and unpackable array based on given mandatory and optional counts.
    def process_args(self, args:list, mandatory, optional):
        argsCount = len(args)
        maxArgs = mandatory + optional
        args.insert(0, "OK")
        if (argsCount < mandatory):
            args[0] = f"Too few arguments: Expected minimum of {mandatory} arguments but found {argsCount}."
        if (argsCount > maxArgs):
            args = args[:maxArgs+1]
            args[0] = f"Too many arguments: Expected maximum of {maxArgs} arguments but found {argsCount}."
        if (argsCount < mandatory + optional):
            fillOptionalArgs = [None] * (maxArgs - (argsCount))
            args.extend(fillOptionalArgs)
        return args

    # Tries to get a network by id.
    def get_network_by_id(self, networkId):
        # Check to see if a networkId was specified, if not, use the active network.
        networkObject = None
        if (networkId is None):
            if (self.hwManager.activeNetwork is None):
                return ("No network specified and no default network assigned.", None)
            else:
                networkId = 1
        try:
            networkObject = self.hwManager.networkList[networkId-1]
            return ("OK", networkObject[3])
        except:
            return ("Specified network not available.", None)
    
    # Tries to get a node by id on a given network.
    def get_node_on_network_by_id(self, network:canopen.Network, nodeId):
        try:
            node = network.nodes[nodeId-1]
            return ("OK", None)
        except:
            return (f"Node not found on given network.", None)

    # Gets the memory info from the given memory identifier.
    def get_memory_info(self, mem):
        #                                Start    End      Len      Page     Pad   RW    BL_ID
        match mem:
            case "APP": result =        [0x10000, 0x3FFFF, 0x30000, 0x1000,  0xFF, "WO", 0x01]
            case "APPDATA": result =    [0x40000, 0x41FFF, 0x2000,  0x1000,  0x00, "RW", 0x02]
            case "PRODDATA": result =   [0x7F000, 0x7FFFF, 0x1000,  0x1000,  0x00, "RW", 0x03]
            case "FRAM": result =       [0x0,     0x0FFF,  0x1000,  0x1000,  0x00, "RW", 0x04]
            case "default": result =    None
        if not result: print("Available memories are: APP, APPDATA, PRODDATA, FRAM")
        return result
    
    # Converts the given hexFileContents into byteList, a dictionary where the indexer is the byte address and the value is the byte at that address.
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
                    raise ValueError("Data received before new section started")
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
                print(f"Type 02: data = {data}, address_msb = {address_msb:08x}")
            elif type_ == 0x03:
                print(f"Type 03: Byte count = {byte_count}, address = {address}, type = {type_}, data = {data}, checksum = {checksum}")
            elif type_ == 0x04:
                address_msb = int(data, 16) << 16
                print(f"Type 04: data = {data}, address_msb = {address_msb:08x}")
            elif type_ == 0x05:
                print(f"Type 05: data = {data}. This is where the program execution will start. We can ignore this.")
            else:
                finished = True
                raise ValueError(f"Error: Unexpected type ({type_})")
            line_no += 1
        return sorted(byteList)

# Contains all available commands.
class Commands():
    def __init__(self, helpers:Helpers):
        self.helpers=helpers

    # Echos any arguments back as a string. Useful for checking that the command system is working.
    def echo(self, args):
        return (True, " ".join(args), " ".join(args))
    
    # Forcefully searches for nodes on the given or default networkId.
    def search(self, args):
        errStr = "Search unsuccessful: "
        # Process arguments.
        error, networkId = self.helpers.process_args(args, 0, 1)
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
            return (True, f"Success. Found: {network.scanner.nodes}.", network.scanner.nodes)
        else:
            return (False, errStr + "No nodes found.", None)

    # Sdo read based on the use of SdoServer
    def sdo_r(self, args):
        errStr = "SDO read operation unsuccessful: "
        # Process arguments.
        error, nodeId, index, subindex, networkId = self.helpers.process_args(args, 3, 1)
        if (error != "OK"):
            return (False, errStr + error, None)
        # Get the network associated with by given networkId.
        error, network = self.helpers.get_network_by_id(networkId)
        if (error != "OK"):
            return (False, errStr + error, None)
        # Get the node on the network by given nodeId.
        error, node = self.helpers.get_node_on_network_by_id(network=network, nodeId=nodeId)
        if (error != "OK"):
            return (False, errStr + error, None)
        # Send the SDO
        try:
            # Read
            data = node.sdo.upload(index, subindex)
            return (True, f"Success. Read {data} from node {nodeId} on network {networkId} at index {index} and subindex {subindex}.", data)
        except Exception as e:
            return (False, errStr + f"{e}", None)

    # Tries to sdo write given data to the given address by nodeId index subindex on the given networkId.
    def sdo_w(self, args):  
        errStr = "SDO write operation unsuccessful: "
        # Process arguments.
        error, nodeId, index, subindex, data, networkId = self.helpers.process_args(args, 4, 1)
        if (error != "OK"):
            return (False, errStr + error, None)
        # Get the network associated with by given networkId.
        error, network = self.helpers.get_network_by_id(networkId)
        if (error != "OK"):
            return (False, errStr + error, None)
        # Get the node on the network by given nodeId.
        error, node = self.helpers.get_node_on_network_by_id(network=network, nodeId=nodeId)
        if (error != "OK"):
            return (False, errStr + error, None)
        # Send the SDO
        try:
            # Write sdo
            node.sdo.download(index, subindex, data)
            return (True, f"Success. Wrote {data} to node {nodeId} on network {networkId} at index {index} and subindex {subindex}.", True)
        except Exception as e:
            return (False, errStr + f"{e}", None)
        
    def backdoor(self, args):
        errStr = "Backdoor unseccessful: "
        # Process arguments.
        error, networkId = self.helpers.process_args(args, 0, 1)
        if (error != "OK"):
            return (False, errStr + error, None)
        # Get the network associated with by given networkId.
        error, network = self.helpers.get_network_by_id(networkId)
        if (error != "OK"):
            return (False, errStr + error, None)
        # Send backdoor.
        message = can.Message(arbitration_id=0x0055, data=[0x46, 0xB3, 0x2E, 0x49, 0xB7, 0x6F, 0x03, 0xCB])
        bus:can.BusABC = network.bus
        bus.send(message)
        return (True, "Success. Backdoor sent.", True)

    # Attempts to begin a bootloader session on a given node on an optionally given network.
    def bts(self, args):
        errStr = "Bootloader entry attempt unseccessful: "
        # Process arguments.
        error, nodeId, networkId = self.helpers.process_args(args, 1, 1)
        if (error != "OK"):
            return (False, errStr + error, None)
        cmd = (0x01 << 8) | 0x0005
        data = bytearray(struct.pack('>H', cmd))
        return self.sdo_w([nodeId, 0x5FF0, 1, data, networkId])
    
    # Attempts to exit a bootloader session on a given node on an optionally given network.
    def bte(self, args):
        errStr = "Bootloader exit attempt unseccessful: "
        # Process arguments.
        error, nodeId, networkId = self.helpers.process_args(args, 1, 1)
        if (error != "OK"):
            return (False, errStr + error, None)
        return self.sdo_w([nodeId, 0x5FF0, 1, 0x0002, networkId])
    
    # Reads a memory space from a given memory area into a hexfile at the given path or returns read data directly.
    def upload(self, args):
        errStr = "Upload unseccessful: "
        # Process arguments.
        error, nodeId, memorySpace, hexfilename, networkId = self.helpers.process_args(args, 2, 2)
        if (error != "OK"):
            return (False, errStr + error, None)
        # Get the memory info for the given space.
        memInfo = self.helpers.get_memory_info(memorySpace)
        # Assign read variables from meminfo.
        deviceStartAddress = memInfo[0]
        deviceEndAddress = memInfo[1]
        deviceLength = memInfo[2]
        pageLength = memInfo[3]
        pad = memInfo[4]
        access = memInfo[5]
        blMemId = memInfo[6]
        # Check read access.
        if (access != "RO" and access != "RW"):
            return (False, errStr + "Unable to read this memory space!", None)
        # Set read ready signal in application.
        cmd = (blMemId << 8) | 0x0005
        cmd_bytes = bytearray(struct.pack('>H', cmd))
        result, error, output = self.sdo_w([nodeId, 0x5FF0, 1, cmd_bytes, networkId])
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
        print(f"Expected amount of data = {expLength}, actual amount of data = {actLength}")
        # If no filename is passed, just return the output, else save to file. TODO
        return (True, error, output)
    
    # Offers a file selection prompt and downloads the selected hex file to the controller.
    def download(self, args):
        errStr = "Download unseccessful: "
        # Process arguments.
        error, nodeId, memorySpace, networkId = self.helpers.process_args(args, 2, 1)
        if (error != "OK"):
            return (False, errStr + error, None)
        # Get the memory info for the given space.
        memInfo = self.helpers.get_memory_info(memorySpace)
        # Assign read variables from meminfo
        deviceStartAddress = memInfo[0]
        deviceEndAddress = memInfo[1]
        deviceLength = memInfo[2]
        pageLength = memInfo[3]
        pad = memInfo[4]
        access = memInfo[5]
        blMemId = memInfo[6]
        # Check write access
        if (access != "WO" and access != "RW"):
            return (False, errStr + "Unable to write to this memory space!", None)
        # Prompt for filename
        hexfileName = filedialog.askopenfilename()
        # Check that a file was selected.
        if (hexfileName is None):
            return (False, errStr + "Unable to open file.", None)
        # Read the file contents.
        with open(hexfileName) as file:
            fileContent = file.readlines()
        # Convert filecontents to ordered byte value dictionary with address as key.
        try:
            hexByteArray:dict = self.hex_file_to_byte_array(self, fileContent)
        except:
            return (False, errStr + "File was not of hex type.", None)
        # Try to send the write ready signal.
        cmd = (blMemId << 8) | 0x0004
        cmd_bytes = bytearray(struct.pack('>H', cmd))
        result, error, output = self.sdo_w([nodeId, 0x5FF0, 1, cmd_bytes, networkId])
        if (not result):
            return (False, errStr + f"Attempt to set memory ({memorySpace}, {blMemId}) into write mode (0x04) failed with result: {result}", None)
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
                result, error, output = self.sdo_w([nodeId, 0x5FF0, 2, ' '.join(map(str, byteList)), networkId])
                if (not result):
                    return (False, errStr + f"Attempt to write Application memory to domain object failed with result: {result}", None)
                # Clear byteList for the next 4kB
                byteList = []
            i += 1
        # Check that bytelist is empty now, or else we didn't send everything.
        if byteList and i != paddedMaxAddr:
            return (False, errStr + f"We've not sent all the data to the bootloader", None)
        return (True, f"Successfully wrote file {hexfileName} to the memory space {memorySpace}.", True)
