import logging
import serial
import time
import os
import pandas as pd

csv_file = 'serial_test.csv'


# Set up USB serial port for gas sampler
ser = serial.Serial('/dev/ttyUSB0', 38400, timeout=1)

columns = ['Date', 'Time UTC', 'Latitude+', 'Latitude-', 'Data String Indicator', 'DSP counter', 'CO2 PPMV', 'N2O PPBV',
           'Pressure (Torr)', 'Temp (K)']
df = pd.DataFrame(columns=columns)

while True:

    line = ser.readline().decode('ascii').strip()  # Read a line from the com port
    measurements = line.split( )[4:-3] # Split the line into measurements, assuming they are separated by spaces, removes unneccisary data
    #goes by index
    df = df.append(measurements, ignore_index=True)
    print(line)
    print(measurements)
    #print(df)
