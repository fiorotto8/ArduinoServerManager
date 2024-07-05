#!/usr/bin/python3
import argparse
from xmlrpc.server import SimpleXMLRPCServer


import sys
sys.path.append('home/software/daq/online/ArduinoServerManager/')

import utilities as ut
import serial
import socket
import base64
import time
import hv
import subprocess

log_path='/home/cygno01/daq/online/ArduinoServerManager/log.txt'

import midas
import midas.client

class ArduinoSerialWrapper:
    def __init__(self, devices, client):
        self.devices = {}
        self.client=client
        for name, (port, baud) in devices.items():
            try:
                self.devices[name] = serial.Serial(port, baud, timeout=0.1)  # 100 ms timeout
                ut.log(f"Connected to Arduino {port}: {name}")
                self.client.msg(f"Connected to Arduino {port}: {name}", is_error=False)

                time.sleep(2)  # Give time for serial connection to establish
            except serial.SerialException as e:
                ut.log(f"Error opening serial port {port}: {e}")
                self.client.msg(f"Error opening serial port {port}: {e}", is_error=True)

    def write(self, name, data):
        device = self.devices.get(name)
        if device:
            data_bytes = base64.b64decode(data)
            return device.write(data_bytes)
        else:
            self.client.msg(f"Device {name} not found", is_error=True)
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
            
            self.client.msg(f"Device {name} not found", is_error=True)
            raise ValueError(f"Device {name} not found")
    
    def get_port(self, name):
        device = self.devices.get(name)
        if device:
            return f"{device.port}"
        else:
            self.client.msg(f"Device {name} not found", is_error=True)
            raise ValueError(f"Device {name} not found")

class HvSerialWrapper:
    def __init__(self, addr, client):
        self.board = hv.Board(addr)
        self.client = client
        if self.board.handle >= 0:
            ut.log("Connected to board with address "+str(addr), log_path)
            self.client.msg("Connected to board with address "+str(addr), is_error=False)
        else:
            ut.log("Error: could not connect to board with address"+str(addr), log_path)
            self.client.msg("Error: could not connect to board with address"+str(addr), is_error=True)
            sys.exit(1)

    def get(self, channel, parameter):
        return self.board.get_channel_value(channel, parameter)

    def set(self, channel, parameter, value):
        return self.board.set_channel_value(channel, parameter, value)


def GetSerialConnections(client, verbose = False):
    p=subprocess.Popen(["ls", "-ltrh", "/dev/serial/by-id/"], stdout=subprocess.PIPE)
    out, err = p.communicate()
    out = out.decode("utf-8")
	
    lines = out.split("\n")
    CAEN_found = False
    MANGOlino_found = False
    KEG_found = False
	
    results = {}
    for i, l in enumerate(lines):
        if "tty" in l:
            if "CAEN" in l:
                if verbose: print("CAEN: ", l, " - ", l[-1])
                CAEN_found = True
                results["HV"] = l[-1]
            elif "95736323532351C081D1" in l:
                if verbose: print("MANGOlino: ", l, " - ", l[-1])
                MANGOlino_found = True
                results["MANGOlino"] = l[-1]
            elif "4423831383835190E090" in l:
                if verbose: print("KEG: ", l, " - ", l[-1])
                KEG_found = True
                results["KEG"] = l[-1]
				
				
    if not CAEN_found:
        client.msg("CAEN HV not found.", is_error=True)
        raise Exception("CAEN HV not found.")
    if not MANGOlino_found:
        client.msg("MANGOlino Arduino not found.", is_error=True)
        raise Exception("MANGOlino Arduino not found.")
    if not KEG_found:
        client.msg("KEG Arduino not found.", is_error=True)
        raise Exception("KEG Arduino not found.")

    return results

if __name__ == '__main__':

    client = midas.client.MidasClient("rpcServer")


    dev_idx = GetSerialConnections(client, verbose = True)
    devices = {
        'KEG': ('/dev/ttyACM'+dev_idx['KEG'], 115200),
        'MANGOlino': ('/dev/ttyACM'+dev_idx['MANGOlino'], 115200),
    }
    """
    devices = {
        'MANGOlino': ('/dev/ttyACM1', 115200),
    }
    """
    hv_board_addr = "ttyACM"+dev_idx["HV"]  # Adjusted for consistency

    port = 8000
    
    with SimpleXMLRPCServer(("0.0.0.0", port), allow_none=True) as server:
        arduino_wrapper = ArduinoSerialWrapper(devices, client)
        hv_wrapper = HvSerialWrapper(hv_board_addr, client)
        
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
        client.msg("Server Alive", is_error=False)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("trying to disconnect...", flush = True)
            client.msg("Server closed", is_error=False)
            client.disconnect()
            print("Disconnected!")
            print ("\nBye, bye...")
            ut.log("Server closed", log_path)
            sys.exit(0)
