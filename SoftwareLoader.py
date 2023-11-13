import customtkinter

# Creates the software tab
class SoftwareTab(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.button = customtkinter.CTkButton(self, text="software")
        self.button.grid(row=0, column=0, sticky="nsew")