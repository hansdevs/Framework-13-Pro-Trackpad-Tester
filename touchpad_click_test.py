# Python 3.14.10
import csv
import fcntl
import os
import re
import struct
import sys
import time
from datetime import datetime

EV_KEY, EV_ABS = 0x01, 0x03
BTN_LEFT = 0x110
ABS_MT_SLOT, ABS_MT_X, ABS_MT_Y, ABS_MT_ID = 0x2F, 0x35, 0x36, 0x39
EVENT = struct.Struct("llHHi")


def find_touchpad():
    with open("/proc/bus/input/devices") as f:
        for block in f.read().split("\n\n"):
            if "Touchpad" in block:
                return "/dev/input/" + re.search(r"event\d+", block).group()


def axis_range(fd, axis):
    buf = bytearray(24)
    fcntl.ioctl(fd, (2 << 30) | (24 << 16) | (ord("E") << 8) | (0x40 + axis), buf)
    return struct.unpack("6i", buf)[1:3]


def zone(x, y):
    row = "top" if y < 33.3 else "middle" if y < 66.7 else "bottom"
    col = "left" if x < 33.3 else "center" if x < 66.7 else "right"
    return f"{row} {col}"


def main():
    if os.geteuid() != 0:
        sys.exit("Run with sudo")

    fd = os.open(find_touchpad(), os.O_RDONLY)
    x_min, x_max = axis_range(fd, ABS_MT_X)
    y_min, y_max = axis_range(fd, ABS_MT_Y)
    folder = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(folder, datetime.now().strftime("touchpad_clicks_%Y%m%d_%H%M%S.csv"))

    slot, fingers, pressed, count = 0, {}, None, 0

    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["click", "time", "zone", "x_pct", "y_pct", "duration_ms"])
        print(f"Logging to {filename}, Ctrl+C to stop")

        try:
            while True:
                _, _, ev_type, code, value = EVENT.unpack(os.read(fd, EVENT.size))

                if ev_type == EV_ABS:
                    if code == ABS_MT_SLOT:
                        slot = value
                    elif code == ABS_MT_ID and value == -1:
                        fingers.pop(slot, None)
                    elif code == ABS_MT_X:
                        fingers.setdefault(slot, [0, 0])[0] = value
                    elif code == ABS_MT_Y:
                        fingers.setdefault(slot, [0, 0])[1] = value

                elif ev_type == EV_KEY and code == BTN_LEFT:
                    if value == 1 and fingers:
                        x, y = next(iter(fingers.values()))
                        pressed = (time.monotonic(), x, y)
                    elif value == 0 and pressed:
                        start, x, y = pressed
                        x_pct = round(100 * (x - x_min) / (x_max - x_min), 1)
                        y_pct = round(100 * (y - y_min) / (y_max - y_min), 1)
                        duration = round(1000 * (time.monotonic() - start))
                        count += 1
                        row = [count, datetime.now().strftime("%H:%M:%S"), zone(x_pct, y_pct), x_pct, y_pct, duration]
                        writer.writerow(row)
                        f.flush()
                        print(*row, sep="\t")
                        pressed = None
        except KeyboardInterrupt:
            print(f"\n{count} clicks saved to {filename}")


if __name__ == "__main__":
    main()
