import time

# Try importing real sensor dependencies
try:
    import serial
    from utilities import npk7
except ImportError:
    serial = None
    npk7 = None


class SensorService:
    """
    Reads soil sensor data (NPK, moisture, temp, pH)
    using Modbus RTU via USB serial.
    Falls back to simulation if unavailable.
    """

    def __init__(self, simulate_on_fail=True):
        self.simulate_on_fail = simulate_on_fail

    # --------------------------------------------------
    # PUBLIC METHOD (used by controllers/services)
    # --------------------------------------------------
    def read_soil(self):
        """
        Returns normalized soil data:
        {
            N, P, K,
            temperature,
            humidity,
            ph,
            rainfall
        }
        """

        if serial and npk7:
            try:
                return self._read_from_sensor()
            except Exception as e:
                print("[SensorService] Sensor read failed:", e)

        if self.simulate_on_fail:
            return self._simulate_data()

        raise RuntimeError("Soil sensor unavailable")

    # --------------------------------------------------
    # REAL SENSOR READ (uses your npk7 code)
    # --------------------------------------------------
    def _read_from_sensor(self):
        with serial.Serial(
            port=npk7.SERIAL_PORT,
            baudrate=npk7.BAUD,
            timeout=npk7.TIMEOUT,
            bytesize=8,
            parity=serial.PARITY_NONE,
            stopbits=1,
        ) as ser:
            raw = npk7.read_once(ser, retries=3)

        # Inject rainfall (not provided by NPK sensor)
        raw["rainfall"] = 100.0

        return self._normalize(raw)

    # --------------------------------------------------
    # NORMALIZE RAW SENSOR OUTPUT
    # --------------------------------------------------
    def _normalize(self, raw):
        """
        Converts npk7 output to backend standard format
        """

        return {
            "N": float(raw["nitrogen_mgkg"]),
            "P": float(raw["phosphorus_mgkg"]),
            "K": float(raw["potassium_mgkg"]),
            "temperature": float(raw["temperature_c"]),
            "humidity": float(raw["moisture_pct"]),
            "ph": float(raw["ph"]),
            "rainfall": float(raw["rainfall"]),
        }

    # --------------------------------------------------
    # FALLBACK SIMULATION
    # --------------------------------------------------
    def _simulate_data(self):
        print("[SensorService] Using simulated soil data")

        return {
            "N": 40.0,
            "P": 35.0,
            "K": 30.0,
            "temperature": 25.0,
            "humidity": 55.0,
            "ph": 6.5,
            "rainfall": 100.0,
        }
