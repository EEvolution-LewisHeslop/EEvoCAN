import customtkinter
import canopen
import CommandSystem
from HwManager import HwManager
from CommandSystem import CommandSystem

class CliFrame(customtkinter.CTkFrame):
    def __init__(self, master, hwManager:HwManager, commandSystem:CommandSystem):
        super().__init__(master)
        self.hwManager = hwManager
        self.commandSystem = commandSystem
        # Set the weights
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Create the section header
        self.CliLabel = customtkinter.CTkLabel(self, text="CLI Frame")
        self.CliLabel.grid(row=0, column=0, padx=20, pady=10, sticky="w")

        # Create the CLI log
        self.cliText = customtkinter.CTkTextbox(self)
        self.cliText.grid(row=1, column=0, columnspan=2, padx=5, pady=(0,5), sticky="nsew")
        # Add the default text
        self.cliText.configure(state='normal')
        self.cliText.insert('end', "Waiting for Commands...\n")
        self.cliText.configure(state='disabled')

        # Create the entry for the CLI
        self.cliEntry = CliEntry(self, height=30, logBox=self.cliText, hwManager=hwManager, commandSystem=commandSystem)
        self.cliEntry.grid(row=2, column=0, columnspan=2, padx=5, pady=(0,5), sticky="ew")

        # Create the send button.
        self.cliSend = customtkinter.CTkButton(self, height=30, text="Send")
        self.cliSend.grid(row=2, column=1, padx=5, pady=(0,5))

class CliEntry(customtkinter.CTkTextbox):
    historyIndex = 0
    history = []
    def __init__(self, master, height, logBox:customtkinter.CTkTextbox,  hwManager:HwManager, commandSystem:CommandSystem):
        super().__init__(master, height=height)
        self.logBox = logBox
        self.hwManager = hwManager
        self.commandSystem = commandSystem
        # Bind enter to send command
        self.bind('<Key>', self.callback)
        # Bind to command log
        self.commandSystem.add_log_changed_callback(self.log_changed)

    def callback(self, event, *args):
        # Get the value on the cursors current row.
        if (event.keysym == 'Up'):
            if (len(self.history) > self.historyIndex):
                # Increase history index and set cli value to that element in history.
                self.historyIndex +=1
                self.set_text_value(self.history[self.historyIndex-1].strip())
            else:
                # Do nothing.
                return "break"
        if (event.keysym == 'Down'):
            if (self.historyIndex > 1):
                # Decrease history index and set cli value to that element in history.
                self.historyIndex -=1
                self.set_text_value(self.history[self.historyIndex-1])
            elif (self.historyIndex == 1):
                # Decrease history index and set cli value to blank.
                self.historyIndex -=1
                self.set_text_value("")
            else:
                # Do nothing
                return "break"
        if (event.keysym == 'Return'):
            # Get the current rowtext.
            index = self.index('insert')
            row, column = index.split('.')
            rowText = self.get(index1=(row +'.0'), index2=(str(int(row)+1)+'.0'))

            # If there was no text, exit early.
            if(rowText.strip() == ""):
                return "break"

            # Add the current text to the history.
            self.history.insert(0, rowText)

            # Set the history index to 0.
            self.historyIndex = 0

            # Set the text to nothing.
            self.set_text_value("")

            # Send the command to the command system
            status, logText, output = self.commandSystem.process_command(rowText)
            return "break"

    def log_changed(self):
        # Post the result to the CLI log.
        self.logBox.configure(state='normal')
        self.logBox.delete(1.0, 'end')
        self.logBox.insert('end', '\n'.join(reversed(self.commandSystem.log)))
        self.logBox.configure(state='disabled')   
        self.logBox.see('end')

    # Sets the entry text to the given text value.
    def set_text_value(self, text):
        index = self.index('insert')
        row, column = index.split('.')
        self.delete(index1=(row +'.0'), index2=(str(int(row)+1)+'.0'))
        self.insert('end', str(text))
