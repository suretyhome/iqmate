#!/usr/bin/env python

import os
import time
import json
import random, string
import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, reason_code, properties):
    client.subscribe("qolsys/#")

def on_message(client, flows, msg):
    topic = msg.topic.split("/")
    if len(topic) >= 4 and topic[1] == "binary_sensor" and topic[3] == "config":
        payload = json.loads(msg.payload)
        add_node(flows, "mqtt in", payload["name"], payload["state_topic"], json.dumps(payload, indent=4))
    if len(topic) >= 5 and topic[1] == "alarm_control_panel" and topic[4] == "config":
        payload = json.loads(msg.payload)
        add_node(flows, "mqtt in", "Qolsys Panel", payload["state_topic"], json.dumps(payload, indent=4))

def add_node(flows, type, name, topic, info):
    flows.append({
        "id": os.urandom(8).hex(),
        "type": type,
        "z": "db0d03662baee2f8",
        "name": name,
        "topic": topic,
        "qos": "2",
        "datatype": "auto-detect",
        "broker": "fbbfa7873cd57aa5",
        "nl": False,
        "rap": True,
        "rh": 0,
        "inputs": 0,
        "x": 80,
        "y": 40 + 60 * (len(flows) - 2),
        "wires": [
            []
        ],
        "info": info
    })

flows = [
    {
        "id": "db0d03662baee2f8",
        "type": "tab",
        "label": "Qolsys",
        "disabled": False,
        "info": "",
        "env": []
    },
        {
        "id": "fbbfa7873cd57aa5",
        "type": "mqtt-broker",
        "name": "IQ Mate",
        "broker": "localhost",
        "port": "1883",
        "clientid": "",
        "autoConnect": True,
        "usetls": False,
        "protocolVersion": "5",
        "keepalive": "60",
        "cleansession": True,
        "autoUnsubscribe": True,
        "birthTopic": "",
        "birthQos": "0",
        "birthRetain": "false",
        "birthPayload": "",
        "birthMsg": {},
        "closeTopic": "",
        "closeQos": "0",
        "closeRetain": "false",
        "closePayload": "",
        "closeMsg": {},
        "willTopic": "",
        "willQos": "0",
        "willRetain": "false",
        "willPayload": "",
        "willMsg": {},
        "userProps": "",
        "sessionExpiry": ""
    },
]

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, userdata=flows)
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.connect("localhost", 1883, 60)
mqttc.loop_start()
time.sleep(4)
mqttc.loop_stop()

with open('flows.json', 'w') as f:
    json.dump(flows, f, ensure_ascii=False, indent=4)
