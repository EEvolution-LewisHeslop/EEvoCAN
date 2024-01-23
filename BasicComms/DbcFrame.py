import customtkinter
from tksheet import Sheet
from tkinter import filedialog
import cantools
import os


# A frame containing a sheet that displays a loaded DBC file.
# By default looks for resources\\default.dbc
# but will later support loading user selected DBCs.
# Takes the current hwmanager
class DbcFrame(customtkinter.CTkFrame):
    network = None

    def __init__(self, master, network=None):
        super().__init__(master, )
        self.network = network
        self.configure(fg_color="darkslategray", corner_radius=6)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Create the section header.
        self.dbcLabel = customtkinter.CTkLabel(self, text="DBC / EDS View")
        self.dbcLabel.grid(row=0, column=0, padx=20, pady=10, sticky="w")

        # Create load dbc button
        self.loadDbcButton = customtkinter.CTkButton(
            self,
            text="Load DBC",
            command=lambda: self.load_dbc(self.sheet))
        self.loadDbcButton.grid(row=0, column=1, padx=20, pady=10)

        # Load default DBC
        self.load_dbc(
            filePath=os.path.join(os.getcwd(), "resources\\default.dbc"))

    # Using a given filepath or prompting the user to open a DBC file
    # and then parses the content of the DBC file, binding callbacks
    def load_dbc(self, filePath=None):
        # TODO: if a dbc is already in use
        # handle clearing of active dbc callbacks
        if (filePath is None):
            filePath = filedialog.askopenfilename()
        print(f"Loading DBC at filepath: {filePath}")

        # Check that a file was selected.
        if (filePath is None):
            return "Unable to open file."

        # load the contents of the file
        self.db = cantools.db.load_file(filePath)

        # Refresh the dbc sheet
        self.refresh_dbc_sheet()

    def refresh_dbc_sheet(self, redraw=True):
        # Create Sheet
        self.sheet = Sheet(self, theme="dark green")
        self.sheet.enable_bindings()
        self.sheet.grid(
            row=1,
            column=0,
            columnspan=2,
            sticky="nsew",
            padx=5,
            pady=(0, 5))
        self.sheet.headers(
            newheaders=["Message", "Signal", "Value", "Unit", "Ticks"])
        self.sheet.edit_bindings(False)

        # Check to see if network is assigned.
        if (self.network is None):
            print("DBC Frame's network is not yet assigned.")

        # Foreach message, create a row in the given sheet,
        # foreach signal in the message, create a row,
        # hide the signal rows,
        # create a button that hides or unhides.
        rowCount = 0
        lastRowCount = 0
        for message in self.db.messages:
            self.sheet.insert_row([message.name])
            messageSignalSet = set()
            for signal in message.signals:
                rowCount += 1
                # Create Signal
                self.sheet.insert_row(['', signal.name, '', signal.unit, ''])
                messageSignalSet.add(rowCount)
                # For the signal register a callback that
                # updates the value cell when a message is received.
                if (self.network is not None):
                    self.network.subscribe(
                        can_id=message.frame_id,
                        callback=lambda x, y, z, r=rowCount, s=signal:
                            self.dbc_callback(x, y, z, r, s))
            # Create a checkbox for the message row that
            # allows you to collapse the message row.
            self.sheet.create_index_checkbox(
                r=lastRowCount,
                check_function=lambda box, rows=messageSignalSet:
                    self.collapse(box, rows), checked=False)
            rowCount += 1
            lastRowCount = rowCount

        # Create a list of the sheetrows after the dbc has been loaded.
        self.sheetRows = [*range(self.sheet.MT.total_data_rows())]

        # Collapse all checkboxes.
        boxes = self.sheet.get_index_checkboxes().values()
        for box in boxes:
            box['check_function']([0, 0, 0, False])

    # Collapses or expands given rows based on its checked ("box[3]") status.
    def collapse(self, box, rows):
        if (not box[3]):
            # Subtract the rows from the total set of rows.
            self.sheetRows = [row for row in self.sheetRows if row not in rows]
            self.sheet.display_rows(
                rows=self.sheetRows,
                all_rows_displayed=False)
        else:
            # Add the rows to the currently displayed rows.
            self.sheetRows.extend(rows)
            self.sheet.display_rows(
                rows=self.sheetRows,
                all_rows_displayed=False)

    # When called, updates the values column at a given row
    # based on the value received for a given signal.
    def dbc_callback(
            self,
            can_id,
            data,
            timestamp,
            rowcount,
            signal: cantools.db.Signal):
        value = self.db.decode_message(can_id, data)[signal.name]
        self.sheet.set_cell_data(rowcount, 2, value=value, redraw=False)
        self.sheet.set_cell_data(rowcount, 4, value=timestamp, redraw=True)
