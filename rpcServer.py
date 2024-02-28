#!/usr/bin/python3
import argparse
import sys
from xmlrpc.server import SimpleXMLRPCServer
import utilities as ut
import serial
import socket
import base64
import time

log_path='/home/cygno01/Desktop/ArduinoServerManager/log.txt'

class ArduinoSerialWrapper:
    def __init__(self, devices):
        self.devices = {}
        for name, (port, baud) in devices.items():
            try:
                self.devices[name] = serial.Serial(port, baud)
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
    
    def readline(self, name):
        device = self.devices.get(name)
        if device:
            return base64.b64encode(device.readline()).decode("utf-8")
        else:
            raise ValueError(f"Device {name} not found")
    
    def get_port(self, name):
        device = self.devices.get(name)
        if device:
            return f"{device.port}"
        else:
            raise ValueError(f"Device {name} not found")

if __name__ == '__main__':
    devices = {
        # Device name mapped to (port, baud rate)
        'KEG': ('/dev/ttyACM0', 115200),
        'MANGOlino': ('/dev/ttyACM1', 115200),
    }

    port = 8000
    with SimpleXMLRPCServer(("0.0.0.0", port), allow_none=True) as server:
        # Register a single ArduinoSerialWrapper instance that handles all devices
        wrapper = ArduinoSerialWrapper(devices)
        server.register_instance(wrapper)
        
        # Register introspection functions
        server.register_introspection_functions()

        ut.log("Server alive", log_path)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            ut.log("Server closed", log_path)
            sys.exit(0)