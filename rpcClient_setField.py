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
    parser.add_argument("-gem", "--gem", nargs=3, type=float, default=[500, 500, 500], help="GEMs voltages in order from 1 to 3")
    parser.add_argument("-f", "--field", type=float, default=300, help="Field to Set in V/cm")
    parser.add_argument("-v", "--verbose", help='Additional check and printout', action='store', type=int, default=None)
    args = parser.parse_args()

    server = ServerProxy(f"http://localhost:{args.port}")
    transfer=500#volt
    V_GEMs=np.sum(args.gem)
    space_ring=0.9#cm
    drift=14.25#cm
    GEM_stack=V_GEMs+2*transfer
    FC_base=GEM_stack+(args.field*space_ring)
    FC_top=FC_base+(drift*args.field)
    
    if args.verbose is not None: print(f"FC base {FC_base} and FC top {FC_top}")

    if FC_top>14900 or FC_base >14900: 
        ut.log("Field to large for this GEM configuration", log_path)
        sys.exit(1)
    

    try:
        #ON the channels
        server.hv_set(0, "Pw", 1)
        server.hv_set(1, "Pw", 1)
        if args.verbose is not None: print(f"Channels ON")    
        ut.log(f"Channels ON.", log_path)
        
        server.hv_set(0, "VSet", float(FC_base))
        if args.verbose is not None: print(f"Channels 0 at {FC_base}")    
        server.hv_set(1, "VSet", float(FC_top))
        if args.verbose is not None: print(f"Channels 1 at {FC_top}")    
        ut.log(f"CH0 at {FC_base}, CH1 at {FC_top}", log_path)

    except Exception as e:
        ut.log(f"ERROR in setting drift field: {e}", log_path)
        if args.verbose is not None: print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()