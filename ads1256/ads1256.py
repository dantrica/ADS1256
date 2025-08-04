import spidev
import RPi.GPIO as GPIO

from ads1256.constants import ADS1256Constants as ADSC  # noqa: N817


class ADS1256:
    #def __init__(
    #    self,
    #    spi_bus: int = 0,
    #    spi_device: int = 0,
    #    spi_frequency: int = 976563,
    #    data_ready_pin: int = 22,
    #    sync_pin: int = 27,
    #):
    #    self._spi_bus = spi_bus
    #    self._spi_device = spi_device
    #    self._spi_frequency = spi_frequency
    #
    #    self._cs_pin = 8 # default or allow as parameter
    #    self._data_ready_pin = data_ready_pin
    #    self._sync_pin = sync_pin
    #
    #    self.data_ready_timeout = 2
    #    self.data_ready_polling_delay = 1e-6
    #    self._v_ref = 2.5
    #
    #    self._configure_spi()
    #    self._configure_gpio()
    #
    #    # Reset the chip to get into a known state.
    #    self.reset()
    #
    #    # Read the chip ID to verify if the SPI communcication is working and
    #    # check if the expected value is returned.
    #    self.check_chip_id()
    #
    #    self.set_gain(1)

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
    
    ###########################################################################
    #                             IO Configuration                            #
    ###########################################################################

    def _configure_spi(self) -> None:
        """Configures the SPI bus.

        Args:
            None
        Returns:
            None
        """
        self.spi = spidev.SpiDev()
        self.spi.open(self._spi_bus, self._spi_device)
        self.spi.max_speed_hz = self._spi_frequency
        # The ADS1256 uses SPI MODE 1 this means CPOL=0 and CPHA=1.
        self.spi.mode = 0b01

    def _configure_gpio(self):
        """Configures GPIO pins using RPi.GPIO"""
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._cs_pin, GPIO.OUT)
        GPIO.setup(self._data_ready_pin, GPIO.IN)
        GPIO.setup(self._sync_pin, GPIO.OUT)
        GPIO.output(self._cs_pin, GPIO.HIGH)
        GPIO.output(self._sync_pin, GPIO.HIGH)

    def enable_cs(self, state: bool) -> None:
        GPIO.output(self._cs_pin, GPIO.HIGH if state else GPIO.LOW)

    ###########################################################################
    #                               R/W Register                              #
    ###########################################################################

    def read_register(self, address: int) -> int:
        """Returns the data byte from the specified register.
        The address must be between `0x00` and `0x0A`.

        Args:
            address (int): The address of the register.

        Returns:
            int: The content of the read register.
        """
        if not (0x00 <= address <= 0x0A):
            raise ValueError('Register address must be between 0x00 and 0x0A')

        self.enable_cs(True)
        self.spi.writebytes([ADSC.CMD_RREG | address, 0x00])
        response = self.spi.readbytes(1)[0]
        self.enable_cs(False)

        return response

    def write_register(self, address: int, data: int) -> None:
        """Writes data byte to the specified register.
        The address must be between `0x00` and `0x0A`.

        Args:
            address (int): The address of the register.
            data (int): The data byte that will be written to the register.
        """
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
            print(
                f'\033[31mADS1256: Got the wrong chip ID. '
                f'Expected 3, got {chip_id} instead.\033[0m'
            )
            exit()

    def set_gain(self, gain):
        if gain not in (1, 2, 4, 8, 16, 32, 64):
            raise ValueError('Gain must be one of: 1, 2, 4, 8, 16, 32, 64')

        # Gets the gain represente from 0x00 to 0x06.
        gain_binary = int.bit_length(gain) - 1

        # Recalucates the voltage per digit based on the new gain.
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
        """Configures multiplexer to connect any pair of pins as a
        differential input to the ADC.
        The pin number should be taken from the constans available
        using the ADS1256Constants class.

        Available pins are:
        POS_AIN0        NEG_AIN0
        POS_AIN1        NEG_AIN1
        POS_AIN2        NEG_AIN2
        POS_AIN3        NEG_AIN3
        POS_AIN4        NEG_AIN4
        POS_AIN5        NEG_AIN5
        POS_AIN6        NEG_AIN6
        POS_AIN7        NEG_AIN7
        POS_AINCOM      NEG_AINCOM

        Args:
            input_1 (int): The first pin of the differential pair.
            input_2 (int): The second pin of the differential pair.
        """
        self.write_register(ADSC.REG_MUX, input_1 | input_2)

    ############################################################################
    #                              Readging Values                             #
    ############################################################################

    def read_value(self) -> int:
        """Reads the next available ADC result. The multiplexer needs to be
        configured beforehand using set_input().

        For the default, free-running mode of the ADC, this means invalid data
        is returned when not synchronising acquisition and input channel
        configuration changes.

        To avoid this, after changing input channel configuration or with an
        external hardware multiplexer, use the sync() method to restart the
        conversion cycle before calling read_value().

        Args:
            None

        Returns:
            int: The raw ADC value.
        """

        self.wait_for_data_ready_low()
        self.enable_cs(True)
        self.spi.writebytes([ADSC.CMD_RDATA])
        response = self.spi.readbytes(3)
        self.enable_cs(False)

        return int.from_bytes(response, 'big', signed=True)

    def read_voltage(self) -> float:
        """Reads the next available ADC value and converts it to a voltage.

        Args:
            None

        Returns:
            float: The voltage in Volts.
        """
        value = self.read_value()
        return value * self._volt_per_digit
