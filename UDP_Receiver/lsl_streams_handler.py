from pylsl import StreamInfo, StreamOutlet, local_clock
import threading
import time

class LSLStreamHandler:

    def __init__(self):
        # Initialize the streams dictionary to keep track of active streams
        self.streams = {}

    def create_vector3_stream(self, name, stream_type, channel_id, sampling_rate):
        info = StreamInfo(name, stream_type, 3, sampling_rate, 'float32', channel_id)
        outlet = StreamOutlet(info)
        self.streams[channel_id] = {
            "outlet": outlet,
            "type": "vector3",
            "active": True,
        }

    def create_float_stream(self, name, stream_type, channel_id, sampling_rate):
        info = StreamInfo(name, stream_type, 1, sampling_rate, 'float32', channel_id)
        outlet = StreamOutlet(info)
        self.streams[channel_id] = {
            "outlet": outlet,
            "type": "float",
            "active": True,
        }

    def create_marker_stream(self, name, stream_type, channel_id):
        # Marker stream with 2 string channels
        info = StreamInfo(name, stream_type, 2, 0, 'string', channel_id)
        outlet = StreamOutlet(info)
        self.streams[channel_id] = {
            "outlet": outlet,
            "type": "marker",
            "active": True,
        }
   
    def push_vector_data(self, channel_id, x, y, z):
        if channel_id in self.streams and self.streams[channel_id]["type"] == "vector3":
            outlet = self.streams[channel_id]["outlet"]
            outlet.push_sample([x, y, z], local_clock())

    def push_float_data(self, channel_id, value):
        if channel_id in self.streams and self.streams[channel_id]["type"] == "float":
            outlet = self.streams[channel_id]["outlet"]
            outlet.push_sample([value], local_clock())

    def push_marker_data(self, channel_id, key, value):
        if channel_id in self.streams and self.streams[channel_id]["type"] == "marker":
            outlet = self.streams[channel_id]["outlet"]
            outlet.push_sample( [key,value], local_clock())

    def stop_stream(self, channel_id):
        if channel_id in self.streams:
            self.streams[channel_id]["active"] = False
            if self.streams[channel_id]["thread"] and self.streams[channel_id]["thread"].is_alive():
                self.streams[channel_id]["thread"].join()
            del self.streams[channel_id]

    def stop_all_streams(self):
        for channel_id, stream in self.streams.items():
            stream["active"] = False
            # If there is a thread associated with the stream (e.g., a heartbeat thread), join it
            if stream.get("thread"):
                stream["thread"].join()

        # Clear the streams dictionary
        self.streams.clear()