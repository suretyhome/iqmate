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
        flows.append(mttq_out_node("IQ Panel Command", payload))
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
    global mqtt_broker
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
        "broker": mqtt_broker['id'],
        "wires": [],
        "info": json.dumps(config, indent=4)
    }

def mttq_in_node(name, topic, config):
    global mqtt_broker
    return {
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
    "name": "Waveshare Device",
    "clienttype": "tcp",
    "bufferCommands": True,
    "stateLogEnabled": True,
    "queueLogEnabled": False,
    "failureLogEnabled": True,
    "tcpHost": "192.168.12.148",
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

flows = [
    qolsys_nodes_tab,
    global_config,
    mqtt_broker,
    waveshare_modbus_client
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
        "y": 439,
        "w": 652,
        "h": 82
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
        "x": 590,
        "y": 480,
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
        "x": 380,
        "y": 480,
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
        "x": 180,
        "y": 480,
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
        "y": 539,
        "w": 572,
        "h": 362
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
        "rate": "4",
        "rateUnit": "s",
        "delayOnStart": False,
        "startDelayTime": "",
        "server": waveshare_modbus_client['id'],
        "useIOFile": False,
        "ioFile": "",
        "useIOForPayload": False,
        "emptyMsgOnFail": False,
        "x": 180,
        "y": 720,
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
            "x": 540,
            "y": 580 + 40 * i,
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
            "x": 390,
            "y": 580 + 40 * i,
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
        "x": 654,
        "y": 539,
        "w": 179,
        "h": 362
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
            "x": 740,
            "y": 580 + 40 * i,
            "wires": [
                [],
                []
            ]
        })
    group['nodes'] = list(map(lambda x: x['id'], nodes))
    return [group] + nodes

def layout_nodes(flows):
    global qolsys_nodes_tab
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
            node["z"] = qolsys_nodes_tab['id']
        if node["type"] in ["change"]:
            commands += 1
            node["x"] = 320
            node["y"] = commands * offset
            node["z"] = qolsys_nodes_tab['id']
        if node["type"] in ["mqtt out"]:
            outputs += 1
            node["x"] = 520
            node["y"] = outputs * offset
            node["z"] = qolsys_nodes_tab['id']

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
