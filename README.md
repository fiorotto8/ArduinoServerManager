# Handle multiple Serial Devices with one Server

A simpleRPC server is initialized by `rpcServer.py` where two instances are instantiated to manage the comunication with both the Arduinos.
The class *ArduinoSerialWrapper* contains the functions exposed to the client that may be used to talk with the device through the server
`rpcClient_simple.py` contains a simple example to write a single word to a selected Arduino