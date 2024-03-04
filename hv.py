#!/usr/bin/python3

from pycaenhv.wrappers import init_system, deinit_system, get_board_parameters, get_crate_map, get_channel_parameters,get_channel_parameter, list_commands,get_channel_parameter_property,get_channel_name,set_channel_parameter
from pycaenhv.enums import CAENHV_SYSTEM_TYPE, LinkType
from pycaenhv.errors import CAENHVError

class Board:

    def __init__(self, host):
        self.host = host
        system_type = CAENHV_SYSTEM_TYPE["N1470"]
        link_type = LinkType["USB_VCP"]
        self.handle = init_system(system_type, link_type, self.host)
        #print(f"Connected to board with handle {self.handle}")

    @property
    def crate_map(self):
        return get_crate_map(self.handle)

    @property
    def parameters(self):
        return get_board_parameters(self.handle, 0)

    def get_channel_parameters(self, ch):
        return get_channel_parameters(self.handle, 0, ch)

    def get_channel_value(self, ch, parameter_name):
        return get_channel_parameter(self.handle, 0, ch, parameter_name)

    def get_voltage(self, electrode):
        return self.get_channel_value(electrode, "VMon")

    def get_current(self, electrode):
        return self.get_channel_value(electrode, "I0Mon")

    def get_status(self, electrode):
        return self.get_channel_value(electrode, "Status")

    def set_channel_value(self, electrode, parameter_name, value):
        set_channel_parameter(self.handle, 0, electrode, parameter_name, value)

    def set_voltage(self, electrode, voltage):
        self.set_channel_value(electrode, "VSet", voltage)

    def set_current(self, electrode, voltage):
        self.set_channel_value(electrode, "ISet", voltage)

