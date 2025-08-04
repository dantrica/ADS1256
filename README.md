# ADS1256

A python library to communicate with the ADS1256 analog to digital converter from Texas Instruments.

Initialization: Create the ADS1256 instance with SPI bus/device, frequency, GPIO pins for CS, DRDY, and SYNC, and reference voltage.

_configure_spi() and _configure_gpio(): Set up SPI interface and GPIO pins for communication and control signals.

reset(): Resets the ADS1256 to a known default state.

check_chip_id(): Verifies the chip ID to confirm communication is correct.

set_gain(1): Sets the programmable gain amplifier to unity gain.

self_calibration(): Performs internal self-calibration for more accurate readings.

set_data_rate(): Sets the sampling rate; choose from constants (e.g., ADSC.DRATE_1000_SPS).

set_input(): Configures the multiplexer for input channels. Here, single-ended mode uses POS_AINx with NEG_AINCOM.

sync(): Synchronizes conversions after changing inputs to get valid data.

read_value(): Reads the raw 24-bit signed ADC value.

read_voltage(): Converts raw ADC value into voltage based on gain and reference voltage.
