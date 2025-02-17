"""
Example of a basic midas frontend that has one periodic equipment.

See `examples/multi_frontend.py` for an example that uses more
features (frontend index, polled equipment, ODB settings etc). 
"""

import midas
import midas.frontend
import midas.event
from paramiko import SSHClient
import numpy as np
from time import sleep
from datetime import datetime
import psutil
import re

import sys
sys.path.append('/home/software/daq/online/ArduinoServerManager/')
import utilities as ut  # Assuming this contains encodeArd and decodeArd functions

import argparse
from xmlrpc.client import ServerProxy
import time
from datetime import datetime as dt
import csv




class DAQServerEquipment(midas.frontend.EquipmentBase):
    """
    We define an "equipment" for each logically distinct task that this frontend
    performs. For example, you may have one equipment for reading data from a
    device and sending it to a midas buffer, and another equipment that updates
    summary statistics every 10s.
    
    Each equipment class you define should inherit from 
    `midas.frontend.EquipmentBase`, and should define a `readout_func` function.
    If you're creating a "polled" equipment (rather than a periodic one), you
    should also define a `poll_func` function in addition to `readout_func`.
    """
    def __init__(self, client):
        # The name of our equipment. This name will be used on the midas status
        # page, and our info will appear in /Equipment/MyPeriodicEquipment in
        # the ODB.
        equip_name = "DAQServer"
        
        # Define the "common" settings of a frontend. These will appear in
        # /Equipment/MyPeriodicEquipment/Common. The values you set here are
        # only used the very first time this frontend/equipment runs; after 
        # that the ODB settings are used.
        default_common = midas.frontend.InitialEquipmentCommon()
        default_common.equip_type = midas.EQ_PERIODIC
        default_common.buffer_name = "SYSTEM"
        default_common.trigger_mask = 0
        default_common.event_id = 200
        default_common.period_ms = 10000
        default_common.read_when = midas.RO_ALWAYS
        default_common.log_history = 1
        
        # You MUST call midas.frontend.EquipmentBase.__init__ in your equipment's __init__ method!
        midas.frontend.EquipmentBase.__init__(self, client, equip_name, default_common)
        
        # You can set the status of the equipment (appears in the midas status page)
        self.set_status("Initialized")

    def readout_func(self):
        """
        For a periodic equipment, this function will be called periodically
        (every 100ms in this case). It should return either a `cdms.event.Event`
        or None (if we shouldn't write an event).
        """
       
       
        ram_used  = psutil.virtual_memory().used/1000/1000/1000
        ram_avail = psutil.virtual_memory().available/1000/1000/1000
       
        self.client.odb_set("/Equipment/DAQServer/Variables/RAMUsed", ram_used)
        self.client.odb_set("/Equipment/DAQServer/Variables/RAMAvailable", ram_avail)
        
        
        # In this example, we just make a simple event with one bank.
        #event = midas.event.Event()
        
        # Create a bank (called "MYBK") which in this case will store 8 ints.
        # data can be a list, a tuple or a numpy array.
        #data = [float(ram_used), float(ram_avail)]
        #event.create_bank("DAQS", midas.TID_FLOAT, data)
        
        
        return None


class MANGOSensorsEquipment(midas.frontend.EquipmentBase):
    """
    Each equipment class you define should inherit from 
    `midas.frontend.EquipmentBase`, and should define a `readout_func` function.
    If you're creating a "polled" equipment (rather than a periodic one), you
    should also define a `poll_func` function in addition to `readout_func`.
    """
    def __init__(self, client):
        # The name of our equipment. This name will be used on the midas status
        # page, and our info will appear in /Equipment/MyPeriodicEquipment in
        # the ODB.
        equip_name = "MANGOSensors"
        
        # Define the "common" settings of a frontend. These will appear in
        # /Equipment/MyPeriodicEquipment/Common. The values you set here are
        # only used the very first time this frontend/equipment runs; after 
        # that the ODB settings are used.
        default_common = midas.frontend.InitialEquipmentCommon()
        default_common.equip_type = midas.EQ_PERIODIC
        default_common.buffer_name = "SYSTEM"
        default_common.trigger_mask = 0
        default_common.event_id = 201
        default_common.period_ms = 20000
        default_common.read_when = midas.RO_ALWAYS
        default_common.log_history = 1

        self.log_path = '/home/cygno01/daq/online/ArduinoServerManager/log.txt'

        # You MUST call midas.frontend.EquipmentBase.__init__ in your equipment's __init__ method!
        midas.frontend.EquipmentBase.__init__(self, client, equip_name, default_common)
        
        # You can set the status of the equipment (appears in the midas status page)
        self.set_status("Initialized")
        


    def extract_number_from_string(self, string):
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
       
    def setSource(self, port, server, name):

        selectedPosition = self.client.odb_get("/Configurations/StepperMotor/SelectedPosition")
        positions = np.array(self.client.odb_get("/Configurations/StepperMotor/Position"))

        hole     = selectedPosition
        position = positions[selectedPosition]

        try:
            ut.log(f"Setting Position to: {position}",self.log_path)
            self.client.msg(f"Setting Position to: {position}", is_error=False)
            self.client.odb_set("/Configurations/SourceState/source_position", -1)
            print("Calibrating...")
            ut.WriteAndRead(server, name, "C",verbose=True)
            time.sleep(1)
            if position ==0:
                print("Checking pos...")
                final_pos=ut.WriteAndRead(server, name, "G",verbose=True)
                if position==float(final_pos[0][-5:]):
                    print(f"Position set correclty at: {position}")
                    ut.log(f"Position set correclty at: {position}",self.log_path)
                    self.client.msg(f"Position set correclty at: {position}", is_error=False)
                    self.client.odb_set("/Configurations/SourceState/source_position", hole)
                else:
                    ut.log(f"Error moving the source to position {position}: Actual Position is {final_pos}",self.log_path)
                    self.client.msg(f"Error moving the source to position {position}: Actual Position is {final_pos}", is_error=False)
            else:
                print("Asking pos...")
                ut.WriteAndRead(server, name, "P",verbose=True)
                time.sleep(2)
                print("Setting pos...")
                ut.WriteAndRead(server, name, str(position),verbose=True)
                time.sleep(1)
                print("Checking pos...")
                final_pos=ut.WriteAndRead(server, name, "G",verbose=True)
                #print(final_pos[0])
                if position==self.extract_number_from_string(final_pos[0]):
                    print(f"Position set correclty at: {position}")
                    ut.log(f"Position set correclty at: {position}",self.log_path)
                    self.client.msg(f"Position set correclty at: {position}", is_error=False)
                    self.client.odb_set("/Configurations/SourceState/source_position", hole)
                else:
                    print(f"Error moving the source to position {position}: Actual Position is {final_pos}")
                    ut.log(f"Error moving the source to position {position}: Actual Position is {final_pos}",self.log_path)
                    self.client.msg(f"Error moving the source to position {position}: Actual Position is {final_pos}", is_error=False)
        except Exception as e:
            ut.log(f"Error interacting with {name}: {e}",self.log_path)
            self.client.msg(f"Error interacting with {name}: {e}", is_error=True)

    def readout_func(self):
        """
        For a periodic equipment, this function will be called periodically
        (every 100ms in this case). It should return either a `cdms.event.Event`
        or None (if we shouldn't write an event).
        """
        while self.client.odb_get("/Equipment/MANGOSensors/Settings/SerialBusy"):
            time.sleep(1)

        self.client.odb_set("/Equipment/MANGOSensors/Settings/SerialBusy", True)

        port = 8000
        server = ServerProxy(f"http://localhost:{port}")
        #name="KEG"
        #try:
        #    KEG_env=ut.WriteAndRead(server, name, "R",verbose = False)[0]
        #    time.sleep(1)
        #except Exception as e:
        #    self.client.msg(f"Error interacting with {name}: {e}", is_error=True)
        #    print(f"Error interacting with {name}: {e}")
            
            
        name="MANGOlino"
        try:
            MANGO_env=ut.WriteAndRead(server, name, "R",verbose = False)[0]
            time.sleep(1)
        except Exception as e:
            self.client.msg(f"Error interacting with {name}: {e}", is_error=True)
            print(f"Error interacting with {name}: {e}")
            
        #KEG_env_vars = KEG_env.split(";")
        #KEG_dict = {}
        #KEG_dict["Temp"] = float(KEG_env_vars[0])-273.15
        #KEG_dict["Pres"] = float(KEG_env_vars[1])/100.
        #KEG_dict["Humi"] = float(KEG_env_vars[2])
        #KEG_dict["Posi"] = float(source_pos)
        #print(KEG_dict)
        
        MANGO_env_vars = MANGO_env.split(";")
        MANGO_dict = {}
        MANGO_dict["Temp"] = float(MANGO_env_vars[0])-273.15
        MANGO_dict["Pres"] = float(MANGO_env_vars[1])/100.
        MANGO_dict["Humi"] = float(MANGO_env_vars[2])
        #print(MANGO_dict)
       
        #self.client.odb_set("/Equipment/MANGOSensors/Variables/KEG_temp",     KEG_dict["Temp"])
        #self.client.odb_set("/Equipment/MANGOSensors/Variables/KEG_pressure", KEG_dict["Pres"])
        #self.client.odb_set("/Equipment/MANGOSensors/Variables/KEG_humidity", KEG_dict["Humi"])
        
        
        self.client.odb_set("/Equipment/MANGOSensors/Variables/MANGOlino_temp",     MANGO_dict["Temp"])
        self.client.odb_set("/Equipment/MANGOSensors/Variables/MANGOlino_pressure", MANGO_dict["Pres"])
        self.client.odb_set("/Equipment/MANGOSensors/Variables/MANGOlino_humidity", MANGO_dict["Humi"])
        
        self.client.odb_set("/Equipment/MANGOSensors/Settings/SerialBusy", False)

        if self.client.odb_get("/Configurations/StepperMotor/buttonPressed"):
            while self.client.odb_get("/Equipment/MANGOSensors/Settings/SerialBusy"):
                time.sleep(1)
            self.client.odb_set("/Equipment/MANGOSensors/Settings/SerialBusy", True)

            #self.setSource(port, server, "KEG")

            self.client.odb_set("/Configurations/StepperMotor/buttonPressed", False)
            self.client.odb_set("/Equipment/MANGOSensors/Settings/SerialBusy", False)

            time.sleep(5)

        return None

class PythonFrontend(midas.frontend.FrontendBase):
    """
    A frontend contains a collection of equipment.
    You can access self.client to access the ODB etc (see `midas.client.MidasClient`).
    """
    def __init__(self):
        # You must call __init__ from the base class.
        midas.frontend.FrontendBase.__init__(self, "MANGOSC")
        
        # You can add equipment at any time before you call `run()`, but doing
        # it in __init__() seems logical.
        self.add_equipment(DAQServerEquipment(self.client))
        self.add_equipment(MANGOSensorsEquipment(self.client))
        
    def begin_of_run(self, run_number):
        """
        This function will be called at the beginning of the run.
        You don't have to define it, but you probably should.
        You can access individual equipment classes through the `self.equipment`
        dict if needed.
        """
        self.set_all_equipment_status("Running", "greenLight")
        #self.client.msg("Frontend has seen start of run number %d" % run_number)
        return midas.status_codes["SUCCESS"]
        
    def end_of_run(self, run_number):
        self.set_all_equipment_status("Finished", "greenLight")
        #self.client.msg("Frontend has seen end of run number %d" % run_number)
        return midas.status_codes["SUCCESS"]
    
    def frontend_exit(self):
        pass
        
        
if __name__ == "__main__":
    # The main executable is very simple - just create the frontend object,
    # and call run() on it.
    with PythonFrontend() as python_fe:
        python_fe.run()
