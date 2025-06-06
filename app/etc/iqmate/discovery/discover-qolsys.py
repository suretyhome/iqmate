#!/usr/bin/env python

import os
import time
import json
import random, string
import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, reason_code, properties):
    client.subscribe("qolsys/#")

iq_panel_online_since = None
iq_panel_devices_discovered = 0

def on_message(client, flows, msg):
    global iq_panel_online_since
    topic = msg.topic.split("/")
    if len(topic) >= 4 and topic[1] == "alarm_control_panel" and topic[2] == "qolsys_panel" and topic[3] == "availability":
        iq_panel_status = msg.payload.decode('utf-8')
        if iq_panel_status == "online":
            iq_panel_online_since = time.time()
            print("IQ Panel is " + iq_panel_status)
        elif iq_panel_status == "offline":
            iq_panel_online_since = 0
        else:
            print("IQ Panel is " + iq_panel_status)
    if len(topic) >= 4 and topic[1] == "binary_sensor" and topic[3] == "config":
        payload = json.loads(msg.payload)
        flows.append(mttq_in_node(payload["name"], payload["state_topic"], payload))
    if len(topic) >= 5 and topic[1] == "alarm_control_panel" and topic[4] == "config":
        payload = json.loads(msg.payload)
        command_template = json.loads(payload["command_template"])
        session = command_template["session_token"]
        flows.append(mttq_in_node("IQ Panel Status", payload["state_topic"], payload))
        iq_panel_command_node = mttq_out_node("IQ Panel Command", payload)
        flows.append(iq_panel_command_node)
        flows.append(panel_command_node("Arm Stay", payload["command_topic"], panel_command("ARM_HOME", session, {
            "bypass": True,
            "delay": 0,
        }), iq_panel_command_node))
        flows.append(panel_command_node("Arm Away", payload["command_topic"], panel_command("ARM_AWAY", session, {
            "bypass": True,
            "delay": 0,
        }), iq_panel_command_node))
        flows.append(panel_command_node("Disarm", payload["command_topic"], panel_command("DISARM", session, {}), iq_panel_command_node))
        flows.append(panel_command_node("Police Panic", payload["command_topic"], panel_command("TRIGGER_POLICE", session, {}), iq_panel_command_node))
        flows.append(panel_command_node("Fire Panic", payload["command_topic"], panel_command("TRIGGER_FIRE", session, {}), iq_panel_command_node))
        flows.append(panel_command_node("Medical Panic", payload["command_topic"], panel_command("TRIGGER_AUXILIARY", session, {}), iq_panel_command_node))

def panel_command(action, session, extra):
    extra["partition_id"] = "0"
    extra["action"] = action
    extra["session_token"] = session
    return extra

def panel_command_node(name, topic, command, command_node):
    global iq_panel_commands_group
    node = {
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
            [command_node['id']]
        ]
    }
    iq_panel_commands_group['nodes'].append(node['id'])
    return node

def mttq_out_node(name, config):
    global iq_panel_commands_group, mqtt_broker
    node = {
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
        "broker": mqtt_broker['id'],
        "wires": [],
        "info": json.dumps(config, indent=4)
    }
    iq_panel_commands_group['nodes'].append(node['id'])
    return node

def mttq_in_node(name, topic, config):
    global iq_panel_sensors_group, iq_panel_devices_discovered
    # Create a subflow instance instead of a MQTT in node
    node = {
        "id": os.urandom(8).hex(),
        "type": "subflow:258764906056d24a",  # Reference to the Qolsys Sensor subflow
        "name": name,
        "env": [
            {
                "name": "topic",
                "type": "str",
                "value": topic
            }
        ],
        "wires": [
            []
        ],
        "info": json.dumps(config, indent=4)
    }
    iq_panel_sensors_group['nodes'].append(node['id'])
    iq_panel_devices_discovered += 1
    print("Discovered " + name)
    return node

qolsys_nodes_tab = {
    "id": os.urandom(8).hex(),
    "type": "tab",
    "label": "Qolsys Nodes",
    "disabled": False,
    "info": "",
    "env": []
}

global_config = {
    "id": "12ecc27b2447ef53",
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

mqtt_broker = {
    "id": "9ff3a2541d0bc618",
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
}

iq_panel_sensors_group = {
    "id": os.urandom(8).hex(),
    "type": "group",
    "z": qolsys_nodes_tab['id'],
    "name": "IQ Panel Sensors",
    "style": {
        "label": True
    },
    "nodes": [],
    # "x": 34,
    # "y": 39
}

iq_panel_commands_group = {
    "id": os.urandom(8).hex(),
    "type": "group",
    "z": qolsys_nodes_tab['id'],
    "name": "IQ Panel Commands",
    "style": {
        "label": True
    },
    "nodes": [],
    # "x": 34,
    # "y": 39
}

# Add the subflow definition to the flows
qolsys_sensor_subflow = {
    "id": "258764906056d24a",
    "type": "subflow",
    "name": "Qolsys Sensor",
    "info": "",
    "category": "",
    "in": [],
    "out": [
        {
            "x": 620,
            "y": 240,
            "wires": [
                {
                    "id": "f0438b0b28420357",
                    "port": 0
                }
            ]
        }
    ],
    "env": [
        {
            "name": "topic",
            "type": "str",
            "value": "null",
            "ui": {
                "icon": "font-awesome/fa-gears",
                "label": {
                    "en-US": "Topic"
                },
                "type": "input",
                "opts": {
                    "types": [
                        "str",
                        "num",
                        "bool",
                        "json",
                        "bin",
                        "env",
                        "conf-types"
                    ]
                }
            }
        }
    ],
    "meta": {},
    "color": "#3FADB5",
    "icon": "node-red/bridge.svg",
    "status": {
        "x": 500,
        "y": 400,
        "wires": [
            {
                "id": "666235ce67962b0a",
                "port": 0
            }
        ]
    }
}

# Add the subflow nodes
subflow_nodes = [
    {
        "id": "29187c98c578000e",
        "type": "mqtt in",
        "z": "258764906056d24a",
        "name": "",
        "topic": "${topic}",
        "qos": "2",
        "datatype": "auto-detect",
        "broker": mqtt_broker['id'],
        "nl": False,
        "rap": True,
        "rh": 0,
        "inputs": 0,
        "x": 270,
        "y": 240,
        "wires": [
            [
                "f0438b0b28420357"
            ]
        ]
    },
    {
        "id": "f0438b0b28420357",
        "type": "function",
        "z": "258764906056d24a",
        "name": "Check Payload",
        "func": "let str = msg.payload;\nlet topic = env.get('topic');\nglobal.set(\"lastPayload\", str)\n\nif (str == 'Open') {\n    msg.payload = false;\n} else if (str == 'Closed') {\n    msg.payload = true;\n} else if (str == 'test') {\n    node.status({ fill: \"red\", shape: \"ring\", text: \"disconnected\" });\n    global.set(\"status\", 'disconnected');\n    return null;\n}\n\nnode.status({ fill: \"green\", shape: \"dot\", text: \"connected\" });\nglobal.set(\"status\", 'connected');\nreturn msg;",
        "outputs": 1,
        "timeout": 0,
        "noerr": 0,
        "initialize": "",
        "finalize": "",
        "libs": [],
        "x": 480,
        "y": 240,
        "wires": [
            []
        ],
        "info": ""
    },
    {
        "id": "666235ce67962b0a",
        "type": "status",
        "z": "258764906056d24a",
        "name": "",
        "scope": [
            "f0438b0b28420357"
        ],
        "x": 380,
        "y": 400,
        "wires": [
            []
        ]
    },
    {
        "id": "53d8536c787ebfec",
        "type": "inject",
        "z": "258764906056d24a",
        "name": "",
        "props": [
            {
                "p": "payload"
            }
        ],
        "repeat": "",
        "crontab": "",
        "once": True,
        "onceDelay": "0",
        "topic": "",
        "payload": "test",
        "payloadType": "str",
        "x": 290,
        "y": 180,
        "wires": [
            [
                "f0438b0b28420357"
            ]
        ]
    },
    {
        "id": "cfb6a7dd2702e5d9",
        "type": "function",
        "z": "258764906056d24a",
        "name": "Check if MQTT is Disconnected",
        "func": "if (global.get(\"status\") == 'disconnected') {\n    node.error(`Error: Qolsys Sensor with topic at MQTT path ${env.get('topic')} invalid topic.`, msg);\n}\n\nreturn msg;",
        "outputs": 1,
        "timeout": 0,
        "noerr": 0,
        "initialize": "",
        "finalize": "",
        "libs": [],
        "x": 570,
        "y": 320,
        "wires": [
            []
        ]
    },
    {
        "id": "9bcec989785e036f",
        "type": "inject",
        "z": "258764906056d24a",
        "name": "",
        "props": [],
        "repeat": "",
        "crontab": "",
        "once": True,
        "onceDelay": 0.1,
        "topic": "",
        "x": 330,
        "y": 320,
        "wires": [
            [
                "cfb6a7dd2702e5d9"
            ]
        ]
    }
]

flows = [
    qolsys_sensor_subflow,  # Add the subflow definition
    qolsys_nodes_tab,
    global_config,
    mqtt_broker,
    iq_panel_sensors_group,
    iq_panel_commands_group
] + subflow_nodes  # Add the subflow nodes

def layout_nodes(flows):
    global qolsys_nodes_tab
    y_offset = 40
    input_rows = 9
    input_i = 0
    command_i = 0
    output_i = 0
    for i, _ in enumerate(flows):
        node = flows[i]
        # Changed to look for subflow instances instead of mqtt in nodes
        if node["type"].startswith("subflow:"):
            column = input_i // input_rows
            row = input_i % input_rows
            node["x"] = 160 + 200 * column
            node["y"] = 80 + row * y_offset
            node["z"] = qolsys_nodes_tab['id']
            input_i += 1
    column = input_i // input_rows
    for i, _ in enumerate(flows):
        node = flows[i]
        if node["type"] in ["change"]:
            node["x"] = 440 + 200 * column
            node["y"] = 80 + command_i * y_offset
            node["z"] = qolsys_nodes_tab['id']
            command_i += 1
        if node["type"] in ["mqtt out"]:
            node["x"] = 660 + 200 * column
            node["y"] = 160
            node["z"] = qolsys_nodes_tab['id']
            output_i += 1

def waiting_for_discovery():
    global iq_panel_devices_discovered, iq_panel_online_since
    if iq_panel_online_since == 0:
        return True
    iq_panel_seconds_online = time.time() - iq_panel_online_since
    if iq_panel_devices_discovered == 0 and iq_panel_online_since > 0 and iq_panel_seconds_online < 600:
        return True
    return iq_panel_online_since > 0 and iq_panel_seconds_online < 4

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, userdata=flows)
mqttc.on_connect = on_connect
mqttc.on_message = on_message
password = ""
mqttc.username_pw_set("iqmate", password)
mqttc.connect("localhost", 1883, 60)
mqttc.loop_start()

iq_panel_online_attempt = 1
while iq_panel_online_attempt == 1 or waiting_for_discovery():
    time.sleep(1)
    if iq_panel_online_since is None:
        print("It seems there is a problem with Appdaemon or the MQTT broker. Check the logs.")
    elif iq_panel_online_since == 0 and iq_panel_online_attempt % 60 == 1:
        print("IQ Panel is offline. Make sure the IP address is correct and the Control4 integration is enabled.")
    iq_panel_online_attempt += 1

mqttc.loop_stop()

layout_nodes(flows)

with open('flows.json', 'w') as f:
    json.dump(flows, f, ensure_ascii=False, indent=4)

credentials = {
    mqtt_broker['id']: {
        "user": "iqmate",
        "password": ""
    }
}

with open('flows_cred.json', 'w') as f:
    json.dump(credentials, f, ensure_ascii=False, indent=4)
