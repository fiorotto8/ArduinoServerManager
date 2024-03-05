# Handle multiple Serial Devices with one Server

A simpleRPC server is initialized by `rpcServer.py` where three instances are instantiated to manage the comunication with both the Arduinos and the CAEN N1570 borad.
- The class *ArduinoSerialWrapper* contains the functions exposed to the client that may be used to talk with the device through the server
`rpcClient_simpleArd.py` contains a simple example to write a single word to a selected Arduino
- The class *HvSerialWrapper* contains the functions exposed to the client that may be used to set and get parameters of HV channels
`rpcClient_simpleHV.py` contains a simple example to set voltage to certain channel

More examples are present that may be needed for datataking 

## Use of crontab
The program may be started with a cronjob as in the following example.
Open crontab:
-``crontab -e ``
install a cronjob:
- ``0 0 * * * python3 path_to_file/rpcServer.py >> path_to_logfile/log.txt 2>&1``
- ``59 23 * * * ps -axu | grep rpcServer.py | awk '{print $2}' | xargs kill -SIGINT``
The two rows written above allow the code to start every day at 00:00 and to kill the program sending a `SIGINT` signal every day at 23:59.
`2>&1` is used to write an error message in the log file if something in the cronjob doesn't work.
