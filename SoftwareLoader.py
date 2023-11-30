import customtkinter
from CommandSystem import CommandSystem


# Creates the software tab@.
# Implements python translations of load_vs_domain.tcl
class SoftwareTab(customtkinter.CTkFrame):
    def __init__(self, master, commandSystem: CommandSystem):
        super().__init__(master)
        self.commandSystem = commandSystem
        self.create_buttons()

    # Basic button instantiation.
    def create_buttons(self):
        self.bl_backdoor_button = customtkinter.CTkButton(
            self,
            text="Backdoor",
            command=lambda: self.commandSystem.process_command(
                "backdoor 1"))
        self.bl_backdoor_button.pack(pady=10)

        self.bl_upload_button = customtkinter.CTkButton(
            self,
            text="Upload",
            command=lambda: self.commandSystem.process_command(
                "upload 1 APPDATA"))
        self.bl_upload_button.pack(pady=10)

        self.bl_download_button = customtkinter.CTkButton(
            self,
            text="Download",
            command=lambda: self.commandSystem.process_command(
                "download 1 APPDATA"))
        self.bl_download_button.pack(pady=10)

        self.bte_button = customtkinter.CTkButton(
            self,
            text="BTE",
            command=lambda: self.commandSystem.process_command(
                "bte 1"))
        self.bte_button.pack(pady=10)

        self.bootloader = customtkinter.CTkButton(
            self,
            text="BTS",
            command=lambda: self.commandSystem.process_command(
                "bts 1"))
        self.bootloader.pack(pady=10)

        self.search = customtkinter.CTkButton(
            self,
            text="Search",
            command=lambda: self.commandSystem.process_command(
                "search"))
        self.search.pack(pady=10)
