# NetworkCommunication

This repository contains a series of scripts to help to move data between different softwares using python and UDP packages.

Data UDP format it will change depending on the requirement, by now you can find the initial json_schema and an example.

## UDPClockTx.py

This is a basic script to send constantly the system time to a UDP port

![image](https://github.com/JuanObiJuan/NetworkCommunication/assets/1729541/39744ce0-fdf9-4a7d-8946-37ff6fe53be8)

You can configure the ip and port and start ot stop the transmission

## UDPClockRx.py

This cript is able to connect to a UDP port and listen for a clock data

![image](https://github.com/JuanObiJuan/NetworkCommunication/assets/1729541/49ea61d0-19d2-465e-a9a6-5a3e9ba39aa2)

You can configure the ip and port and start ot stop listening

##UE_Emulator.py

This script emulates a constant flow of data to a UDP port. The data structure is following the json schema provided.

![image](https://github.com/JuanObiJuan/NetworkCommunication/assets/1729541/8db2161e-e545-430e-aa4d-0b88c7a69adf)

You can configure ports, ip address.
You can also modify on the fly the sampling ratio with the slider from 1 sample per second to 100, this emulates the changing nature of the samples of Unreal Engine (frames per second).

##UDP_2_LSL.py

This script combines three tasks:
- receives an UDP clock
- receives positional data from UDP (UE)
- Stream one LSL stream per property found in the positonal data.

