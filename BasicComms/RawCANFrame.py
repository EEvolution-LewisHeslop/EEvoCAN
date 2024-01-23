import customtkinter
import tk_tools
import canopen
from can import Message, Listener
import time


class RawCANFrame(customtkinter.CTkFrame):
    network: canopen.Network = None

    def __init__(self, master, network=None):
        super().__init__(master)
        self.network = network

        # Set the weights
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Create the section header.
        self.rawCANLabel = customtkinter.CTkLabel(self, text="Raw CAN Data")
        self.rawCANLabel.grid(row=0, column=0, padx=20, pady=10, sticky="w")

        # Create the scroll to bottom checkbox.
        self.scrollToBottomCheckbox = customtkinter.CTkCheckBox(
            self,
            text="Scroll to Bottom")
        self.scrollToBottomCheckbox.select()
        self.scrollToBottomCheckbox.grid(
            row=0,
            column=0,
            padx=20,
            pady=10,
            sticky='e')

        # Create logging LED
        self.led0 = tk_tools.Led(self, size=40, bg="#333333")
        self.led0.grid(row=0, column=1, padx=10, pady=0)
        self.led0.to_green(False)

        # Create the logging button.
        self.logCANButton = customtkinter.CTkButton(
            self,
            text="Log CAN",
            command=lambda: self.load_dbc(self.sheet))
        self.logCANButton.grid(row=0, column=2, padx=20, pady=10)

        # Create the raw CAN viewer.
        self.canText = customtkinter.CTkTextbox(self, font=("Courier", 12))
        self.canText.grid(
            row=1,
            column=0,
            columnspan=3,
            padx=5,
            pady=(0, 5),
            sticky="nsew")
        # Add the default text
        self.canText.configure(state='normal')
        self.canText.insert('end', "Waiting for CAN...\n")
        self.canText.configure(state='disabled')

        if (self.network is not None):
            self.assign_listener()

    def assign_listener(self):
        # Create a listener
        listener = RawCANListener(
            self.canText,
            self.led0,
            self.scrollToBottomCheckbox)
        self.network.notifier.add_listener(listener)
        print("Assigned listener to RawCANFrame")


class RawCANListener(Listener):
    def __init__(self,
                 text: customtkinter.CTkTextbox,
                 led: tk_tools.Led,
                 scrollToBottom:
                 customtkinter.CTkCheckBox):
        self.text = text
        self.led = led
        self.scrollToBottom = scrollToBottom

    def on_message_received(self, msg: Message) -> None:
        self.led.to_green(True)
        time.sleep(0.02)
        try:
            self.text.configure(state='normal')
            self.text.insert('end', str(msg).strip().replace('  ', ' ')+"\n")
            self.text.configure(state='disabled')
            if (self.scrollToBottom.get()):
                self.text.see('end')
            self.led.to_green(False)
        except Exception as e:
            print(f"Error updating can log: {e}")
