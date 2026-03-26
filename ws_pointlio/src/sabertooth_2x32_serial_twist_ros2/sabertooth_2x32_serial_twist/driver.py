import threading
from dataclasses import dataclass
from typing import Literal

import serial


Protocol = Literal['packet', 'plain_text']


@dataclass
class SabertoothConfig:
    port: str = '/dev/ttyUSB0'
    baudrate: int = 9600
    address: int = 128
    protocol: Protocol = 'packet'
    timeout_sec: float = 0.1
    motor_1_reversed: bool = False
    motor_2_reversed: bool = False


class SabertoothSerialDriver:
    """Small Sabertooth 2x32 serial driver.

    Supports:
      - packet serial with 7-bit checksum
      - plain text serial (ASCII commands like 'M1:500\n')
    """

    def __init__(self, config: SabertoothConfig):
        self._cfg = config
        self._serial = serial.Serial(
            port=config.port,
            baudrate=config.baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=config.timeout_sec,
            write_timeout=config.timeout_sec,
        )
        self._lock = threading.Lock()

    def close(self) -> None:
        if self._serial.is_open:
            self._serial.close()

    def stop(self) -> None:
        self.set_motor_power(0.0, 0.0)

    def set_motor_power(self, left: float, right: float) -> None:
        left = self._apply_reverse(left, self._cfg.motor_1_reversed)
        right = self._apply_reverse(right, self._cfg.motor_2_reversed)

        if self._cfg.protocol == 'packet':
            self._write_packet_motor(1, left)
            self._write_packet_motor(2, right)
        elif self._cfg.protocol == 'plain_text':
            self._write_plain_text_motor(1, left)
            self._write_plain_text_motor(2, right)
        else:
            raise ValueError(f'Unsupported protocol: {self._cfg.protocol}')

    def _apply_reverse(self, value: float, reverse: bool) -> float:
        value = max(-1.0, min(1.0, value))
        return -value if reverse else value

    def _write_packet_motor(self, motor_index: int, normalized: float) -> None:
        magnitude = int(round(abs(max(-1.0, min(1.0, normalized))) * 127.0))
        if motor_index == 1:
            command = 0 if normalized >= 0.0 else 1
        elif motor_index == 2:
            command = 4 if normalized >= 0.0 else 5
        else:
            raise ValueError('motor_index must be 1 or 2')

        packet = bytes([
            self._cfg.address,
            command,
            magnitude,
            (self._cfg.address + command + magnitude) & 0x7F,
        ])
        with self._lock:
            self._serial.write(packet)
            self._serial.flush()

    def _write_plain_text_motor(self, motor_index: int, normalized: float) -> None:
        value = int(round(max(-1.0, min(1.0, normalized)) * 2047.0))
        line = f'M{motor_index}:{value}\n'.encode('ascii')
        with self._lock:
            self._serial.write(line)
            self._serial.flush()
