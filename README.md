# IQ Mate (Qolsys IQ Panel Super Charger)

IQ Mate is a tool to help more serious home automation folks make the most of their Qolsys IQ Panel. Use it to integrate your IQ Panel with devices outside of the Qolsys & Alarm.com walled garden.

IQ Mate interacts with the IQ Panel in 2 ways:

1. It uses the [Qolsys Gateway](https://github.com/XaF/qolsysgw) integration from Home Assistant to interact with the [IQ Panel Control4](https://qolsys.reamaze.com/kb/connections-and-configurations/how-to-integrate-your-iq-system-with-control-4) integration, which gives IQ Mate real-time sensor status and lets it arm and disarm the IQ Panel.
2. It uses Qolsys Programmable (PGM) Outputs and Sensor Inputs to send and receive on/off signals with the IQ Panel. This enables virtually any automation to be programmed with any device, even if it's not compatible with Qolsys or Alarm.com. It's not super efficient but it works.

Automations are programmed in [Node-RED](https://nodered.org/), a visual flow editor that makes it easy to program complex automations.