# ADS1256

A Python library to communicate with the ADS1256 (by Texas Instruments) and the Raspberry Pi 4 B.

Initialization: Create the ADS1256 instance with SPI bus/device, frequency, GPIO pins for CS, DRDY, and SYNC, and reference voltage.


Methods: 

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

Suggested PINs: 
ADS1256	pins to Raspberry Pi 4 B
CS	to GPIO8
DRDY to	GPIO22
MISO	to GPIO9
MOSI	to GPIO10
SCLK	to GPIO11
VCC	5V to (pin 2)
GND	to GND (pins 9, 25, 39, 6, 14, 20, 30, and 34)
