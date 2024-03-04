#!/usr/bin/python3
import argparse
from xmlrpc.client import ServerProxy
import time
import utilities as ut  # Assuming this contains encodeArd and decodeArd functions

log_path = '/home/cygno01/Desktop/ArduinoServerManager/log.txt'

def WriteAndRead(server, name, message,verbose=None):
    encoded_message = ut.encodeArd(message.encode())
    server.arduino_write(name, encoded_message)
    time.sleep(1)  # Allow some time for the message to be processed
    # Read the output for calibration
    response_encoded = server.arduino_readlines(name)
    # Assume response_encoded is a list of Base64-encoded strings
    response_decoded = [ut.decodeArd(line) for line in response_encoded]
    if verbose is not None:
        for line in response_decoded:
            print(f"Response from {name}: {line}")
    return response_decoded

def main():
    parser = argparse.ArgumentParser(description='Set the source position after calibrating')
    parser.add_argument("-p", "--position", help='Position to set in Arduino', action='store', type=float, default=10)
    parser.add_argument("-v", "--verbose", help='Additional check and printout', action='store', type=int, default=None)
    args = parser.parse_args()

    port = 8000
    server = ServerProxy(f"http://localhost:{port}")

    name="KEG"
    try:
        if args.verbose is not None:
            # Use the prefixed method name for getting port information
            ser_port = server.arduino_get_port(name)
            print(f"Info for {name}: Port={ser_port}")

        ut.log(f"Setting Position to: {args.position}",log_path)
        if args.verbose is not None: print("Calibrating...")
        WriteAndRead(server, name, "C",verbose=args.verbose)
        time.sleep(1)
        if args.verbose is not None: print("Asking pos...")
        WriteAndRead(server, name, "P",verbose=args.verbose)
        time.sleep(1)
        if args.verbose is not None: print("Setting pos...")
        WriteAndRead(server, name, str(args.position),verbose=args.verbose)
        time.sleep(1)
        if args.verbose is not None: print("Checking pos...")
        final_pos=WriteAndRead(server, name, "G",verbose=args.verbose)
        if args.position==float(final_pos[0][-5:]):
            if args.verbose is not None: print(f"Position set correclty at: {args.position}")
            ut.log(f"Position set correclty at: {args.position}",log_path)
        else:
            if args.verbose is not None: print(f"Error moving the source to position {args.position}: Actual Position is {final_pos}")
            ut.log(f"Error moving the source to position {args.position}: Actual Position is {final_pos}",log_path)
    except Exception as e:
        ut.log(f"Error interacting with {name}: {e}",log_path)
        if args.verbose is not None: print(f"Error interacting with {name}: {e}")


if __name__ == "__main__":
    main()