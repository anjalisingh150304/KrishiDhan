#!/usr/bin/env python3
# 7-in-1 NPK Sensor reader (Modbus RTU) via USB serial on Raspberry Pi
# Author: Rohit Kadam, www.robosap.in
# Notes:
# - Default serial port: /dev/ttyUSB0 (change below if needed)
# - Baud: 4800

import time
import serial

SERIAL_PORT = "/dev/ttyUSB0"  # e.g., /dev/ttyUSB0, /dev/ttyUSB1, /dev/ttyAMA0
BAUD = 4800
TIMEOUT = 0.3  # seconds
POLL_MS = 5000

SLAVE_ADDR = 0x01
START_REG = 0x0000
REG_COUNT = 0x0007  # 7 registers → 14 data bytes

# Scaling (adjust if your probe differs)
MOIST_SCALE = 0.1
TEMP_SCALE = 0.1
PH_SCALE = 0.1
EC_SCALE = 1.0  # some probes use 0.1 or 10.0

RESP_LEN = 19  # [addr][func][byteCount=14][14 data][CRCLo][CRCHi]


def crc16_modbus(data: bytes) -> int:
    crc = 0xFFFF
    for b in data:
        crc ^= b
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc & 0xFFFF


def build_request(slave: int, start_reg: int, reg_count: int) -> bytes:
    frame = bytearray(8)
    frame[0] = slave
    frame[1] = 0x03  # Read Holding Registers
    frame[2] = (start_reg >> 8) & 0xFF
    frame[3] = start_reg & 0xFF
    frame[4] = (reg_count >> 8) & 0xFF
    frame[5] = reg_count & 0xFF
    crc = crc16_modbus(frame[:6])
    frame[6] = crc & 0xFF  # CRC Lo
    frame[7] = (crc >> 8) & 0xFF  # CRC Hi
    return bytes(frame)


def read_exact(ser: serial.Serial, n: int, timeout_s: float) -> bytes:
    """Read exactly n bytes or return b'' on timeout."""
    deadline = time.time() + timeout_s
    out = bytearray()
    while len(out) < n and time.time() < deadline:
        chunk = ser.read(n - len(out))
        if chunk:
            out.extend(chunk)
        else:
            time.sleep(0.001)
    return bytes(out) if len(out) == n else b""


def parse_payload(resp: bytes):
    if len(resp) != RESP_LEN:
        raise ValueError("Bad length")

    if resp[2] != 14:
        raise ValueError("Bad byteCount")

    rx_crc = (resp[18] << 8) | resp[17]
    calc_crc = crc16_modbus(resp[:-2])
    if rx_crc != calc_crc:
        raise ValueError("CRC mismatch")

    if resp[0] != SLAVE_ADDR or resp[1] != 0x03:
        raise ValueError("Bad addr/func")

    d = resp[3:17]
    regs = []
    for i in range(0, 14, 2):
        regs.append((d[i] << 8) | d[i + 1])

    soilHumidity = regs[0] * MOIST_SCALE
    soilTempC = regs[1] * TEMP_SCALE
    soilEC = regs[2] * EC_SCALE
    soilPH = regs[3] * PH_SCALE
    N, P, K = regs[4], regs[5], regs[6]

    return {
        "moisture_pct": soilHumidity,
        "temperature_c": soilTempC,
        "ec_uScm": soilEC,
        "ph": soilPH,
        "nitrogen_mgkg": N,
        "phosphorus_mgkg": P,
        "potassium_mgkg": K,
    }


def read_once(ser: serial.Serial, retries: int = 3):
    req = build_request(SLAVE_ADDR, START_REG, REG_COUNT)

    for attempt in range(1, retries + 1):
        ser.reset_input_buffer()
        ser.write(req)
        resp = read_exact(ser, RESP_LEN, TIMEOUT)
        if not resp:
            if attempt == retries:
                raise TimeoutError("No/short response from sensor")
            continue

        try:
            return parse_payload(resp)
        except Exception:
            if attempt == retries:
                raise
            time.sleep(0.05)
    raise RuntimeError("Unexpected read error")


def main():
    print("Soil NPK Sensor - USB Serial Reader (Modbus RTU)")
    print(f"Port={SERIAL_PORT}, {BAUD} 8N1, slave=0x{SLAVE_ADDR:02X}")

    while True:
        try:
            with serial.Serial(
                SERIAL_PORT,
                BAUD,
                timeout=0,
                bytesize=8,
                parity=serial.PARITY_NONE,
                stopbits=1,
            ) as ser:
                while True:
                    try:
                        reading = read_once(ser, retries=3)
                        print("---- Soil Sensor Readings ----")
                        print(f"Moisture: {reading['moisture_pct']:.1f} %")
                        print(f"Temperature: {reading['temperature_c']:.1f} °C")
                        print(f"Conductivity: {reading['ec_uScm']:.1f} uS/cm")
                        print(f"pH: {reading['ph']:.1f}")
                        print(
                            f"N: {reading['nitrogen_mgkg']}  P: {reading['phosphorus_mgkg']}  K: {reading['potassium_mgkg']} (mg/kg)"
                        )
                        print("--------------------------------\n")
                    except Exception as e:
                        print(f"[WARN] Read failed: {e}")
                    time.sleep(POLL_MS / 1000.0)

        except serial.SerialException as e:
            print(f"[ERROR] Serial open failed on {SERIAL_PORT}: {e}")
            print("Retrying in 3s...")
            time.sleep(3)


if __name__ == "__main__":
    main()
