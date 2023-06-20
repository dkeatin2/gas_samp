#modifying the previous code to index through all valves and handle I2C communication.
#skipping ingesting usb serial data for now, the gas sampler has it's own datalog

#this should index through all valves attached to the raspi over GPIO
#and record which valves were activated with time stamp.
#the CSV produced can be combined with the gas sampler's data for complete result analysis






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

# Set up logging
logging.basicConfig(filename='status.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

csv_file = 'valve_history.csv'
autosave_interval = 60
max_queue_size = 10000

columns = ['Date', 'Time UTC', 'Valve operating', 'current operation', 'leak fault?', 'total valve actuations', 'total run time']
#example: date, time, valve_01, purge, N, 12349, 00:43:20:10


df = pd.DataFrame(columns=columns)

# Create a queue for communication between threads
data_queue = queue.Queue()

# set up variables


# build list of total valves and assign them pin numbers, this will be usefull as we expand to breakout boards
# valve = []

valve_1_pin = 16  # gpio pin for valve 1 and soforth
valve_2_pin = 18  # gpio pin for purge valve?

# time values below are a stand-in till we know how long it takes for sample gas to reach the sampler
sample_time = 10
purge_time = 10

# pin assignments
ledPin = 22  # status LED pin22


# def leak_detection():
#    this will detect leaks with either a dedicated thread or a watchdog in the main loop
# if leak detected, pause data collection, sound alarm,

# setup GPIO pins
def setup():
    GPIO.setmode(GPIO.BOARD)  # GPIO Numbering of Pins
    GPIO.setup(ledPin, GPIO.OUT)  # Set ledPin as output
    GPIO.output(ledPin, GPIO.LOW)  # Set ledPin to LOW to turn Off the LED
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(ledPin, GPIO.OUT)
    GPIO.setup(valve_1_pin, GPIO.OUT)
    GPIO.setup(valve_2_pin, GPIO.OUT)


# Define a function to append a row to the CSV file
def append_to_csv(row, csv_file):
    try:
        if not os.path.isfile(csv_file):
            row.to_csv(csv_file, index=False)
        else:
            row.to_csv(csv_file, mode='a', header=False, index=False)
    except Exception as e:
        logging.error("Error appending to CSV: %s", e)


# read data from the com port in a separate thread
def read_data():
    timeout = 10  # set a timeout of 10 seconds
    while True:
        try:
            ser.timeout = timeout  # set the timeout
            line = ser.readline().decode('utf-8').strip()  # Read a line from the com port

            # Split the line into measurements, assuming they are separated by spaces
            measurements = line.split(' ')[:-55]

            # Check if the number of measurements matches the number of columns in the DataFrame
            if len(measurements) == len(columns):

                # Convert the measurements to floats and create a new DataFrame row
                data = {}
                for column, value in zip(columns, measurements):
                    if value.isnumeric():
                        data[column] = float(value)
                    else:
                        data[column] = value
                row = pd.DataFrame(data, columns=columns, index=[0])

                # Append the row to the CSV file
                append_to_csv(row, csv_file)

                # Check if the queue size is within limits before adding the row
                if data_queue.qsize() < max_queue_size:
                    data_queue.put(row)
                else:
                    logging.warning("Queue size limit reached, discarding the oldest data.")
                    data_queue.get()
                    data_queue.put(row)
            else:
                logging.warning("Received an improperly formatted line, skipping.")
        except Exception as e:
            logging.error("Error appending to CSV: %s", e)


# Define a function to auto-save and reset the DataFrame in a separate thread
def auto_save_data():
    global df
    count = 0

    while True:
        try:
            # Get the next row from the queue
            row = data_queue.get()

            # Add the row to the DataFrame
            df = df.append(row, ignore_index=True)
            count += 1

            # Auto-save and reset the DataFrame after a certain number of readings
            if count >= autosave_interval:
                df.to_csv('autosave_{}_{}'.format(int(time.time()), csv_file), index=False)
                df = pd.DataFrame(columns=columns)
                count = 0
        except Exception as e:
            logging.error('Error appending to CSV: %s', e)


def controller():
    while True:
        # now = datetime.datetime.now()
        # timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
        # with open('data.csv', 'a') as f:
        # 	status = 'Sampled and purged successfully'
        # 	data = ','.join([timestamp, '', status])
        # 	f.write(data + '\n')

        # Close the sample valve and open the purge valve
        GPIO.output(valve_1_pin, GPIO.LOW)
        logging.info('purging manifold')
        GPIO.output(valve_2_pin, GPIO.HIGH)
        time.sleep(purge_time)

        # Close the purge valve, pen the sample valve
        GPIO.output(valve_2_pin, GPIO.LOW)
        logging.info('sampling with valve')
        GPIO.output(valve_1_pin, GPIO.HIGH)
        time.sleep(sample_time)

    # future implementation, index through the list of valves, remember to update status logger
    # x = 0
    # while x <= (max valve number)
    # logging.info('purge')
    # #purge vavle open for
    # time.sleep(purge_time)
    # Purge valve close
    # logging.info('sampling with valve',x)
    # sample valve[x] open for (sample_time)
    # time.sleep(sample_time)
    # timestamp+status
    # sample valve[x] close
    # x+1
    # else
    # x = 0


def endprogram():
    GPIO.output(ledPin, GPIO.LOW)  # LED Off
    GPIO.output(valve_1_pin, GPIO.LOW)
    GPIO.output(valve_2_pin, GPIO.LOW)
    GPIO.cleanup()  # Release resources

    # Close the serial connection when the script is interrupted
    ser.close()

    # Save the remaining readings in the DataFrame to a CSV file
    df.to_csv('autosave_{}_{}'.format(int(time.time()), csv_file), index=False)

    # Log the termination of the script
    logging.info('Sensor readings saved, script terminated.')
    print('Sensor readings saved.')


def loop():
    while True:
        GPIO.output(ledPin, GPIO.HIGH)  # LED On

        GPIO.output(ledPin, GPIO.LOW)  # LED Off
        time.sleep(1.0)  # wait 1 sec


# Create separate threads for reading data from the com port and auto-saving
data_thread = threading.Thread(target=read_data)
auto_save_thread = threading.Thread(target=auto_save_data)

# Start the data and auto-save threads
data_thread.start()
auto_save_thread.start()

if __name__ == '__main__':
    # set up GPIO pins
    setup()

    try:
        # run main loop
        controller()
        while True:
            # Keep the main thread running while the data and auto-save threads are working
            time.sleep(1)
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the destroy() will be  executed.
        endprogram()
