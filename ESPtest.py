import serial
import time

# Change this to your actual port (check with: ls /dev/tty* or Device Manager)
PORT = '/dev/ttyUSB1'   # Linux
# PORT = 'COM3'         # Windows

BAUD = 9600

ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(2)  # allow ESP32 to reset

print("Connected to ESP32")

def send_command(byte1, byte2):
    """
    Send exactly 2 bytes to ESP32
    """
    data = bytes([byte1, byte2])
    ser.write(data)
    print(f"Sent: {byte1:#04x}, {byte2:#04x}")

def build_actuator_byte(channel, direction, speed):
    """
    Build command byte based on your ACTUATOR_DECODE()

    channel: 0 = arm, 1 = bucket
    direction: 0 = reverse, 1 = forward
    speed: 0–63 (0 = brake)
    """
    byte = 0
    byte |= (channel & 0x01) << 7
    byte |= (direction & 0x01) << 6
    byte |= (speed & 0x3F)
    return byte

#def lift_up_dump():
#    print(f"running lift_up_dump")
#    b1 = build_actuator_byte(channel=1, direction=0, speed=30)
#    b2 = build_actuator_byte(channel=0, direction=0, speed=30)
#    send_command(b1, b2)
#    time.sleep(5)
#    print(f"done")

# Example usage
try:
#    lift_up_dump()
    while True:
        # move arm; direction 1 extends and direction 0 retracts
        b1 = build_actuator_byte(channel=0, direction=0, speed=30)
        
        # move bucket; direction 0 extends and direction 1 retracts
        b2 = build_actuator_byte(channel=1, direction=0, speed=0)

        send_command(b1, b2)

        time.sleep(12)

        # Stop both (brake)
        stoparm = build_actuator_byte(0, 0, 0)
        stopbucket = build_actuator_byte(1, 0, 0)
        send_command(stoparm, stopbucket)


        time.sleep(2)

except KeyboardInterrupt:
    stoparm = build_actuator_byte(0, 0, 0)
    stopbucket = build_actuator_byte(1, 0, 0)
    send_command(stoparm, stopbucket)
    print("Exiting...")
    ser.close()
