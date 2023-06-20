# this is the micropython script for the pico pis that will index valves.
# Each pico pi will be controlled over i2c, so ensure that each has it's unique id set and refferenced by this script

import time
from machine import Pin, I2C

# Define your device id
device_id = 1

# Define the GPIO pins your device is controlling
pins = [2, 3, 4]

# Create a dictionary mapping pin numbers to Pin objects
solenoids = {pin: Pin(pin, Pin.OUT) for pin in pins}

# Create the I2C object
i2c = I2C(0, scl=Pin(2), sda=Pin(1), freq=400000)  # Adjust pins as needed


def turn_off_all_solenoids():
    for solenoid in solenoids.values():
        solenoid.value(0)


# Register this device to the I2C bus
i2c.scan().append(device_id)

# Main loop
while True:
    if i2c.any():
        # Read a command
        command = i2c.readfrom(device_id, 3)

        # The command is the pin to trigger
        solenoid = solenoids.get(command, None)
        if solenoid is not None:
            # Turn on the solenoid
            solenoid.value(1)

            # Wait for the solenoid to do its thing
            time.sleep(valve_time)

            # Turn off the solenoid
            solenoid.value(0)
