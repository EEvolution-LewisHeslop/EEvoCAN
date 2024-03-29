import math
import customtkinter
from tksheet import Sheet
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

from ConfigurationWizard.Interpolation import Interpolation
from ConfigurationWizard.ResizeHandler import ResizeHandler


# Creates the derate subtabs
class DerateTab(customtkinter.CTkFrame):
    canvasWidget = None

    def __init__(self, master, values, charge=False):
        super().__init__(master)

        # Configure layout.
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(2, weight=1)

        # Create update axis button.
        self.updateAxisButton = customtkinter.CTkButton(
            self,
            text="Update Axis / Clear",
            command=lambda: ResizeHandler.update_axis(charge))
        self.updateAxisButton.grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="w",
            padx=5,
            pady=5)

        # Create sheet X-Label
        self.xlabel = customtkinter.CTkLabel(self, text="Temperature (degC)")
        self.xlabel.grid(row=1, column=1, sticky="n")

        # Create Sheet
        self.table = Sheet(
            self,
            theme="dark green",
            data=values,
            table_bg="#2b2b2b",
            index_bg="#2b2b2b",
            header_bg="#2b2b2b",
            top_left_bg="#2b2b2b",
            show_x_scrollbar=True,
            show_y_scrollbar=True)
        self.table.enable_bindings()
        self.table.grid(row=2, column=1, sticky="nsew", padx=5, pady=5)
        startEditBinding = ("begin_edit_cell", self.begin_edit_cell)
        endEditBinding = ("end_edit_cell", self.end_edit_cell)
        self.table.extra_bindings([startEditBinding, endEditBinding])

        # Create sheet Y-Label
        self.ylabel = customtkinter.CTkLabel(self, text="SoC (%)")
        self.ylabel.grid(row=2, column=0, sticky="w")

        # Create plot button.
        self.updateAxisButton = customtkinter.CTkButton(
            self,
            text="Plot Table",
            command=lambda: self.generate_plot())
        self.updateAxisButton.grid(row=0, column=2, sticky="w", padx=5, pady=5)

        # Assign sheet to resize handler charge table
        ResizeHandler.setTableReference(self.table, charge)

        # Create interpolate button
        self.interpolateButton = customtkinter.CTkButton(
            self, text="Interpolate",
            command=lambda: self.interpolate_values(self.table))
        self.interpolateButton.grid(
            row=0,
            column=0,
            columnspan=2,
            padx=5,
            pady=5,
            sticky="e")

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
        newData = Interpolation.ScatteredBicubicInterpolation(
            oldData,
            len(table.MT._headers),
            len(table.MT._row_index))
        table.set_sheet_data(newData)
        table.set_all_cell_sizes_to_text(redraw=True)

    def generate_plot(self):
        # Update plot data
        if (hasattr(self, "cbar")):
            self.cbar.remove()
        self.ax.clear()  # Clear existing plot data

        # Set title and axes labels
        self.ax.set_title(
            "Current(z) by Temperature(x) and SoC(y)",
            color='white')
        self.ax.set_xlabel("Temperature (degC)")
        self.ax.set_ylabel("SoC (%)")

        # Populate data
        im = self.ax.imshow(self.table.get_sheet_data())

        # Create the colourbar for the current plot
        self.cbar = self.ax.figure.colorbar(im, ax=self.ax)
        self.cbar.ax.set_ylabel(
            "Current (A)",
            rotation=-90,
            va="bottom",
            color="white")

        # Determine the interval for ticks (for example, every 5th label)
        headerLength = len(self.table.MT._headers)
        rowIndexLength = len(self.table.MT._row_index)
        tickMax = max(headerLength, rowIndexLength)
        x_tick_interval = calculate_tick_interval(tickMax)
        y_tick_interval = calculate_tick_interval(tickMax)

        # Apply intervals to set_xticks and set_yticks
        self.ax.set_xticks(
            range(0, len(self.table.MT._headers), x_tick_interval),
            labels=self.table.MT._headers[::x_tick_interval])
        self.ax.set_yticks(
            range(0, len(self.table.MT._row_index), y_tick_interval),
            labels=self.table.MT._row_index[::y_tick_interval])

        # Colour the figure.
        self.ax.figure.set_facecolor("#2b2b2b")
        self.ax.spines['bottom'].set_color('white')
        self.ax.spines['top'].set_color('white')
        self.ax.spines['left'].set_color('white')
        self.ax.spines['right'].set_color('white')
        self.ax.xaxis.label.set_color('white')
        self.ax.yaxis.label.set_color('white')
        self.ax.title.set_color('white')
        self.ax.tick_params(axis='x', colors='white')
        self.ax.tick_params(axis='y', colors='white')

        # Colour the colourbar
        self.cbar.ax.yaxis.set_tick_params(color='white')
        self.cbar.outline.set_edgecolor('white')
        plt.setp(plt.getp(self.cbar.ax.axes, 'yticklabels'), color='white')

        # Update the canvas with the new plot
        self.canvas.draw()
        # Place the canvas widget if not already placed
        self.canvas_widget.grid(row=2, column=2, sticky="nsew")

    def begin_edit_cell(self, event=None):
        return event.text

    def end_edit_cell(self, event=None):
        # Validate user input.
        if event.text is None:
            return
        trimmed = event.text.replace(" ", "")
        try:
            trimmed = float(trimmed)
            return float("{:.3f}".format(trimmed))
        except ValueError:
            print("Sheet input was non-numeric.")


def calculate_tick_interval(count):
    # Use a logarithmic scale to determine the tick interval
    return max(1, int(pow(10, math.log10(count) - 1)))
