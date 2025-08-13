# Data Control Center

## Introduction

The **Data Control Center** is a GUI-based application that serves as a bridge between UDP data reception and LSL (Lab Streaming Layer) data streaming. It provides real-time monitoring and forwarding capabilities for three types of data: Vector3 (3D coordinates), Float values, and Event markers.

The application receives UDP packets containing JSON data, displays them in an intuitive graphical interface, and can forward the data as LSL streams for consumption by other applications or analysis tools.

## Key Features

- **Multi-port UDP listening** for different data types
- **Real-time data visualization** in organized tables
- **LSL stream forwarding** with configurable sampling rates
- **Start/stop controls** for both UDP reception and LSL streaming
- **Event handling** with special processing for specific event types
- **Configuration persistence** across sessions

## Dependencies

### Required Python Packages

Before running the Data Control Center, ensure you have the following dependencies installed:

```bash
pip install pylsl tkinter
```

**Note:** `tkinter` comes pre-installed with most Python distributions, but if you encounter import errors, you may need to install it separately.

### System Requirements

- **Python 3.6+**
- **LSL library** (pylsl package)
- **Network access** for UDP communication
- **Operating System:** Windows, macOS, or Linux

## Installation and Setup

1. **Clone or download** the repository containing the Data Control Center files
2. **Install dependencies:**
   ```bash
   pip install pylsl
   ```
3. **Navigate** to the UDP_Receiver directory
4. **Run the application:**
   ```bash
   python data_control_center.py
   ```

## Configuration

### Default Port Configuration

The Data Control Center listens on the following UDP ports by default:

- **Port 8081:** Vector3 data (3D coordinates)
- **Port 8082:** Float data (numeric values)
- **Port 8083:** Event data (string markers/events)

### Configuration File

The application creates and uses a `config.ini` file to store settings. This file is automatically created on first run and saved when the application closes.

### LSL Sampling Rate

You can configure the LSL output sampling rate through the GUI:
- Default: **10 samples/second**
- Range: Any positive numeric value
- Location: "Samples/second" input field in the LSL Output section

## User Interface

### Main Window Layout

The Data Control Center features a two-column layout:

#### Left Column: UDP Input
- **Start/Stop UDP Listening** button (red when stopped, green when active)
- **Vector3 Data Table:** Shows real-time 3D coordinate data
- **Float Data Table:** Displays numeric values
- **Event Data Table:** Lists event markers and their values

#### Right Column: LSL Output
- **Samples/second input field:** Configure LSL streaming rate
- **Start/Stop LSL Streams** button (red when stopped, green when active)

### Button States and Visual Feedback

- **Red buttons:** Service is stopped
- **Green buttons:** Service is active
- **Flashing green:** Indicates active streaming/listening
- **Data tables:** Auto-update every 50ms when UDP listening is active

## UDP Data Formats

The Data Control Center expects UDP packets with the following structure:

### Packet Structure
1. **Header:** 4 bytes containing the UTF-8 text size (big-endian unsigned integer)
2. **Payload:** UTF-8 encoded JSON string

### JSON Data Formats

#### Vector3 Data Format
**Port:** 8081
```json
{
    "vector3": {
        "user_head_position": {
            "x": -197.7,
            "y": 197.78,
            "z": 297.4
        },
        "user_head_rotation": {
            "x": 79.63,
            "y": 79.63,
            "z": 79.65
        }
    }
}
```

**Requirements:**
- Root key must be `"vector3"`
- Each vector must contain `"x"`, `"y"`, and `"z"` numeric values
- Multiple vectors can be included in a single packet

#### Float Data Format
**Port:** 8082
```json
{
    "float": {
        "float_1": 0.123,
        "float_2": 0.456
    }
}
```

**Requirements:**
- Root key must be `"float"`
- Values must be numeric (integers or floats)
- Multiple float values can be included in a single packet

#### Event Data Format
**Port:** 8083
```json
{
    "event": {
        "event_key_1": "value for this event key 1",
        "event_key_2": "value for this event key 2"
    }
}
```

**Requirements:**
- Root key must be `"event"`
- Values are typically strings but can be any JSON-serializable type
- Multiple events can be included in a single packet

### Special Event Handling

The application provides special processing for certain event keys:

- **`provant_id`:** Stored as a global variable with timestamp
- **`level_title`:** Stored as a global variable
- **All events:** Automatically removed after processing to prevent re-transmission

## Usage Workflow

### Basic Operation

1. **Start the application:** Run `python data_control_center.py`
2. **Configure LSL sampling rate** (optional): Enter desired samples/second
3. **Start UDP listening:** Click "Start UDP Listening" button
4. **Send UDP data:** Begin transmitting data to the configured ports
5. **Monitor data:** View real-time data in the GUI tables
6. **Start LSL streaming** (optional): Click "Start LSL Streams" to forward data
7. **Stop services:** Use the respective stop buttons when finished

### LSL Stream Output

When LSL streaming is active, the application creates the following stream types:

- **Vector3 streams:** One stream per vector name (3 channels: x, y, z)
- **Float streams:** One stream per float name (1 channel)
- **Event marker stream:** Single stream for all events (2 string channels)

### Data Persistence

- **Vector3 and Float data:** Continuously updated (latest values displayed)
- **Event data:** Consumed after processing (prevents duplication)
- **Configuration:** Automatically saved on application close

## Troubleshooting

### Common Issues

1. **Import Error for pylsl:**
   ```bash
   pip install pylsl
   ```

2. **Port already in use:**
   - Check if another application is using ports 8081-8083
   - Modify port configuration if needed

3. **JSON parsing errors:**
   - Verify UDP packet format matches expected structure
   - Check that JSON is valid and properly formatted

4. **No data appearing:**
   - Ensure UDP packets are being sent to correct ports
   - Verify JSON structure matches required format
   - Check network connectivity and firewall settings

### Debug Information

The application provides console output for:
- Listener start/stop status
- JSON parsing errors with detailed error messages
- Packet rate information (when uncommented in code)

## Advanced Configuration

### Modifying Default Ports

To change the default UDP ports, modify the port numbers in the `start_stop_udp_listening()` method:

```python
self.listener.start_listener("Vector3", 8081)  # Change 8081 to desired port
self.listener.start_listener("Float", 8082)    # Change 8082 to desired port
self.listener.start_listener("Event", 8083)    # Change 8083 to desired port
```

### Extending Functionality

The modular design allows for easy extension:
- **New data types:** Add processing methods in `udp_data_handler.py`
- **Additional LSL streams:** Extend `lsl_streams_handler.py`
- **Custom event processing:** Modify event handling in `data_control_center.py`

## File Structure

```
UDP_Receiver/
├── data_control_center.py          # Main GUI application
├── udp_data_handler.py             # UDP packet reception and processing
├── lsl_streams_handler.py          # LSL stream management
├── vector3_list_packet_example.json # Example Vector3 packet
├── float_list_packet_example.json   # Example Float packet
├── event_list_packet_example.json   # Example Event packet
└── config.ini                      # Auto-generated configuration file
```
