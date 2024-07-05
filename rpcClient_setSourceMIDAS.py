#!/usr/bin/python3
import argparse
from xmlrpc.client import ServerProxy
import time
import utilities as ut  # Assuming this contains encodeArd and decodeArd functions
import re
import midas
import midas.client

log_path = '/home/cygno01/daq/online/ArduinoServerManager/log.txt'

def extract_number_from_string(string):
    # Define a regular expression pattern to match the number after a colon
    pattern = r':\s*([-+]?\d*\.\d+|\d+)'  # Matches floating-point or integer numbers
    
    # Search for the pattern in the string
    match = re.search(pattern, string)
    
    if match:
        # Extract the matched number
        number_str = match.group(1)
        
        # Convert the extracted number string to a float
        number = float(number_str)
        return number
    else:
        return None  # Return None if no match found
    
def main():
    client = midas.client.MidasClient("rpcClient_setSource")
    
    parser = argparse.ArgumentParser(description='Set the source position after calibrating')
    parser.add_argument("-p", "--position", help='Position to set in Arduino', action='store', type=float, default=10)
    parser.add_argument("-v", "--verbose", help='Additional check and printout', action='store', type=int, default=None)
    args = parser.parse_args()

    print(client.odb_get("/Equipment/MANGOSensors/Settings/SerialBusy"))

    while client.odb_get("/Equipment/MANGOSensors/Settings/SerialBusy"):
            time.sleep(1)
            
    client.odb_set("/Equipment/MANGOSensors/Settings/SerialBusy", True)
            
    port = 8000
    server = ServerProxy(f"http://localhost:{port}")

    name="KEG"
    try:
        if args.verbose is not None:
            # Use the prefixed method name for getting port information
            ser_port = server.arduino_get_port(name)
            print(f"Info for {name}: Port={ser_port}")

        ut.log(f"Setting Position to: {args.position}",log_path)
        client.msg(f"Setting Position to: {args.position}", is_error=False)
        if args.verbose is not None: print("Calibrating...")
        ut.WriteAndRead(server, name, "C",verbose=args.verbose)
        time.sleep(1)
        if args.position ==0:
            if args.verbose is not None: print("Checking pos...")
            final_pos=ut.WriteAndRead(server, name, "G",verbose=args.verbose)
            if args.position==float(final_pos[0][-5:]):
                if args.verbose is not None: print(f"Position set correclty at: {args.position}")
                ut.log(f"Position set correclty at: {args.position}",log_path)
                client.msg(f"Position set correclty at: {args.position}", is_error=False)
            else:
                if args.verbose is not None: print(f"Error moving the source to position {args.position}: Actual Position is {final_pos}")
                ut.log(f"Error moving the source to position {args.position}: Actual Position is {final_pos}",log_path)
                client.msg(f"Error moving the source to position {args.position}: Actual Position is {final_pos}", is_error=False)
        else:
            if args.verbose is not None: print("Asking pos...")
            ut.WriteAndRead(server, name, "P",verbose=args.verbose)
            time.sleep(1)
            if args.verbose is not None: print("Setting pos...")
            ut.WriteAndRead(server, name, str(args.position),verbose=args.verbose)
            time.sleep(1)
            if args.verbose is not None: print("Checking pos...")
            final_pos=ut.WriteAndRead(server, name, "G",verbose=args.verbose)
            # print(final_pos)
            # if args.position==float(final_pos[0][-6:]):
            if args.position==extract_number_from_string(final_pos[0]):
                if args.verbose is not None: print(f"Position set correclty at: {args.position}")
                ut.log(f"Position set correclty at: {args.position}",log_path)
                client.msg(f"Position set correclty at: {args.position}", is_error=False)
            else:
                if args.verbose is not None: print(f"Error moving the source to position {args.position}: Actual Position is {final_pos}")
                ut.log(f"Error moving the source to position {args.position}: Actual Position is {final_pos}",log_path)
                client.msg(f"Error moving the source to position {args.position}: Actual Position is {final_pos}", is_error=False)
    except Exception as e:
        ut.log(f"Error interacting with {name}: {e}",log_path)
        client.msg(f"Error interacting with {name}: {e}", is_error=True)
        if args.verbose is not None: print(f"Error interacting with {name}: {e}")
        client.odb_set("/Equipment/MANGOSensors/Settings/SerialBusy", False)
        client.disconnect()
        
    client.odb_set("/Equipment/MANGOSensors/Settings/SerialBusy", False)
    client.disconnect()


if __name__ == "__main__":
    main()
