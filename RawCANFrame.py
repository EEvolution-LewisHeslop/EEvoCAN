import customtkinter
import tk_tools
import canopen
from can import Message, Listener, Notifier

class RawCANFrame(customtkinter.CTkFrame):
    network:canopen.Network = None
    
    def __init__(self, master):
        super().__init__(master)

        # Set the weights
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Create the section header.
        self.rawCANLabel = customtkinter.CTkLabel(self, text="Raw CAN Data")
        self.rawCANLabel.grid(row=0, column=0, padx=20, pady=10, sticky="w")

        # Create logging LED
        self.led0 = tk_tools.Led(self, size=40, bg="#333333")
        self.led0.grid(row=0, column=1, padx=10, pady=0)
        self.led0.to_green(False)

        # Create the logging button.
        self.logCANButton = customtkinter.CTkButton(self, text="Log CAN", command=lambda:self.load_dbc(self.sheet))
        self.logCANButton.grid(row=0, column=2, padx=20, pady=10)

        # Create the raw CAN viewer.
        self.canText = customtkinter.CTkTextbox(self)
        self.canText.grid(row=1, column=0, columnspan=3 , padx=5, pady=(0,5), sticky="nsew")
        # Add the default text
        self.canText.configure(state='normal')
        self.canText.insert('end', "Waiting for CAN...")
        self.canText.configure(state='disabled')

    def assign_listener(self):
        # Create a listener
        listener = RawCANListener(self.canText)
        self.network.notifier.add_listener(listener)        
        print("Assigned listener to RawCANFrame")

class RawCANListener(Listener):
    def __init__(self, text:customtkinter.CTkTextbox):
        self.text=text

    def on_message_received(self, msg:Message) -> None:
        self.text.configure(state='normal')
        self.text.insert('end', str(msg)+"\n")
        self.text.configure(state='disabled')    