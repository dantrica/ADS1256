import spidev
import RPi.GPIO as GPIO
import time
from ads1256.constants import ADS1256Constants as ADSC  # noqa: N817

class ADS1256:
    def __init__(
        self,
        spi_bus=0,
        spi_device=0,
        spi_frequency=976563,
        data_ready_pin=22,
        sync_pin=27,
        cs_pin=8,
        v_ref=2.5
    ):
        self._spi_bus = spi_bus
        self._spi_device = spi_device
        self._spi_frequency = spi_frequency

        self._data_ready_pin = data_ready_pin
        self._sync_pin = sync_pin
        self._cs_pin = cs_pin
        self._v_ref = v_ref

        self.data_ready_timeout = 2
        self.data_ready_polling_delay = 1e-6

        self._configure_spi()
        self._configure_gpio()

        self.reset()
        self.check_chip_id()
        self.set_gain(1)

    ###########################################################################
    #                             IO Configuration                            #
    ###########################################################################

    def _configure_spi(self) -> None:
        """Configures the SPI bus."""
        self.spi = spidev.SpiDev()
        self.spi.open(self._spi_bus, self._spi_device)
        self.spi.max_speed_hz = self._spi_frequency
        self.spi.mode = 0b01  # SPI MODE 1: CPOL=0, CPHA=1

    def _configure_gpio(self):
        """Configures GPIO pins using RPi.GPIO"""
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._cs_pin, GPIO.OUT)
        GPIO.setup(self._data_ready_pin, GPIO.IN)
        GPIO.setup(self._sync_pin, GPIO.OUT)
        GPIO.output(self._cs_pin, GPIO.HIGH)
        GPIO.output(self._sync_pin, GPIO.HIGH)

    def enable_cs(self, state: bool) -> None:
        GPIO.output(self._cs_pin, GPIO.LOW if state else GPIO.HIGH)

    ###########################################################################
    #                               R/W Register                              #
    ###########################################################################

    def read_register(self, address: int) -> int:
        if not (0x00 <= address <= 0x0A):
            raise ValueError('Register address must be between 0x00 and 0x0A')

        self.enable_cs(True)
        self.spi.writebytes([ADSC.CMD_RREG | address, 0x00])
        response = self.spi.readbytes(1)[0]
        self.enable_cs(False)

        return response

    def write_register(self, address: int, data: int) -> None:
        if not (0x00 <= address <= 0x0A):
            raise ValueError('Register address must be between 0x00 and 0x0A')

        self.enable_cs(True)
        self.spi.writebytes([ADSC.CMD_WREG | address, 0x00, data])
        self.enable_cs(False)

    def wait_for_data_ready_low(self):
        timeout = time.time() + self.data_ready_timeout
        while GPIO.input(self._data_ready_pin):
            if time.time() > timeout:
                raise TimeoutError("DRDY timeout.")
            time.sleep(self.data_ready_polling_delay)

    ###########################################################################
    #                                 Control                                 #
    ###########################################################################

    def reset(self):
        self.enable_cs(True)
        self.spi.writebytes([ADSC.CMD_RESET])
        self.enable_cs(False)
        self.wait_for_data_ready_low()

    def read_chip_id(self):
        return self.read_register(ADSC.REG_STATUS) >> 4

    def check_chip_id(self):
        chip_id = self.read_chip_id()
        if chip_id != 3:
            raise RuntimeError(
                f"ADS1256: Incorrect chip ID. Expected 3, got {chip_id}")

    def set_gain(self, gain):
        gain_map = {1: 0x00, 2: 0x01, 4: 0x02, 8: 0x03,
                    16: 0x04, 32: 0x05, 64: 0x06}
        if gain not in gain_map:
            raise ValueError('Gain must be one of: 1, 2, 4, 8, 16, 32, 64')

        gain_binary = gain_map[gain]
        self._volt_per_digit = self._v_ref * 2.0 / (gain * (2**23 - 1))
        self.write_register(ADSC.REG_ADCON, gain_binary)

    def volt_per_digit(self):
        return self._volt_per_digit

    def self_calibration(self):
        self.enable_cs(True)
        self.spi.writebytes([ADSC.CMD_SELFCAL])
        self.enable_cs(False)
        self.wait_for_data_ready_low()

    def set_data_rate(self, data_rate):
        self.write_register(ADSC.REG_DRATE, data_rate)

    def sync(self):
        GPIO.output(self._sync_pin, GPIO.LOW)
        time.sleep(1e-5)
        GPIO.output(self._sync_pin, GPIO.HIGH)

    def set_input(self, input_1: int, input_2: int) -> None:
        self.write_register(ADSC.REG_MUX, input_1 | input_2)

    ###########################################################################
    #                              Reading Values                             #
    ###########################################################################

    def read_value(self) -> int:
        self.wait_for_data_ready_low()
        self.enable_cs(True)
        self.spi.writebytes([ADSC.CMD_RDATA])
        response = self.spi.readbytes(3)
        self.enable_cs(False)

        return int.from_bytes(response, 'big', signed=True)

    def read_voltage(self) -> float:
        value = self.read_value()
        return value * self._volt_per_digit
