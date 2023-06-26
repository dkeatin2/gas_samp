import serial
import time

# Initialize serial port
ser = serial.Serial('/dev/ttyUSB0', 9600)

while True:
    # Define the data to be sent
    data = "Hello, World!\n"

    # Write the data to the serial port
    ser.write(data.encode())

    # Read from the serial port
    read_data = ser.readline().decode().strip()  # Use .decode() to convert bytes to string

    # Print the data received
    print(read_data)

    # Check if sent and received data are same
    if data.strip() == read_data:
        print("Loopback test passed")
    else:
        print("Loopback test failed")

    # Wait before sending the next message
    time.sleep(1)
