#!/usr/bin/python3
import utilities as ut
from xmlrpc.client import ServerProxy
import base64
import time
import argparse
import signal
from contextlib import contextmanager

log_path='/home/cygno01/Desktop/ArduinoServerManager/log.txt'

# Define a timeout exception class
class TimeoutException(Exception):
    pass

# Timeout handler function
def timeout_handler(signum, frame):
    raise TimeoutException

# Context manager to apply the timeout to a block of code
@contextmanager
def timeout(time):
    # Register the signal function handler
    signal.signal(signal.SIGALRM, timeout_handler)
    # Schedule the SIGALRM signal to be sent after `time` seconds
    signal.alarm(time)
    try:
        yield
    except TimeoutException:
        print("Operation timed out!")
    finally:
        # Disable the alarm
        signal.alarm(0)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Send a request to one Arduino')
    parser.add_argument("-m","--message",help='Message to send', action='store', type=str, default="W")
    parser.add_argument("-a","--arduino",help='Select Arduino, if None the message will be sent to both of them', action='store', type=str, default=None)
    parser.add_argument("-v","--verbose",help='additional check and printout', action='store', type=int, default=None)
    args = parser.parse_args()
    
    port = 8000
    server = ServerProxy(f"http://localhost:{port}")
    
    device_names = [args.arduino] if args.arduino else ['KEG', 'MANGOlino']
    
    for name in device_names:
        try:
            if args.verbose is not None: 
                ser_port = server.get_port(name)
                print(f"Info for {name}: Port={ser_port}")
            
            server.write(name, ut.encodeArd(args.message.encode()))
            time.sleep(1)  # Allow some time for the message to be processed
            response_encoded = server.readline(name)
            response = ut.decodeArd(response_encoded)
            if args.verbose is not None: print(f"Response from {name} after sending {args.message}: {response}")
            else: print(response)     

        except Exception as e:
            print(f"Error interacting with {name}: {e}")