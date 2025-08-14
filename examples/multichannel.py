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

# ----------------------- Multi-Channel Acquisition ---------------------

# Configure acquisition parameters
channels = [0, 1, 2]  # Read AIN0, AIN1, AIN2
duration_sec = 5      # Total acquisition time in seconds
sampling_interval = 0.01  # 10 ms between reads (100 Hz)
num_samples = int(duration_sec / sampling_interval)

# Data storage
data = {ch: [] for ch in channels}
timestamps = []

print(f"Starting acquisition on channels {channels} for {duration_sec}s")
start_time = time.time()
for i in range(num_samples):
    t_now = time.time() - start_time
    timestamps.append(t_now)

    for ch in channels:
        # Set multiplexer to AINx vs AINCOM
        adc.set_input(getattr(ADSC, f"POS_AIN{ch}"), ADSC.NEG_AINCOM)
        voltage = adc.read_voltage()
        data[ch].append(voltage)

    # Wait for next sample time
    elapsed = time.time() - start_time - t_now
    time.sleep(max(0, sampling_interval - elapsed))

print("Acquisition complete.")

# ----------------------------- Plotting -------------------------------

plt.figure(figsize=(12, 6))
for ch in channels:
    plt.plot(timestamps, data[ch], label=f"AIN{ch}")

plt.xlabel("Time [s]")
plt.ylabel("Voltage [V]")
plt.title("ADS1256 Multi-Channel Voltage Acquisition")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# -------------------------- Notes -----------------------------
# - This code avoids real-time plotting to ensure maximum acquisition speed.
# - To perform real-time plotting, use matplotlib's FuncAnimation or a GUI framework,
#   but that reduces acquisition speed.
# - For higher sample rates, reduce SPI frequency cautiously and buffer reads.
# - All constants for channels, gain, and sample rate are from ADS1256Constants.

# Clean up SPI and GPIO resources
adc.spi.close()
GPIO.cleanup()
