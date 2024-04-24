import json
data = {
    "properties": [
        {"HeadPosition": {"x": 13.1, "y":15.7, "z": 26.24987429}},
        {"HeadRotation": {"x": 15.5348, "y": 45.4589, "z":359.99999999999}}
    ]
}
serialized_data = json.dumps(data)
print("Data size:", len(serialized_data.encode('utf-8')), "bytes")