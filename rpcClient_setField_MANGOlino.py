import argparse
import sys
from xmlrpc.client import ServerProxy
import time
import utilities as ut  # Assuming this contains the log function
import numpy as np

log_path = '/home/cygno01/daq/online/ArduinoServerManager/log.txt'

def main():
    parser = argparse.ArgumentParser(description='Control and monitor HV board.')
    parser.add_argument("-p", "--port", type=int, default=8000, help="Port of the XML-RPC server, default 8000")
    parser.add_argument("-gem", "--gem", nargs=3, type=float, default=[400, 400, 400], help="GEMs voltages in order from 1 to 3")
    parser.add_argument("-f", "--field", type=float, default=0.3, help="Drift field to Set in kV/cm")
    parser.add_argument("-t", "--transfer", type=float, default=2.5, help="Set transfer field in kV/cm")
    parser.add_argument("-v", "--verbose", help='Additional check and printout', action='store_true')
    args = parser.parse_args()

    server = ServerProxy(f"http://localhost:{args.port}")
    transfer=200*args.transfer#volt
    V_GEMs=np.sum(args.gem)
    space_ring=1#cm
    drift=4.25#cm
    GEM_stack=V_GEMs+2*transfer
    FC_base=GEM_stack+(args.field*space_ring*1000)
    FC_top=FC_base+(drift*args.field*1000)
    
    if args.verbose: 
        print(f"GEM stack is at: {GEM_stack}")
        print(f"FC base is at: {FC_base}")
        print(f"Cathode voltage will be: {FC_top}")

    if FC_top>14900 or FC_base >14900: 
        ut.log("Field to large for this GEM configuration", log_path)
        sys.exit(1)

    try:
        #ON the channels
        server.hv_set(0, "Pw", 1)
        if args.verbose: print(f"Channel 0 ON")    
        ut.log(f"Channel 0 ON.", log_path)
        
        server.hv_set(0, "VSet", float(FC_top))
        if args.verbose: print(f"Channels 0 at {FC_top}")    
        ut.log(f"CH0 at {FC_top}", log_path)

    except Exception as e:
        ut.log(f"ERROR in setting drift field: {e}", log_path)
        if args.verbose: print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()