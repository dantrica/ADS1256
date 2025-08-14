"""
# Include the code lines below if you are running directly on Jupyter from your Raspberry Pi 
import sys
sys.path.append('address to ads1256.py and constants.py')
"""
import time
import matplotlib.pyplot as plt
import pandas as pd
from ads1256 import ADS1256
from constants import ADS1256Constants as ADSC
import RPi.GPIO as GPIO

# ---------------------------- Configuration ----------------------------

# Initialize ADS1256 instance with custom SPI and GPIO settings
adc = ADS1256(
    spi_bus=0,
    spi_device=1,          # Using SPI0.1 to avoid conflict with manual CS
    spi_frequency=100000,  # Recommended 50 kHz SPI clock, others 10 kHz, 100 kHz, not recommended 500 kHz, 1000 kHz and the maximum 2 MHz.
    cs_pin=8,              # Chip select manually controlled on GPIO8
    data_ready_pin=22,     # DRDY pin on GPIO22
    v_ref=2.6518           # Reference voltage in volts
)

# Enable Buffer. True Recommended for signals with high impedance (Resistors, Sensors), on the contrary False for signals with low impedance (Power Supplies)
adc.enable_buffer(True)

# Set gain (amplification) and sample rate
adc.set_gain(1)  # Gain options: 1,2,4,8,16,32,64
adc.set_data_rate(ADSC.DRATE_1000)  # Choose sample rate (1000 SPS here)

# ----------------------- Single Channel Read Example -------------------

# Set input channel to AIN0 vs AINCOM
adc.set_input(ADSC.POS_AIN0, ADSC.NEG_AINCOM)
#adc.set_input(ADSC.POS_AIN1, ADSC.NEG_AIN0)

# Read voltage from AIN0
voltage_ain0 = adc.read_voltage()
print(f"AIN0 Voltage: {voltage_ain0:.6f} V")
