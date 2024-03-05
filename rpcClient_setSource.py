#!/usr/bin/python3
import argparse
from xmlrpc.client import ServerProxy
import time
import utilities as ut  # Assuming this contains encodeArd and decodeArd functions

log_path = '/home/cygno01/daq/online/ArduinoServerManager/log.txt'

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
        ut.WriteAndRead(server, name, "C",verbose=args.verbose)
        time.sleep(1)
        if args.position ==0:
            if args.verbose is not None: print("Checking pos...")
            final_pos=ut.WriteAndRead(server, name, "G",verbose=args.verbose)
            if args.position==float(final_pos[0][-5:]):
                if args.verbose is not None: print(f"Position set correclty at: {args.position}")
                ut.log(f"Position set correclty at: {args.position}",log_path)
            else:
                if args.verbose is not None: print(f"Error moving the source to position {args.position}: Actual Position is {final_pos}")
                ut.log(f"Error moving the source to position {args.position}: Actual Position is {final_pos}",log_path)
        else:
            if args.verbose is not None: print("Asking pos...")
            ut.WriteAndRead(server, name, "P",verbose=args.verbose)
            time.sleep(1)
            if args.verbose is not None: print("Setting pos...")
            ut.WriteAndRead(server, name, str(args.position),verbose=args.verbose)
            time.sleep(1)
            if args.verbose is not None: print("Checking pos...")
            final_pos=ut.WriteAndRead(server, name, "G",verbose=args.verbose)
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