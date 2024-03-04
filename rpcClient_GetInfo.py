#!/usr/bin/python3
import argparse
from xmlrpc.client import ServerProxy
import time
import utilities as ut  # Assuming this contains encodeArd and decodeArd functions

log_path = '/home/cygno01/Desktop/ArduinoServerManager/log.txt'

def main():
    parser = argparse.ArgumentParser(description='Set the source position after calibrating')
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
        ut.log(f"Reading {name} variables...")
        KEG_env=ut.WriteAndRead(server, name, "R",verbose=args.verbose)[0]
        time.sleep(1)        
        source_pos=ut.WriteAndRead(server, name, "G",verbose=args.verbose)[0][-5:]
        time.sleep(1)        
    except Exception as e:
        ut.log(f"Error interacting with {name}: {e}",log_path)
        if args.verbose is not None: print(f"Error interacting with {name}: {e}")
    name="MANGOlino"
    try:
        if args.verbose is not None:
            # Use the prefixed method name for getting port information
            ser_port = server.arduino_get_port(name)
            print(f"Info for {name}: Port={ser_port}")
        ut.log(f"Reading {name} variables...")
        MANGO_env=ut.WriteAndRead(server, name, "R",verbose=args.verbose)[0]
        time.sleep(1)              
    except Exception as e:
        ut.log(f"Error interacting with {name}: {e}",log_path)
        if args.verbose is not None: print(f"Error interacting with {name}: {e}")

    print(f"KEG: {KEG_env};{source_pos} - MANGOlino: {MANGO_env}")

if __name__ == "__main__":
    main()