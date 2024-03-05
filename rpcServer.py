#!/usr/bin/python3
import argparse
import sys
from xmlrpc.server import SimpleXMLRPCServer
import utilities as ut
import serial
import socket
import base64
import time
import hv

log_path='/home/cygno01/daq/online/ArduinoServerManager/log.txt'

class ArduinoSerialWrapper:
    def __init__(self, devices):
        self.devices = {}
        for name, (port, baud) in devices.items():
            try:
                self.devices[name] = serial.Serial(port, baud, timeout=0.1)  # 100 ms timeout
                ut.log(f"Connected to Arduino {port}: {name}")

                time.sleep(2)  # Give time for serial connection to establish
            except serial.SerialException as e:
                ut.log(f"Error opening serial port {port}: {e}")

    def write(self, name, data):
        device = self.devices.get(name)
        if device:
            data_bytes = base64.b64decode(data)
            return device.write(data_bytes)
        else:
            raise ValueError(f"Device {name} not found")
    
    def readlines(self, name):
        device = self.devices.get(name)
        if device:
            lines = []  # Initialize an empty list to hold the lines read from the serial port
            start_time = time.time()  # Record the start time for the timeout
            read_timeout = 60  # Timeout in seconds

            while True:
                if time.time() - start_time > read_timeout:
                    break  # Break the loop if the timeout is reached

                line = device.readline()  # Read a line from the serial port
                if line:
                    encoded_line = base64.b64encode(line).decode("utf-8")  # Encode the line
                    lines.append(encoded_line)  # Add the encoded line to the list
                    if "PANDA" in line.decode("utf-8"):  # Check if the decoded line contains "PANDA"
                        break  # Exit the loop if "PANDA" is found
                    start_time = time.time()  # Reset the start time whenever new data is received
                else:
                    time.sleep(0.1)  # Small delay to prevent a tight loop if no data is available

            return lines
        else:
            raise ValueError(f"Device {name} not found")
    
    def get_port(self, name):
        device = self.devices.get(name)
        if device:
            return f"{device.port}"
        else:
            raise ValueError(f"Device {name} not found")

class HvSerialWrapper:
    def __init__(self, addr):
        self.board = hv.Board(addr)
        if self.board.handle >= 0:
            ut.log("Connected to board with address "+str(addr), log_path)
        else:
            ut.log("Error: could not connect to board with address"+str(addr), log_path)
            sys.exit(1)

    def get(self, channel, parameter):
        return self.board.get_channel_value(channel, parameter)

    def set(self, channel, parameter, value):
        return self.board.set_channel_value(channel, parameter, value)

if __name__ == '__main__':
    devices = {
        'KEG': ('/dev/ttyACM0', 115200),
        'MANGOlino': ('/dev/ttyACM1', 115200),
    }
    hv_board_addr = "ttyACM3"  # Adjusted for consistency

    port = 8000
    with SimpleXMLRPCServer(("0.0.0.0", port), allow_none=True) as server:
        arduino_wrapper = ArduinoSerialWrapper(devices)
        hv_wrapper = HvSerialWrapper(hv_board_addr)
        
        # Arduino methods
        server.register_function(lambda name, data: arduino_wrapper.write(name, data), 'arduino_write')
        server.register_function(lambda name: arduino_wrapper.readlines(name), 'arduino_readlines')
        server.register_function(lambda name: arduino_wrapper.get_port(name), 'arduino_get_port')

        # HV Board methods
        server.register_function(lambda channel, parameter: hv_wrapper.get(channel, parameter), 'hv_get')
        server.register_function(lambda channel, parameter, value: hv_wrapper.set(channel, parameter, value), 'hv_set')
        
        # Register introspection functions
        server.register_introspection_functions()
        
        ut.log("Server Alive", log_path)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            ut.log("Server closed", log_path)
            sys.exit(0)