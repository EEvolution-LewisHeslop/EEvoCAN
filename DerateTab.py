import customtkinter
from tksheet import Sheet
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

from Interpolation import Interpolation
from ResizeHandler import ResizeHandler

# Creates the derate subtabs
class DerateTab(customtkinter.CTkFrame):
    canvasWidget = None
    def __init__(self, master, values, charge=False):
        super().__init__(master)

        # Configure layout.
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        
        # Create update axis button.
        self.updateAxisButton = customtkinter.CTkButton(self, text="Update Axis / Clear", command=lambda:ResizeHandler.update_axis(charge))
        self.updateAxisButton.grid(row=0, column=0, sticky="w", padx=5, pady=5)

        # Create Sheet
        self.table = Sheet(self, theme="dark green", data = values)
        self.table.enable_bindings()
        self.table.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        # Create plot button.
        self.updateAxisButton = customtkinter.CTkButton(self, text="Plot Table", command=lambda:self.generate_plot())
        self.updateAxisButton.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        # Assign sheet to resize handler charge table
        ResizeHandler.setTableReference(self.table, charge)

        # Create interpolate button
        self.interpolateButton = customtkinter.CTkButton(self, text="Interpolate", command=lambda:self.interpolate_values(self.table))
        self.interpolateButton.grid(row=2, column=0, padx=5, pady=5)

        # Resize
        ResizeHandler.update_axis(charge)
        
        # Reset Values
        self.table.set_sheet_data(values)

        # Interpolate Values
        self.interpolate_values(self.table)

        # Plot Values
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.generate_plot()

        # Bind cleanup to the frame destroy
        self.bind("<Destroy>", self.cleanup_function)

    def cleanup_function(self, *args):
        # Clear the matplotlib plot
        if self.fig is not None:
            self.fig.clf()  # Clear the figure
            plt.close(self.fig)  # Close the figure to release resources
            self.fig = None

        # Destroy the Tkinter canvas widget if it exists
        if self.canvas_widget is not None:
            self.canvas_widget.destroy()
            self.canvas_widget = None

    def interpolate_values(self, table: Sheet):
        oldData = table.MT.data
        newData = Interpolation.ScatteredBicubicInterpolation(oldData, len(table.MT._headers), len(table.MT._row_index))
        table.set_sheet_data(newData)
        table.set_all_column_widths(30)
    
    def generate_plot(self):
        # Update plot data
        self.ax.clear()  # Clear existing plot data
        im = self.ax.imshow(self.table.get_sheet_data())

        # Show all ticks and label them with the respective list entries
        self.ax.tick_params()

        # Draw the new plot.
        self.canvas.draw()  # Update the canvas with the new plot
        self.canvas_widget.grid(row=1, column=1)  # Place the canvas widget if not already placed
