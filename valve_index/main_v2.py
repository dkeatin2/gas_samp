import threading
import serial
import datetime
import time
import RPi.GPIO as GPIO  # RPi.GPIO can be referred as GPIO from now
import csv
import os
import queue
import logging
import pandas as pd



    #---- setup function instantiates all one-time setup variables ----

#setup threading
data_queue = queue.Queue() # Create a queue for communication between threads

#setting up autosaver
autosave_interval = 60
max_queue_size = 10000


#setting up data reading and recording
ser = serial.Serial('/dev/ttyUSB0', 38400, timeout=1)
columns = ['Date', 'Time UTC', 'Latitude+', 'Latitude-',
           'Data String Indicator','DSP counter', 'CO2 PPMV',
           'N2O PPBV','Pressure (Torr)', 'Temp (K)','Active Valve']

df = pd.DataFrame(columns=columns)

#setup valve_controller
#GPIO/UART/I2C setup stuff goes here
active_valve = 00

def auto_saver():
    #auto_saver will write data buffer to a timestamped CSV file every 10k lines or so.
    #This is to prevent the buffer from overfilling, but also to have some layer of data redundancy


    csv_file = 'sensor_readings.csv'  #append datetime to filename
    # #put df into sensor_readings


def serial_reader():
    # Reads serial into buffer, transposes to match columns, appends active_valve
    while True:
        line = ser.readline().decode('ascii').strip()  # Read a line from the com port
        measurements = line.split()[:-11]  # Split the line into measurements, assuming they are separated by spaces, removes unneccisary data
        measurements.append(active_valve)  #append active_valve to end of measurements
        data_dict = dict(zip(columns, measurements))  # Convert measurements to a dictionary
        df = df.append(data_dict, ignore_index=True)  # Append dictionary to DataFrame

def valve_controller():
    while True:
        #run valves through dictonary of valves/devices
        #update variable 'active_valve' with global for the data logger function
        global active_valve


def endprogram():
    #set all gpio pin to off

    #close serial connection
    ser.close()

    #save remaining readings to csv?

    #log termination of script

# Create separate threads for reading data from the com port and auto-saving
serial_reader_thread = threading.Thread(target=serial_reader)
auto_saver_thread = threading.Thread(target=auto_saver)

#start both threads
serial_reader_thread.start()
auto_saver_thread.start()

if __name__ == '__main_v2__':
    #setup()

    try:
        valve_controller()

    except KeyboardInterrupt: #when keyboardinterrupt, activate following
        endprogram()
        #In the future, add a way to detect power loss and exicute endprogram() to gracefully shutdown.