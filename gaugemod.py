import tkinter as tk
from engineering_notation import EngNumber
from math import pi, cos, sin


class Gauge(tk.Frame):
    """
    Shows a gauge, much like the RotaryGauge.::

        gauge = tk_tools.Gauge(root, max_value=100.0,
                               label='speed', unit='km/h')
        gauge.grid()
        gauge.set_value(10)

    :param parent: tkinter parent frame
    :param width: canvas width
    :param height: canvas height
    :param min_value: the minimum value
    :param max_value: the maximum value
    :param label: the label on the scale
    :param unit: the unit to show on the scale
    :param divisions: the number of divisions on the scale
    :param yellow: the beginning of the yellow (warning) zone in percent
    :param red: the beginning of the red (danger) zone in percent
    :param yellow_low: in percent warning for low values
    :param red_low: in percent if very low values are a danger
    :param bg: background
    """

    def __init__(
        self,
        parent,
        width: int = 200,
        height: int = 100,
        min_value=0.0,
        max_value=100.0,
        label="",
        unit="",
        divisions=8,
        yellow=50,
        red=80,
        yellow_low=0,
        red_low=0,
        bg="lightgrey",
    ):
        self._parent = parent
        self._width = width
        self._height = height
        self._label = label
        self._unit = unit
        self._divisions = divisions
        self._min_value = EngNumber(min_value)
        self._max_value = EngNumber(max_value)
        self._average_value = EngNumber((max_value + min_value) / 2)
        self._yellow = yellow * 0.01
        self._red = red * 0.01
        self._yellow_low = yellow_low * 0.01
        self._red_low = red_low * 0.01

        super().__init__(self._parent)

        self._canvas = tk.Canvas(
            self,
            width=self._width,
            height=self._height,
            bg=bg)
        self._canvas.grid(row=0, column=0, sticky="news")
        self._min_value = EngNumber(min_value)
        self._max_value = EngNumber(max_value)
        self._start = 150.0
        self._max_angle = 120.0
        self._rot_offset = (180.0 - self._start)/180.0
        self._rot_factor = (0.5 - self._rot_offset)/0.5
        self._value = self._min_value
        self.draw_once()

    def draw_once(self):
        # Create the tick marks and colors across the top.
        for i in range(self._divisions):
            extent = self._max_angle / self._divisions
            start = self._start - i * extent
            rate = (i + 1) / (self._divisions + 1)
            if rate < self._red_low:
                bg_color = "red"
            elif rate <= self._yellow_low:
                bg_color = "yellow"
            elif rate <= self._yellow:
                bg_color = "green"
            elif rate <= self._red:
                bg_color = "yellow"
            else:
                bg_color = "red"

            self._canvas.create_arc(
                0,
                int(self._height * 0.15),
                self._width,
                int(self._height * 1.8),
                start=start,
                extent=-extent,
                width=2,
                fill=bg_color,
                style="pie",
            )
        bg_color = "white"
        ratio = 0.06
        self._canvas.create_arc(
            self._width * ratio,
            int(self._height * 0.25),
            self._width * (1.0 - ratio),
            int(self._height * 1.8 * (1.0 - ratio * 1.1)),
            start=self._start,
            extent=-120,
            width=2,
            fill=bg_color,
            style="pie",
        )

        # Display lowest value.
        value_text = "{}".format(self._min_value)
        self._canvas.create_text(
            self._width * 0.1,
            self._height * 0.7,
            font=("Courier New", int(self._height/10)),
            text=value_text,
        )
        # Display greatest value.
        value_text = "{}".format(self._max_value)
        self._canvas.create_text(
            self._width * 0.9,
            self._height * 0.7,
            font=("Courier New", int(self._height/10)),
            text=value_text,
        )
        # Display center value.
        value_text = "{}".format(self._average_value)
        self._canvas.create_text(
            self._width * 0.5,
            self._height * 0.1,
            font=("Courier New", int(self._height/10)),
            text=value_text,
        )

    # Creates or updates the readout, with bg as bg colour.
    def readout(self, bg):
        # Update the value text.
        value_text = "{}{}".format(self._value, self._unit)

        # See if the readout already exists, this prevents flickering.
        if (len(self._canvas.find_withtag('readout')) < 1):
            # Create the rectangle behind the readout.
            r_width = (self._width - 10)/2
            r_height = (self._height)/5
            r_offset = (self._height)*0.08
            self.readoutRect = self._canvas.create_rectangle(
                self._width / 2.0 - r_width / 2.0,
                self._height / 2.0 - r_height / 2.0 + r_offset,
                self._width / 2.0 + r_width / 2.0,
                self._height / 2.0 + r_height / 2.0 + r_offset,
                fill=bg,
                outline="grey",
                tags='readout'
            )
            # Create digital readout label.
            self._canvas.create_text(
                self._width * 0.5,
                self._height * 0.5 - r_offset,
                font=("Courier New", int(self._height/10)),
                text=self._label,
                tags='readout'
            )
            # Create the digital readout value.
            self.readoutText = self._canvas.create_text(
                self._width * 0.5,
                self._height * 0.5 + r_offset,
                font=("Courier New", int(self._height/10)),
                text=value_text,
                fill="white",
                tags=['readout', 'text']
            )
        else:
            # Update the readoutText and bg color.
            self._canvas.itemconfigure(self.readoutText, text=value_text)
            self._canvas.itemconfigure(self.readoutRect, fill=bg)

    # Creates or refreshes needle based on current value.
    def needle(self):
        # Calculate the new needle value as a percentage.
        value_as_percent = (self._value - self._min_value) / (
            self._max_value - self._min_value
        )
        if value_as_percent > 1:
            value_as_percent = 1

        # See if the needle already exists, this prevents flickering.
        if (len(self._canvas.find_withtag('needle')) < 1):
            # Create the needle.
            self._canvas.create_line(
                self._width/2,
                int(self._height * 0.97),
                self._width/2,
                int(self._height * 0.15),
                fill='red',
                width=(self._height/100)*3,
                arrow='last',
                tags='needle')

        # Update needle position with respect to value as percent.
        angle = (value_as_percent * self._rot_factor + self._rot_offset)
        x = (self._width/2) - ((self._width/2)) * cos(angle * pi)
        y = (self._height) - (self._height*0.86) * sin(angle * pi)
        self._canvas.coords('needle', self._width/2, self._height * 0.97, x, y)

    # Sets the _value to the given EngNumber conversion of given value.
    # Creates or updates the readout and needle correspondingly.
    def set_value(self, value):
        self._value = EngNumber(value)
        # Check for value out of range and colour readout accordingly.
        if self._min_value * 1.02 < value < self._max_value * 0.98:
            self.readout("black")
        else:
            self.readout("red")
        self.needle()
        self._canvas.tag_raise('needle', 'readout')
