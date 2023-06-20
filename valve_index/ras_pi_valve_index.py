#this is the valve index version intended to communicate to a number of i2c connected pico pies
#effectivly using them as GIPO bus expanders, so that neumerous sites can have gas collected.

#please ensure that valve numbers correspond to the correct valves!

import RPi.GPIO as GPIO
import time
import csv
from smbus2 import SMBus

GPIO.setmode(GPIO.BOARD)  # Use physical pin numbering
GPIO.setwarnings(False)

# Define your I2C bus. (1) is typically used for newer Raspberry Pis. If you're using a really old one, it might be (0)
bus = SMBus(1)

valve_time = 5  # replace with your time for each solenoid
purge_pin = 7  # replace with your GPIO pin for the purge valve
purge_time = 1  # replace with your time for the purge solenoid

# setup the purge pin as output
GPIO.setup(purge_pin, GPIO.OUT, initial=GPIO.LOW)

# Define your I2C devices (Raspberry Pi Picos) along with the GPIOs they are controlling
# deviceID: [ gpio pins]
devices = {
    1: [2, 3, 4],
    2: [5, 6, 7],
    # Add more devices as needed
}

def turn_off_all_solenoids():
    for device, pins in devices.items():
        for pin in pins:
            # Send a 0 to the pin to turn it off
            bus.write_byte_data(device, pin, 0)
    GPIO.output(purge_pin, GPIO.LOW)

try:
    # open the CSV file for writing
    with open('log.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Device", "Solenoid", "Start", "End"])

        # iterate over each device and pin
        for device, pins in devices.items():
            for pin in pins:
                # Send a 1 to the pin to turn it on
                bus.write_byte_data(device, pin, 1)

                start_time = time.ctime()
                # wait for valve_time seconds
                time.sleep(valve_time)
                end_time = time.ctime()

                # Send a 0 to the pin to turn it off
                bus.write_byte_data(device, pin, 0)

                # log the solenoid activation to the CSV
                writer.writerow([device, pin, start_time, end_time])

                # activate the purge solenoid
                GPIO.output(purge_pin, GPIO.HIGH)

                purge_start_time = time.ctime()
                # wait for purge_time seconds
                time.sleep(purge_time)
                purge_end_time = time.ctime()

                # deactivate the purge solenoid
                GPIO.output(purge_pin, GPIO.LOW)

                # log the purge solenoid activation to the CSV
                writer.writerow([purge_pin, purge_start_time, purge_end_time])

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Always turn off all solenoids and cleanup GPIO even if an error occurs
    turn_off_all_solenoids()
    GPIO.cleanup()
