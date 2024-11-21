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
    global iq_panel_sensors_group, mqtt_broker
    node = {
        "id": os.urandom(8).hex(),
        "type": "mqtt in",
        "name": name,
        "topic": topic,
        "qos": "2",
        "datatype": "auto-detect",
        "broker": mqtt_broker['id'],
        "nl": False,
        "rap": True,
        "rh": 0,
        "inputs": 0,
        "wires": [
            []
        ],
        "info": json.dumps(config, indent=4)
    }
    iq_panel_sensors_group['nodes'].append(node['id'])
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

mqtt_broker = {
    "id": os.urandom(8).hex(),
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

waveshare_modbus_client = {
    "id": os.urandom(8).hex(),
    "type": "modbus-client",
    "name": "Waveshare IO Module",
    "clienttype": "tcp",
    "bufferCommands": True,
    "stateLogEnabled": True,
    "queueLogEnabled": False,
    "failureLogEnabled": True,
    "tcpHost": "192.168.1.200",
    "tcpPort": "4196",
    "tcpType": "DEFAULT",
    "serialPort": "/dev/ttyUSB",
    "serialType": "RTU-BUFFERD",
    "serialBaudrate": "9600",
    "serialDatabits": "8",
    "serialStopbits": "1",
    "serialParity": "none",
    "serialConnectionDelay": "100",
    "serialAsciiResponseStartDelimiter": "0x3A",
    "unit_id": "1",
    "commandDelay": "1",
    "clientTimeout": "1000",
    "reconnectOnTimeout": True,
    "reconnectTimeout": "2000",
    "parallelUnitIdsAllowed": True,
    "showErrors": True,
    "showWarnings": True,
    "showLogs": True
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

flows = [
    qolsys_nodes_tab,
    global_config,
    mqtt_broker,
    waveshare_modbus_client,
    iq_panel_sensors_group,
    iq_panel_commands_group
]

def waveshare_set_up_nodes(qolsys_nodes_tab, waveshare_modbus_client):
    group = {
        "id": os.urandom(8).hex(),
        "type": "group",
        "z": qolsys_nodes_tab['id'],
        "name": "Waveshare Set Up (do this once)",
        "style": {
            "label": True
        },
        "nodes": [],
        "x": 54,
        "y": 839
    }
    modbus_node = {
        "id": os.urandom(8).hex(),
        "type": "modbus-flex-write",
        "z": qolsys_nodes_tab['id'],
        "g": group['id'],
        "name": "Waveshare Config",
        "showStatusActivities": True,
        "showErrors": True,
        "showWarnings": True,
        "server": waveshare_modbus_client['id'],
        "emptyMsgOnFail": False,
        "keepMsgProperties": False,
        "delayOnStart": False,
        "startDelayTime": "",
        "x": group['x'] + 536,
        "y": group['y'] + 41,
        "wires": [
            [],
            []
        ]
    }
    change_node = {
        "id": os.urandom(8).hex(),
        "type": "change",
        "z": qolsys_nodes_tab['id'],
        "g": group['id'],
        "name": "Control Mode Normal",
        "rules": [
            {
                "t": "set",
                "p": "payload",
                "pt": "msg",
                "to": "{\"value\":[0,0,0,0,0,0,0,0],\"fc\":16,\"unitid\":1,\"address\":4096,\"quantity\":8}",
                "tot": "json"
            }
        ],
        "action": "",
        "property": "",
        "from": "",
        "to": "",
        "reg": False,
        "x": group['x'] + 326,
        "y": group['y'] + 41,
        "wires": [
            [
                modbus_node['id']
            ]
        ]
    }
    inject_node = {
        "id": os.urandom(8).hex(),
        "type": "inject",
        "z": qolsys_nodes_tab['id'],
        "g": group['id'],
        "name": "Set Contol Mode",
        "props": [
            {
                "p": "payload"
            },
            {
                "p": "topic",
                "vt": "str"
            }
        ],
        "repeat": "",
        "crontab": "",
        "once": False,
        "onceDelay": 0.1,
        "topic": "",
        "payload": "",
        "payloadType": "date",
        "x": group['x'] + 126,
        "y": group['y'] + 41,
        "wires": [
            [
                change_node['id']
            ]
        ]
    }
    nodes = [inject_node, change_node, modbus_node]
    group['nodes'] = list(map(lambda x: x['id'], nodes))
    return [group] + nodes

def iq_hardwire_pg_outputs_nodes(qolsys_nodes_tab, waveshare_modbus_client):
    group = {
        "id": os.urandom(8).hex(),
        "type": "group",
        "z": qolsys_nodes_tab['id'],
        "name": "IQ Hardwire PowerG Outputs",
        "style": {
            "label": True
        },
        "nodes": [],
        "x": 54,
        "y": 459
    }
    sampler = {
        "id": os.urandom(8).hex(),
        "type": "modbus-read",
        "z": qolsys_nodes_tab['id'],
        "g": group['id'],
        "name": "Output Sampler",
        "topic": "",
        "showStatusActivities": False,
        "logIOActivities": False,
        "showErrors": True,
        "showWarnings": True,
        "unitid": "",
        "dataType": "Input",
        "adr": "0",
        "quantity": "8",
        "rate": "1",
        "rateUnit": "s",
        "delayOnStart": False,
        "startDelayTime": "",
        "server": waveshare_modbus_client['id'],
        "useIOFile": False,
        "ioFile": "",
        "useIOForPayload": False,
        "emptyMsgOnFail": False,
        "x": group['x'] + 126,
        "y": group['y'] + 181,
        "wires": [
            [],
            []
        ]
    }
    nodes = [sampler]
    for i in range(8):
        events = {
            "id": os.urandom(8).hex(),
            "type": "rbe",
            "z": qolsys_nodes_tab['id'],
            "g": group['id'],
            "name": "Events " + str(i + 1),
            "func": "rbe",
            "gap": "",
            "start": "",
            "inout": "out",
            "septopics": True,
            "property": "payload",
            "topi": "topic",
            "x": group['x'] + 486,
            "y": group['y'] + 41 + 40 * i,
            "wires": [
                []
            ]
        }
        samples = {
            "id": os.urandom(8).hex(),
            "type": "change",
            "z": qolsys_nodes_tab['id'],
            "g": group['id'],
            "name": "Samples " + str(i + 1),
            "rules": [
                {
                    "t": "set",
                    "p": "payload",
                    "pt": "msg",
                    "to": "payload[" + str(i) + "]",
                    "tot": "msg"
                }
            ],
            "action": "",
            "property": "",
            "from": "",
            "to": "",
            "reg": False,
            "x": group['x'] + 336,
            "y": group['y'] + 41 + 40 * i,
            "wires": [
                [
                    events['id']
                ]
            ]
        }
        sampler['wires'][0].append(samples['id'])
        nodes.extend([samples, events])
    group['nodes'] = list(map(lambda x: x['id'], nodes))
    return [group] + nodes

def iq_hardwire_pg_inputs_nodes(qolsys_nodes_tab, waveshare_modbus_client):
    group = {
        "id": os.urandom(8).hex(),
        "type": "group",
        "z": qolsys_nodes_tab['id'],
        "name": "IQ Hardwire PowerG Inputs",
        "style": {
            "label": True
        },
        "nodes": [],
        "x": 674,
        "y": 459
    }
    nodes = []
    for i in range(8):
        nodes.append({
            "id": os.urandom(8).hex(),
            "type": "modbus-write",
            "z": qolsys_nodes_tab['id'],
            "g": group['id'],
            "name": "Input " + str(i + 1),
            "showStatusActivities": False,
            "showErrors": True,
            "showWarnings": True,
            "unitid": "",
            "dataType": "Coil",
            "adr": str(i),
            "quantity": "1",
            "server": waveshare_modbus_client['id'],
            "emptyMsgOnFail": False,
            "keepMsgProperties": False,
            "delayOnStart": False,
            "startDelayTime": "",
            "x": group['x'] + 86,
            "y": group['y'] + 41 + 40 * i,
            "wires": [
                [],
                []
            ]
        })
    group['nodes'] = list(map(lambda x: x['id'], nodes))
    return [group] + nodes

def layout_nodes(flows):
    global qolsys_nodes_tab
    y_offset = 40
    input_rows = 9
    input_i = 0
    command_i = 0
    output_i = 0
    for i, _ in enumerate(flows):
        node = flows[i]
        if node["type"] in ["mqtt in"]:
            column = input_i // input_rows
            row = input_i % input_rows
            node["x"] = 160 + column * 200
            node["y"] = 80 + row * y_offset
            node["z"] = qolsys_nodes_tab['id']
            input_i += 1
    column = input_i // input_rows
    for i, _ in enumerate(flows):
        node = flows[i]
        if node["type"] in ["change"]:
            node["x"] = 400 + 200 * column
            node["y"] = 80 + command_i * y_offset
            node["z"] = qolsys_nodes_tab['id']
            command_i += 1
        if node["type"] in ["mqtt out"]:
            node["x"] = 620 + 200 * column
            node["y"] = 160
            node["z"] = qolsys_nodes_tab['id']
            output_i += 1

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, userdata=flows)
mqttc.on_connect = on_connect
mqttc.on_message = on_message
password = ""
mqttc.username_pw_set("iqmate", password)
mqttc.connect("localhost", 1883, 60)
mqttc.loop_start()
time.sleep(4)
mqttc.loop_stop()

layout_nodes(flows)

flows.extend(waveshare_set_up_nodes(qolsys_nodes_tab, waveshare_modbus_client))
flows.extend(iq_hardwire_pg_outputs_nodes(qolsys_nodes_tab, waveshare_modbus_client))
flows.extend(iq_hardwire_pg_inputs_nodes(qolsys_nodes_tab, waveshare_modbus_client))

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
