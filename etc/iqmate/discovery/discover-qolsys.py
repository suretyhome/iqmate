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
        flows.append(mttq_in_node(payload["name"], payload["state_topic"], payload))
    if len(topic) >= 5 and topic[1] == "alarm_control_panel" and topic[4] == "config":
        payload = json.loads(msg.payload)
        command_template = json.loads(payload["command_template"])
        session = command_template["session_token"]
        flows.append(mttq_in_node("IQ Panel Armed", payload["state_topic"], payload))
        flows.append(mttq_out_node("IQ Panel", "See IQ Panel Arm State info"))
        flows.append(panel_command_node("Arm Stay", payload["command_topic"], panel_command("ARM_HOME", session, {
            "bypass": True,
            "delay": 0,
        })))
        flows.append(panel_command_node("Arm Away", payload["command_topic"], panel_command("ARM_AWAY", session, {
            "bypass": True,
            "delay": 0,
        })))
        flows.append(panel_command_node("Disarm", payload["command_topic"], panel_command("DISARM", session, {})))
        flows.append(panel_command_node("Police Panic", payload["command_topic"], panel_command("TRIGGER_POLICE", session, {})))
        flows.append(panel_command_node("Fire Panic", payload["command_topic"], panel_command("TRIGGER_FIRE", session, {})))
        flows.append(panel_command_node("Medical Panic", payload["command_topic"], panel_command("TRIGGER_AUXILIARY", session, {})))

def panel_command(action, session, extra):
    extra["partition_id"] = "0"
    extra["action"] = action
    extra["session_token"] = session
    return extra

def panel_command_node(name, topic, command):
    return {
        "id": os.urandom(8).hex(),
        "type": "change",
        "name": name,
        "rules": [
            {
                "t": "set",
                "p": "topic",
                "pt": "msg",
                "to": topic,
                "tot": "str"
            },
            {
                "t": "set",
                "p": "payload",
                "pt": "msg",
                "to": json.dumps(command, indent=4),
                "tot": "json"
            },
            {
                "t": "set",
                "p": "payload.code",
                "pt": "msg",
                "to": "${IQ Panel User Code}",
                "tot": "env"
            }
        ],
        "action": "",
        "property": "",
        "from": "",
        "to": "",
        "reg": False,
        "wires": [
            []
        ]

    }

def mttq_out_node(name, config):
    return {
        "id": os.urandom(8).hex(),
        "type": "mqtt out",
        "name": name,
        "topic": "",
        "qos": "2",
        "retain": "",
        "respTopic": "",
        "contentType": "application/json",
        "userProps": "",
        "correl": "",
        "expiry": "",
        "broker": "fbbfa7873cd57aa5",
        "wires": [],
        "info": json.dumps(config, indent=4)
    }

def mttq_in_node(name, topic, config):
    return {
        "id": os.urandom(8).hex(),
        "type": "mqtt in",
        "name": name,
        "topic": topic,
        "qos": "2",
        "datatype": "auto-detect",
        "broker": "fbbfa7873cd57aa5",
        "nl": False,
        "rap": True,
        "rh": 0,
        "inputs": 0,
        "wires": [
            []
        ],
        "info": json.dumps(config, indent=4)
    }

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
    {
        "id": os.urandom(8).hex(),
        "type": "global-config",
        "name": "global-config",
        "env": [
            {
                "name": "IQ Panel User Code",
                "value": "",
                "type": "str"
            }
        ]
    }
]

def layout_nodes(flows):
    offset = 60
    inputs = 0
    commands = 0
    outputs = 0
    for i, _ in enumerate(flows):
        node = flows[i]
        if node["type"] in ["mqtt in"]:
            inputs += 1
            node["x"] = 120
            node["y"] = inputs * offset
            node["z"] = "db0d03662baee2f8"
        if node["type"] in ["change"]:
            commands += 1
            node["x"] = 320
            node["y"] = commands * offset
            node["z"] = "db0d03662baee2f8"
        if node["type"] in ["mqtt out"]:
            outputs += 1
            node["x"] = 520
            node["y"] = outputs * offset
            node["z"] = "db0d03662baee2f8"

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, userdata=flows)
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.connect("localhost", 1883, 60)
mqttc.loop_start()
time.sleep(4)
mqttc.loop_stop()

layout_nodes(flows)
with open('flows.json', 'w') as f:
    json.dump(flows, f, ensure_ascii=False, indent=4)
