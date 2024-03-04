#!/usr/bin/python3
import argparse
from xmlrpc.client import ServerProxy
import time
import utilities as ut  # Assuming this contains encodeArd and decodeArd functions

log_path = '/home/cygno01/Desktop/ArduinoServerManager/log.txt'

def main():
    parser = argparse.ArgumentParser(description='Send a request to one Arduino')
    parser.add_argument("-m", "--message", help='Message to send', action='store', type=str, default="W")
    parser.add_argument("-a", "--arduino", help='Select Arduino, if None the message will be sent to both of them', action='store', type=str, default=None)
    parser.add_argument("-v", "--verbose", help='Additional check and printout', action='store', type=int, default=None)
    args = parser.parse_args()

    port = 8000
    server = ServerProxy(f"http://localhost:{port}")

    device_names = [args.arduino] if args.arduino else ['KEG', 'MANGOlino']

    for name in device_names:
        try:
            if args.verbose is not None:
                # Use the prefixed method name for getting port information
                ser_port = server.arduino_get_port(name)
                print(f"Info for {name}: Port={ser_port}")

            # Encode the message and use the prefixed method name for writing
            encoded_message = ut.encodeArd(args.message.encode())
            server.arduino_write(name, encoded_message)
            time.sleep(1)  # Allow some time for the message to be processed

            # Use the prefixed method name for reading the response
            response_encoded = server.arduino_readline(name)
            response = ut.decodeArd(response_encoded)
            if args.verbose is not None:
                print(f"Response from {name} after sending {args.message}: {response}")
            else:
                print(response)

        except Exception as e:
            print(f"Error interacting with {name}: {e}")

if __name__ == "__main__":
    main()