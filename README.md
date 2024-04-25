# NetworkCommunication

This repository contains a series of scripts to help to move data between different pieces of software using python and UDP packages.

Scripts are right now in development and are ment to be edited and adapted to your needs, so expect changes, additions or missing things bits on this documentation.

Data UDP format it will change depending on the requirements, by now you can find the initial json_schema and a json file example.

## Dependencies

Depends on the script, i.e. UDP_2_LSL requires LSL library already installed in your system, you can install it with brew,pip or others depending on your os

## Broadcasting/Multicasting/EndToEnd

While is possible to broadcast and multicast udp packages in the network, network capacity can become easily flooded with data (even in a fast Local network).
Communication success it will depend then on the weakest network device (computer(headset/mobile/...) and not only the main router/switch offering the net architecture.
Recommendation is to point the transmitters to target the IP address of the receivers. In that case receivers doesn't need to point to the transmitters, you can leave the address field empty and click in listen/receive.

## UDPClockTx.py

This is a basic script to send constantly the system time to a UDP port

![image](https://github.com/JuanObiJuan/NetworkCommunication/assets/1729541/39744ce0-fdf9-4a7d-8946-37ff6fe53be8)

You can configure the ip and port and start ot stop the transmission

## UDPClockRx.py

This cript is able to connect to a UDP port and listen for a clock data

![image](https://github.com/JuanObiJuan/NetworkCommunication/assets/1729541/49ea61d0-19d2-465e-a9a6-5a3e9ba39aa2)

You can configure the ip and port and start ot stop listening

## UE_Emulator.py

This script emulates a constant flow of data to a UDP port. The data structure is following the json schema provided.

![image](https://github.com/JuanObiJuan/NetworkCommunication/assets/1729541/ed21329f-24a4-4346-b663-b22a60419552)

You can configure ports, ip address.

You can also modify on the fly the sampling ratio with the slider from 1 sample per second to 100, this emulates the changing nature of the samples of Unreal Engine (frames per second).

## UDP_2_LSL.py

This script combines three tasks:
- receives an UDP clock
- receives positional data from UDP (UE)
- Stream one LSL stream per property found in the positional data.

