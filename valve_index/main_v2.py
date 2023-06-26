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

#___setting up autosaver___
autosave_interval = 60
max_queue_size = 10000


#___setting up data reading and recording___
ser = serial.Serial('/dev/ttyUSB0', 38400, timeout=1)
columns = ['Date', 'Time UTC', 'Latitude+', 'Latitude-',
           'Data String Indicator', 'DSP counter', 'CO2 PPMV',
           'N2O PPBV', 'Pressure (Torr)', 'Temp (K)', 'Active Valve']

df = pd.DataFrame(columns=columns)

#___setup valve_controller___
#GPIO/UART/I2C setup stuff goes here
GPIO.setmode(GPIO.BOARD)  # GPIO Numbering of Pins

#setup GPIO pin for UPS failsafe
ups_flag = False
ups_pin = 17
GPIO.setup(ups_pin, GPIO.IN)

#put this somewhere fast loopin
#if ups_pin is pulled low:
#    ups_flag = True


#dictonary for device ID, valve .no, valve time.
#this is to allow custom valve times for each valve, stored neatly.
#valve_time for each valve may need to vary based on distance from the gas sensor.
#"device name": [(gpio pin number, number of seconds to hold valve)]

devices = {
    "pi_pico_01": [(2, 1), (3, 2), (4, 3)],
    "pi_pico_02": [(2, 1), (3, 2), (4, 3)],
    # Add more devices as needed
}


#Depreciate V
#make a list of 0 to 48
valve_list = list(range(0, 47))
active_valve = 0
temp_gpio = 0
#Depreciate ^

#__Perhaps__ you could do some intel sampling by switching to a new valve
# after gas values level out enough to be considered a good reading


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


        #iterate through valve list, lock out active valve and update it for auto_saver to grab
        #(lock stops the variable from being accessed untill the process is finished)

        for i in valve_list:
            with lock:
                active_valve = i
            #set valve gpio high for valve_time
            with lock:
                active_valve = 'p'
            #set purge

        for pin, sample_time in devices["pi_pico_01"]:
            GPIO.output(pin, GPIO.HIGH)
            time.sleep(sample_time)

        #placeholder method of stepping through valves in index



def endprogram():
    #set all gpio pin to off


    GPIO.cleanup()

    #close serial connection
    ser.close()

    #save remaining readings to csv

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

    except KeyboardInterrupt or ups_flag == True: #when keyboardinterrupt or UPS trips, run the following
        endprogram()
