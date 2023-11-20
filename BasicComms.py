import customtkinter

# Creates the basic tab
class BasicTab(customtkinter.CTkFrame):
    def __init__(self, master: customtkinter.CTkFrame):
        super().__init__(master)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Create the four frames:
        self.buttonA = customtkinter.CTkButton(self, text="Hello")
        self.buttonA.grid(row=0, column=0, sticky="nsew")
        self.buttonB = customtkinter.CTkButton(self, text="Hello")
        self.buttonB.grid(row=0, column=1, sticky="nsew")
        self.buttonC = customtkinter.CTkButton(self, text="Hello")
        self.buttonC.grid(row=1, column=0, sticky="nsew")
        self.buttonD = customtkinter.CTkButton(self, text="Hello")
        self.buttonD.grid(row=1, column=1, sticky="nsew")