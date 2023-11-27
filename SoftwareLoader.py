import customtkinter
import can

from HwManager import HwManager
from CANdle import CANdle
from tkinter import filedialog
import struct

# Creates the software tab, which implements python translations of load_vs_domain.tcl
class SoftwareTab(customtkinter.CTkFrame):
    def __init__(self, master, hwManager: HwManager):
        super().__init__(master)
        self.hwManager = hwManager
        self.create_buttons()
        self.candle = CANdle(hwManager=hwManager)

    # Basic button instantiation.
    def create_buttons(self):
        self.bl_backdoor_button = customtkinter.CTkButton(self, text="VS BL Backdoor", command=self.bl_backdoor)
        self.bl_backdoor_button.pack(pady=10)

        self.bl_upload_button = customtkinter.CTkButton(self, text="VS BL Upload", command=self.bl_upload)
        self.bl_upload_button.pack(pady=10)

        self.bl_download_button = customtkinter.CTkButton(self, text="VS BL Download", command=self.bl_download)
        self.bl_download_button.pack(pady=10)

        self.bte_button = customtkinter.CTkButton(self, text="VS BTE", command=self.bte)
        self.bte_button.pack(pady=10)

        self.bootloader = customtkinter.CTkButton(self, text="BTS", command=self.bl_command)
        self.bootloader.pack(pady=10)

        self.search = customtkinter.CTkButton(self, text="Search", command=self.find_nodes)
        self.search.pack(pady=10)

    # Sends raw CAN backdoor message on the first available network.
    def bl_backdoor(self):
        message = can.Message(arbitration_id=0x0055, data=[0x46, 0xB3, 0x2E, 0x49, 0xB7, 0x6F, 0x03, 0xCB])
        # Check for an available network.
        if len(self.hwManager.activeDevices) > 0:
            bus:can.BusABC = self.hwManager.activeDevices[0].get('bus')
            bus.send(message)
        else:
            print("No devices to send bootloader backdoor.")

    # Searches for nodes
    def find_nodes(self):
        # This will attempt to read an SDO from nodes 1 - 127
        try:
            result = self.candle.search_for_nodes()
        except Exception as e:
            print(f"Error searching for nodes:\n{e}")
        return result

    # Sends raw CAN backdoor message on the first available network.
    def bl_command(self):
        # Set read command for application
        cmd = (0x01 << 8) | 0x0005
        cmd_bytes = bytearray(struct.pack('>H', cmd))
        result = self.candle.sdo_write(1, 0x5FF0, 1, cmd_bytes)
        if (not result):
            return result

    # Reads a memory space from a given memory area into a hexfile at the given path or returns read data directly.
    def bl_upload(self, nodeId=1, memorySpace="APPDATA", hexfilename=None):
        # Get the memory info for the given space.
        if (memorySpace == None):
            # Usually handle error but for basic button just read app data
            memorySpace = "APPDATA"
        memInfo = self.get_memory_info(memorySpace)
        
        # Assign read variables from meminfo
        deviceStartAddress = memInfo[0]
        deviceEndAddress = memInfo[1]
        deviceLength = memInfo[2]
        pageLength = memInfo[3]
        pad = memInfo[4]
        access = memInfo[5]
        blMemId = memInfo[6]
        
        # Check read access
        if (access != "RO" and access != "RW"):
            return "Unable to read this memory space!"
        
        # Set read command for application
        cmd = (blMemId << 8) | 0x0005
        cmd_bytes = bytearray(struct.pack('>H', cmd))
        result = self.candle.sdo_write(nodeId, 0x5FF0, 1, cmd_bytes)
        if (not result):
            return result
        
        # read the domain as a block of bytes
        CanDataBytes = self.candle.sdo_read(nodeId, 0x5FF0, 2)
        if ("Error" in CanDataBytes):
            return CanDataBytes
        
        # first 4 bytes is the length of the data
        expLength = CanDataBytes[0:3]
        dataBytes = CanDataBytes[4:]
        actLength = len(dataBytes)
        print(f"Expected amount of data = {expLength}, actual amount of data = {actLength}")
    
        # if no filename is passed, just return the output, else save to file TODO
        print(dataBytes)

    # Offers a file selection prompt and downloads the selected hex file to the controller.
    def bl_download(self, nodeId=1, memorySpace="APPDATA"):
        # Get the memory info for the given space.
        memInfo = self.get_memory_info(memorySpace)
        
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
            return "Unable to write to this memory space!"
    
        # TODO make fileopen prompts limit filetypes and point to a useful directory
        hexfileName = filedialog.askopenfilename()
        
        # Check that a file was selected.
        if (hexfileName is None):
            return "Unable to open file."

        # Read the file contents.
        with open(hexfileName) as file:
            fileContent = file.readlines()
            
        # Convert filecontents to ordered byte value dictionary with address as key.
        hexByteArray:dict = self.hex_file_to_byte_array(self, fileContent)
    
        # Try to send the write command.
        cmd = (blMemId << 8) | 0x0004
        result = self.candle.sdo_write(nodeId, 0x5FF0, 1, cmd)
        if result != "OK":
            return "Attempt to set memory ({}, {}) into write mode (0x04) failed. Result = {}".format(memorySpace, blMemId, result)
        print("Write command to {} OK".format(memorySpace))

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
                result = self.candle.sdo_write(nodeId, 0x5FF0, 2, ' '.join(map(str, byteList)))
                if result != "OK":
                    return "Attempt to write Application memory to domain object failed. Result = {}".format(result)

                print("Sent data to {:08x}".format(i))
                # Clear byteList for the next 4kB
                byteList = []

            i += 1

        # Check that bytelist is empty now, or else we didn't send everything.
        if byteList and i != paddedMaxAddr:
            return "ERROR: We've not sent all the data to the bootloader"

        return "OK"

    # Exits the current bootloader session on the given node.
    def bte(self, nodeId):
        # Ending the bootloader session with an SDO command
        if (not self.hwManager.activeCanopenNetworks):
            return "No available canopen networks for bte."
        
        result = self.candle.sdo_write(nodeId, 0x5FF0, 1, 0x0002, self.hwManager.activeCanopenNetworks[0])

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
                print(f"Received this line and don't know what to do with it: {line}")
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