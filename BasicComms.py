import customtkinter
from tksheet import Sheet
import cantools
import os
import tk_tools

from tkinter import filedialog

# Creates the basic tab
class BasicTab(customtkinter.CTkFrame):
    def __init__(self, master: customtkinter.CTkFrame):
        super().__init__(master)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Create the four frames:
        self.RawCANFrame = RawCANFrame(self)
        self.RawCANFrame.grid(row=0, column=0, sticky="nsew")

        self.dbcFrame = DbcFrame(self)
        self.dbcFrame.grid(row=0, column=1, sticky="nsew")

        self.CliFrame = CliFrame(self)
        self.CliFrame.grid(row=1, column=0, sticky="nsew")

        self.buttonD = customtkinter.CTkButton(self, text="GAUGES")
        self.buttonD.grid(row=1, column=1, sticky="nsew")

class CliFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        # Set the weights
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Create the section header
        self.CliLabel = customtkinter.CTkLabel(self, text="CLI Frame")
        self.CliLabel.grid(row=0, column=0, padx=20, pady=10, sticky="w")

        # Create the CLI log
        self.canText = customtkinter.CTkTextbox(self)
        self.canText.grid(row=1, column=0, columnspan=3 , padx=5, pady=(0,5), sticky="nsew")
        # Add the default text
        self.canText.configure(state='normal')
        self.canText.insert('end', "Waiting for Commands...")
        self.canText.configure(state='disabled')

        # Create the entry for the cli

class RawCANFrame(customtkinter.CTkFrame):
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

        # Create the logging buttons.

class DbcFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.configure(fg_color="darkslategray", corner_radius=6)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Create the section header.
        self.dbcLabel = customtkinter.CTkLabel(self, text="DBC / EDS View")
        self.dbcLabel.grid(row=0, column=0, padx=20, pady=10, sticky="w")

        # Create load dbc button
        self.loadDbcButton = customtkinter.CTkButton(self, text="Load DBC", command=lambda:self.load_dbc(self.sheet))
        self.loadDbcButton.grid(row=0, column=1, padx=20, pady=10)

        # Create Sheet
        self.sheet = Sheet(self, theme="dark green")
        self.sheet.enable_bindings()
        self.sheet.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=(0,5))
        self.sheet.extra_bindings([("begin_edit_cell", self.begin_edit_cell),
                                   ("end_edit_cell", self.end_edit_cell)])
        self.sheet.headers(newheaders=["Message", "Signal", "Value", "Unit", "Ticks"])
        self.sheet.edit_bindings(False)

        # Load DBC
        self.load_dbc(filePath=os.path.join(os.getcwd(), "resources\\default.dbc"))
        
    def begin_edit_cell(self, event = None):
        return event.text

    def end_edit_cell(self, event = None):
        # Validate user input.
        if event.text is None:
            return
        trimmed = event.text.replace(" ", "")
        try:
            trimmed = float(trimmed)
            return float("{:.3f}".format(trimmed))
        except ValueError:
            print("Sheet input was non-numeric.")
    
    # Prompt the user to open a dbc file and then parses the content of the DBC file, binding callbacks
    def load_dbc(self, filePath=None):
        print("loading dbc")
        if (filePath is None):
            filePath = filedialog.askopenfilename()

        # Check that a file was selected.
        if (filePath is None):
            return "Unable to open file."

        # load the contents of the file
        dbcContent = cantools.db.load_file(filePath)

        # Create a dictionary of signalnames vs rows and values and ticks.
        self.activeSignalsDict = dict()

        # Foreach message, create a row in the given sheet, foreach signal in the message, create a row, hide the signal rows, create a button that hides or unhides.
        rowCount = 0
        lastRowCount = 0
        for message in dbcContent.messages:
            self.sheet.insert_row([message.name])
            messageSignalSet = set()
            for signal in message.signals:
                rowCount+=1
                # Create Signal
                self.create_signal(rowCount, signal)
                messageSignalSet.add(rowCount)
            self.sheet.create_index_checkbox(r = lastRowCount, check_function=lambda x, y=messageSignalSet:self.collapse(x, y), checked=True)
            rowCount+=1
            lastRowCount = rowCount

        # Create a list of the sheetrows after the dbc has been loaded.
        self.sheetRows = [*range(self.sheet.MT.total_data_rows())]

    def collapse(self, box, rows):
        if(not box[3]):
            # Subtract the rows from the total set of rows.
            self.sheetRows = [row for row in self.sheetRows if row not in rows]
            self.sheet.display_rows(rows=self.sheetRows, all_rows_displayed=False)
        else:
            # Add the rows to the currently displayed rows.
            self.sheetRows.extend(rows)
            self.sheet.display_rows(rows=self.sheetRows, all_rows_displayed=False)

    def create_signal(self, rowCount, signal):
        self.sheet.insert_row(['', signal.name, '', signal.unit, ''])
        self.activeSignalsDict[signal.name] = (rowCount, "", 0)
