import json
import math
import socket
import threading
from datetime import datetime
import time
from tkinter import Tk, Label, Button, Entry, StringVar, Frame, IntVar, Checkbutton, Scrollbar, BooleanVar

from pylsl import StreamInfo, StreamOutlet, local_clock, pylsl


#UDP clock rx functions

def receive_udp_clock():
    global running_udp_clock
    global time_received
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((udp_clock_ip_var.get(), int(ucp_clock_port_var.get())))
        try:
            while running_udp_clock:
                clock_data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
                time_received = clock_data.decode()
                udp_clock_rx_time_label.config(text=time_received)
        except Exception as e:
            print(f"Error: {e}")

def click_on_start_listening_udp_clock():
    global running_udp_clock
    running_udp_clock = True
    udp_clock_rx_time_label.config(highlightbackground='green', highlightcolor='green')  # Set border color to green
    udp_clock_rx_start_button.config(state="disabled")
    udp_clock_rx_stop_button.config(state="normal")
    thread = threading.Thread(target=receive_udp_clock)
    thread.daemon = True
    thread.start()

def click_on_stop_listening_udp_clock():
    global running_udp_clock
    running_udp_clock = False
    udp_clock_rx_time_label.config(highlightbackground='red', highlightcolor='red')  # Set border color to green
    udp_clock_rx_stop_button.config(state="disabled")
    udp_clock_rx_start_button.config(state="normal")


#UDP data rx functions
def receive_udp_data():
    global running_udp_data
    global udp_data_rx_properties
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((udp_data_rx_ip_var.get(), int(udp_data_rx_port_var.get())))
        try:
            while running_udp_data:
                message, _ = sock.recvfrom(1024)
                data = json.loads(message.decode())
                #update main data
                udp_data_rx_properties = data["properties"]
                # Update the UI
                update_ui_udp_data(data["properties"])

        except Exception as e:
            print(f"Error: {e}")

def click_on_start_receiving_udp_data():
    global running_udp_data
    running_udp_data = True
    udp_data_rx_frame.config(highlightbackground='green', highlightcolor='green')
    udp_data_rx_start_button.config(state="disabled")
    udp_data_rx_stop_button.config(state="normal")
    thread = threading.Thread(target=receive_udp_data)
    thread.daemon = True
    thread.start()


def click_on_stop_receiving_udp_data():
    global running_udp_data
    running_udp_data = False
    udp_data_rx_frame.config(highlightbackground='red', highlightcolor='green')
    udp_data_rx_stop_button.config(state="disabled")
    udp_data_rx_start_button.config(state="normal")


def update_ui_udp_data(properties):
    for row_index, prop in enumerate(properties):
        keys = list(prop.keys())
        propertyName = keys[0]
        udp_data_rx_label_list[row_index][1].config(text=str(prop[propertyName]["x"]))  # Update X label
        udp_data_rx_label_list[row_index][2].config(text=str(prop[propertyName]["y"]))  # Update Y label
        udp_data_rx_label_list[row_index][3].config(text=str(prop[propertyName]["z"]))  # Update Z label


#LSL functions
def create_lsl_streams():
    global lsl_samples_var
    global udp_data_rx_properties
    for prop in udp_data_rx_properties:
        print("creating stream...")
        property_name = list(prop.keys())[0]
        print(" ->stream: " +property_name)
        stream_info = StreamInfo(name=f'UDP_{property_name}', type='3D Positional Data', channel_count=3, nominal_srate=(1.0*lsl_samples_var.get()), channel_format='float32', source_id=f'unique_id_{property_name}')
        outlet = StreamOutlet(stream_info)
        stream_outlets[property_name] = outlet

        # Set up display for stream data
        if property_name not in lsl_data_labels:
            row = len(lsl_data_labels) + 1
            label = Label(lsl_data_display_frame, text=f"{property_name}: x=0, y=0, z=0", font=("Helvetica", 8),width=50)
            label.grid(row=row, column=0, sticky="w")
            lsl_data_labels[property_name] = label

        # Start a thread for each outlet to push data
        threading.Thread(target=push_data, args=(property_name,), daemon=True).start()

def push_data(property_name):
    global lsl_samples_var
    global udp_data_rx_properties
    print("pushing "+property_name)
    outlet_info = stream_outlets.get(property_name)
    if not outlet_info:
        print(f"No outlet for {property_name}")
        return
    while running_lsl_stream:
        # Find the correct dictionary containing the property_name
        property_dict = next((prop for prop in udp_data_rx_properties if property_name in prop), None)
        if property_dict:
            data = [
                property_dict[property_name]["x"],
                property_dict[property_name]["y"],
                property_dict[property_name]["z"]
            ]
            #TODO find the right conversion between udp clock and local_clock from lsl
            #Check what is excactly local_clock
            stamp = local_clock() - 0.125
            #TODO One option for sure is to add an offset to the local clock
            stamp = local_clock() - 0.125
            #TODO and then do outlet.push_sample(mysample, stamp)
            #TODO another option is to change the local clock of this machine based on the udp clock received
            if send_timecode_var.get():
                #user wants to attach time sync with the stream
                if False:
                #if running_udp_clock:
                    #grab timestamp from udp clock
                    current_datetime = datetime.datetime.now()
                    timestamp = pylsl.local_clock()
                else:
                    outlet_info.push_sample(data, local_clock())
            else:
                #option with no timestamp
                outlet_info.push_sample(data)

            # Update the GUI
            lsl_data_labels[property_name].config(text=f"{property_name}: x={data[0]}, y={data[1]}, z={data[2]}")
        else:
            print(f"{property_name} not found in properties")
        time.sleep(1.0 / lsl_samples_var.get())

def click_on_start_lsl_streams():
    global running_lsl_stream
    running_lsl_stream = True
    lsl_data_display_frame.config(highlightbackground='green', highlightcolor='green')
    lsl_start_button.config(state="disabled")
    lsl_stop_button.config(state="normal")
    create_lsl_streams()
def click_on_stop_lsl_streams():
    global running_lsl_stream
    running_lsl_stream = False
    lsl_data_display_frame.config(highlightbackground='red', highlightcolor='red')
    lsl_stop_button.config(state="disabled")
    lsl_start_button.config(state="normal")


# Main UI
root = Tk()
root.title("UDP to LSL")
root.minsize(300, 300)

# UDP RX Clock part
running_udp_clock: bool = False
time_received = time.time()
udp_clock_rx_title_Label = Label(root, text="UDP Clock Receiver", font=('Helvetica', 18))
udp_clock_rx_title_Label.pack(pady=5)

udp_clock_rx_time_label = Label(root, text="", font=("Helvetica", 12),borderwidth=2,relief="solid", padx=5,pady=5,highlightthickness=2,highlightbackground='red', highlightcolor='red')
udp_clock_rx_time_label.pack(pady=5)

now = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
udp_clock_rx_time_label.config(text=now)

udp_clock_ip_var = StringVar(value="127.0.0.1")
ucp_clock_port_var = StringVar(value="5005")

udp_clock_rx_ip_frame = Frame(root)
udp_clock_rx_ip_frame.pack(pady=5)

udp_clock_rx_ip_entry = Entry(udp_clock_rx_ip_frame, textvariable=udp_clock_ip_var, font=("Helvetica", 12),width=15)
udp_clock_rx_ip_entry.pack(side="left", ipady=2)

udp_clock_rx_port_entry = Entry(udp_clock_rx_ip_frame, textvariable=ucp_clock_port_var, font=("Helvetica", 12),width=8)
udp_clock_rx_port_entry.pack(side="left", ipady=2)

udp_clock_rx_button_frame = Frame(root)
udp_clock_rx_button_frame.pack(pady=10)

udp_clock_rx_start_button = Button(udp_clock_rx_button_frame, text="Start Listening UDP clock", command=click_on_start_listening_udp_clock, state="normal")
udp_clock_rx_start_button.pack(side="left", padx=5, ipady=20)  # Pack button on the left side of its frame

udp_clock_rx_stop_button = Button(udp_clock_rx_button_frame, text="Stop Listening UDP clock", command=click_on_stop_listening_udp_clock, state="disabled")
udp_clock_rx_stop_button.pack(side="left", padx=5, ipady=20)  # Pack button on the left side of its frame

# UDP DATA UI part

udp_data_rx_title_Label = Label(root, text="UDP Data Receiver", font=('Helvetica', 18))
udp_data_rx_title_Label.pack(pady=5)

udp_data_rx_frame = Frame(root,borderwidth=2,relief="solid",padx=5,pady=5,highlightthickness=2,highlightbackground='red', highlightcolor='red')
udp_data_rx_frame.pack(padx=10, pady=10)

udp_data_rx_headers = ["Property Name", "X", "Y", "Z"]
for i, header in enumerate(udp_data_rx_headers):
    Label(udp_data_rx_frame, text=header, font=('Helvetica', 10, 'bold'), borderwidth=0, relief='groove').grid(row=0,
                                                                                                               column=i)

udp_data_rx_label_list = []  # List to store label references for updating
udp_data_rx_properties = [{"HeadPosition": {"x": 0, "y": 0, "z": 0}}, {"HeadRotation": {"x": 0, "y": 0, "z": 0}}]
for row_index, prop in enumerate(udp_data_rx_properties):
    row_labels = []
    keys = list(prop.keys())
    propertyName = keys[0]
    row_labels.append(Label(udp_data_rx_frame, text=propertyName, borderwidth=0, relief='groove'))
    row_labels[0].grid(row=row_index + 1, column=0)
    for i in range(3):
        lab = Label(udp_data_rx_frame, text=prop[propertyName][["x", "y", "z"][i]], borderwidth=0, relief='groove',
                    width=12)
        lab.grid(row=row_index + 1, column=i + 1)
        row_labels.append(lab)
    udp_data_rx_label_list.append(row_labels)

udp_data_rx_ip_var = StringVar(value="127.0.0.1")
udp_data_rx_port_var = StringVar(value="5006")

udp_data_rx_ip_frame = Frame(root)
udp_data_rx_ip_frame.pack(pady=5)

udp_data_rx_ip_entry = Entry(udp_data_rx_ip_frame, textvariable=udp_data_rx_ip_var, font=("Helvetica", 12), width=15)
udp_data_rx_ip_entry.pack(side="left", ipady=2)

udp_data_rx_port_entry = Entry(udp_data_rx_ip_frame, textvariable=udp_data_rx_port_var, font=("Helvetica", 12), width=8)
udp_data_rx_port_entry.pack(side="left", ipady=2)

udp_data_rx_button_frame = Frame(root)
udp_data_rx_button_frame.pack(pady=10)

udp_data_rx_start_button = Button(udp_data_rx_button_frame, text="Start listening UDP data", command=click_on_start_receiving_udp_data,
                                  state="normal")
udp_data_rx_start_button.pack(side="left", padx=5, ipady=20)

udp_data_rx_stop_button = Button(udp_data_rx_button_frame, text="Stop listening UDP data", command=click_on_stop_receiving_udp_data,
                                 state="disabled")
udp_data_rx_stop_button.pack(side="left", padx=5, ipady=20)

#LSL streams

stream_outlets = {}

lsl_tx_title_Label = Label(root, text="UDP to LSL", font=('Helvetica', 18))
lsl_tx_title_Label.pack(pady=5)

lsl_data_display_frame = Frame(root, borderwidth=2, relief="solid", padx=5, pady=5, highlightthickness=2)
lsl_data_display_frame.pack(padx=10, pady=10)

lsl_data_labels = {}

send_timecode_var = BooleanVar(value=False)
send_timecode_checkbox = Checkbutton(root, text="Send Timecode", variable=send_timecode_var, onvalue=True, offvalue=False, font=('Helvetica', 12))
send_timecode_checkbox.pack(padx=10, pady=10)

lsl_ui_frame = Frame(root)
lsl_ui_frame.pack(padx=10, pady=10)

lsl_samples_label = Label(lsl_ui_frame, text="Samples per second:", font=('Helvetica', 12))
lsl_samples_label.pack(side="left", padx=5)

lsl_samples_var = IntVar(value=18)
lsl_samples_entry = Entry(lsl_ui_frame, textvariable=lsl_samples_var, font=("Helvetica", 12), width=5)
lsl_samples_entry.pack(side="left", padx=5)

lsl_button_frame = Frame(root)
lsl_button_frame.pack(pady=10)

lsl_start_button = Button(lsl_button_frame, text="Start LSL Stream", command=click_on_start_lsl_streams, state="normal")
lsl_start_button.pack(side="left", padx=5, ipady=20)

lsl_stop_button = Button(lsl_button_frame, text="Stop LSL Stream", command=click_on_stop_lsl_streams, state="disabled")
lsl_stop_button.pack(side="left", padx=5, ipady=20)

#info
hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname)

your_local_ip = Label(root, text="your local ip: "+IPAddr, font=("Helvetica", 8))
your_local_ip.pack(pady=10)
your_local_ip.pack(ipady=20)

root.mainloop()
