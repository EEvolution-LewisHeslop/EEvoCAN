import customtkinter

# Creates the basic tab
class BasicTab(customtkinter.CTkFrame):
    def __init__(self, master: customtkinter.CTkFrame):
        super().__init__(master)
        self.button = customtkinter.CTkButton(self, text="Hello")
        self.button.grid(row=0, column=0, sticky="nsew")