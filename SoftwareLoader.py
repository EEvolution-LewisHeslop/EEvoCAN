import customtkinter
import can
import canopen

from HwManager import HwManager

# Creates the software tab
class SoftwareTab(customtkinter.CTkFrame):
    def __init__(self, master, hwManager: HwManager):
        super().__init__(master)
        self.hw_manager = hwManager
        self.create_buttons()

    def create_buttons(self):
        self.bl_backdoor_button = customtkinter.CTkButton(self, text="VS BL Backdoor", command=self.vs_bl_backdoor)
        self.bl_backdoor_button.pack(pady=10)

        self.bl_upload_button = customtkinter.CTkButton(self, text="VS BL Upload", command=self.vs_bl_upload)
        self.bl_upload_button.pack(pady=10)

        self.bl_download_button = customtkinter.CTkButton(self, text="VS BL Download", command=self.vs_bl_download)
        self.bl_download_button.pack(pady=10)

        self.bte_button = customtkinter.CTkButton(self, text="VS BTE", command=self.vs_bte)
        self.bte_button.pack(pady=10)

    def vs_bl_backdoor(self):
        # Sending a specific CAN message
        message = can.Message(arbitration_id=0x0055, data=[0x46, 0xB3, 0x2E, 0x49, 0xB7, 0x6F, 0x03, 0xCB])
        self.hw_manager.activeBuses[0].send(message)

    def vs_bl_upload(self, node_id, memory_space, hexfilename=None):
        # Implement the memory read logic here
        # Use canopen.SdoClient for SDO upload
        pass

    def vs_bl_download(self, node_id, memory_space, hexfilename=None):
        # Implement the memory write logic here
        # Use canopen.SdoClient for SDO download
        pass

    def vs_bte(self, node_id):
        # Ending the bootloader session with an SDO command
        # Example: sending a specific SDO command
        network = canopen.Network()
        network.connect(channel=self.hw_manager.activeBuses[0].channel_info, bustype='socketcan')
        node = network.add_node(node_id, 'path_to_eds_file.eds')
        node.sdo[0x5FF0][1].raw = 0x0002
        network.disconnect()