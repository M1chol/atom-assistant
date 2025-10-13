import serial
from serial.tools import list_ports

SERVO_VID = 4292
SERVO_PID = 60000

serialServo = None


def openSerial():
    global serialServo
    ports = list_ports.comports()
    for _port in ports:
        if _port.vid == SERVO_VID and _port.pid == SERVO_PID:
            serialServo = _port.device
    if not serialServo:
        return False, "Failed to find servo"
    try:
        serialServo = serial.Serial(
            serialServo, baudrate=115200, timeout=1, dsrdtr=False, rtscts=False
        )
    except:
        return False, "Failed to connect to port"
    return True, "Servo connected"


def set_angle(angle: int):
    if not serialServo:
        return False, "Servo is not connected"
    try:
        command = f"CMD{angle};{180 - angle}"
        serialServo.write(command.encode() + b"\n")
        return True, f"Set angle {angle}"
    except ValueError as e:
        return False, e
