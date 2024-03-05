#!/usr/bin/python3
import serial
import numpy as np
import pandas as pd
from datetime import datetime as dt
import base64
import time 
#Everything that is sent to the server and every that is read from the server should be encoded and decodeed accordinly with the funciton

#Utilities
def log(msg, path='/home/cygno01/daq/online/ArduinoServerManager/log.txt'):  #function that write a log file witha specified message
    f=open(path, 'a') #open the log file, append mode
    f.write(str(dt.now())+" "+str(msg)+"\n") #write datetime and message
    f.close() #close the log file

def decodeArd(response):
    decoded_bytes = base64.b64decode(response)
    decoded_str = decoded_bytes.decode('utf-8').strip()
    return decoded_str

def encodeArd(data_to_send):
    encoded_data=base64.b64encode(data_to_send).decode('ascii')
    return encoded_data

#Function
def whichArd(server):
    server.write(encodeArd(b'W'))
    time.sleep(1)
    response=decodeArd(server.readline())
    time.sleep(1)
    return response

def readEnv(server):
    response=server.write(encodeArd(b'R'))
    time.sleep(1)
    response=decodeArd(server.readline()) 
    response_arr=np.array(response.split(sep=";"),dtype="d")
    time.sleep(1)
    return response_arr

def WriteAndRead(server, name, message,verbose=None):
    encoded_message = encodeArd(message.encode())
    server.arduino_write(name, encoded_message)
    time.sleep(1)  # Allow some time for the message to be processed
    # Read the output for calibration
    response_encoded = server.arduino_readlines(name)
    # Assume response_encoded is a list of Base64-encoded strings
    response_decoded = [decodeArd(line) for line in response_encoded]
    if verbose is not None:
        for line in response_decoded:
            print(f"Response from {name}: {line}")
    return response_decoded