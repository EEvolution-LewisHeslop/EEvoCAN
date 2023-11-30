import customtkinter
import canopen
import tk_tools
import cantools


class GaugeFrame(customtkinter.CTkFrame):
    def __init__(
            self,
            master,
            network: canopen.Network = None,
            db: cantools.db.Database = None):
        super().__init__(master)
        self.configure(fg_color="darkslategray", corner_radius=6)
        self.network = network
        self.db = db
        # Set the weights
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Create the section header
        self.gaugesLabel = customtkinter.CTkLabel(self, text="Gauges Frame")
        self.gaugesLabel.grid(
            row=0,
            column=0,
            columnspan=3,
            padx=20,
            pady=10,
            sticky="w")

        # Create Battery Temp Gauge
        self.gauge1 = tk_tools.Gauge(
            self,
            min_value=-30,
            max_value=85.0,
            label='Bat Temp',
            unit='°C',
            bg="darkslategray")
        self.gauge1.grid(row=1, column=0, padx=5, pady=5)
        self.gauge1.set_value(25)
        self.gauge1._canvas.configure(
            bg="darkslategray",
            highlightthickness=0)

        # Create Battery Current Gauge
        self.gauge2 = tk_tools.Gauge(
            self,
            max_value=100.0,
            label='Bat Current',
            unit='A',
            bg="darkslategray")
        self.gauge2.grid(row=1, column=1, padx=5, pady=5)
        self.gauge2.set_value(50)
        self.gauge2._canvas.configure(bg="darkslategray", highlightthickness=0)

        # Create Battery SoC Gauge
        self.gauge3 = tk_tools.Gauge(
            self,
            max_value=100.0,
            label='SoC',
            unit='%',
            bg="darkslategray")
        self.gauge3.grid(row=1, column=2, padx=5, pady=5)
        self.gauge3.set_value(75)
        self.gauge3._canvas.configure(
            bg="darkslategray",
            highlightthickness=0)

        # Register Callback for Temperature Gauge
        message = db.get_message_by_name('DashInfo')
        signal = message.get_signal_by_name('BatteryTemperature')
        self.network.subscribe(
            can_id=message.frame_id,
            callback=lambda x, y, z, s=signal, g=self.gauge1:
                self.gauge_callback(x, y, z, s, g))

        # Register Callback for the Current Gauge
        signal = message.get_signal_by_name('Current')
        self.network.subscribe(
            can_id=message.frame_id,
            callback=lambda x, y, z, s=signal, g=self.gauge2:
                self.gauge_callback(x, y, z, s, g))

        # Register Callback for the SoC Gauge
        signal = message.get_signal_by_name('StateOfCharge')
        self.network.subscribe(
            can_id=message.frame_id,
            callback=lambda x, y, z, s=signal, g=self.gauge3:
                self.gauge_callback(x, y, z, s, g))

        # Create the CreateGauge Button
        self.createGauge = customtkinter.CTkButton(self, text="Create Gauge")
        self.createGauge.grid(row=2, columnspan=3, padx=5, pady=5)

    def gauge_callback(
            self,
            can_id,
            data,
            timestamp,
            signal: cantools.db.Signal,
            gauge):
        value = self.db.decode_message(can_id, data)[signal.name]
        gauge.set_value(value)
