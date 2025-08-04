# ADS1256

A python library to communicate with the ADS1256 analog to digital converter from Texas Instruments.

__init__: Sets up SPI interface with ADS1256, SPI mode and speed. Defines command and register constants. Calls init_adc() to initialize the chip.

send_command(cmd): Sends a single-byte SPI command to ADS1256.

write_register(reg, value): Writes a byte value to a register reg using SPI commands.

read_register(reg): Reads a byte from register reg.

init_adc(): Initializes the ADC chip by waking it up, configuring status and ADCON registers, setting default data rate (1000 SPS), and running self-calibration.

set_data_rate(rate): Changes sample rate of ADC to one of predefined supported rates.

set_channel(channel): Selects the input channel (0-7) on the multiplexer, always using AINCOM as negative input (single-ended input).

read_adc(): Requests a reading from the ADC, reads 3 bytes, converts it from 24-bit two’s complement to signed integer.

read_channel(channel): Sets the channel and returns a single ADC reading from it.

read_multiple_channels(channels): Reads a list of channels sequentially, returns a dictionary mapping channel to value.

close(): Closes SPI connection cleanly.
