import logging

import serial
import time
import os
import pandas as pd


# Set up USB serial port for gas sampler
ser = serial.Serial('/dev/ttyUSB0', 38400, timeout=1)

columns = ['Date', 'Time UTC', 'Latitude+', 'Latitude-', 'Data String Indicator', 'DSP counter', 'CO2 PPMV', 'N2O PPBV',
           'Pressure (Torr)', 'Temp (K)']
df = pd.DataFrame(columns=columns)

while True:
    line = ser.readline().decode('utf-8').strip()  # Read a line from the com port
    measurements = line.split(' ')[:-55] # Split the line into measurements, assuming they are separated by spaces, removes unneccisary data
    df = df.append(measurements, ignore_index=True)