# ha-dachs-modbus - Template Home Assistant Integration for ModbusTCP Devices

This repository provides a template for creating a Home Assistant integration to control and monitor devices using ModbusTCP.

## Setup

1.  **Configure your ModbusTCP device.**\
    Ensure your device is accessible on your network via ModbusTCP and note its IP address and port.
1.  **Install the Integration (Template).**\
    This integration is available through HACS (Home Assistant Community Store). Click the following button to add it to your Home Assistant: \
    [![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=dachs_modbus)\
    \
    Alternatively add it manually with the following steps:
    1.  **Add this repository as a Custom Repository in HACS.**
        *   In HACS, go to the Integrations tab.
        *   Click on the three dots in the top right corner and select `Custom repositories`.
        *   Enter the URL of this repository (`https://github.com/fischerq/ha-braiins-pool/`) and select the category `Integration`.
        *   Click `Add`.
    1.  **Install the integration (Template).**
        *   Search for "Braiins Pool" in the HACS Integrations tab.
        *   Click "Download" and restart Home Assistant.
1.  **Add the Modbus TCP Device (Template) integration.**
    *   Go to Settings -> Devices & Services -> Add Integration.
    *   Search for "Modbus TCP Device (Template)" and select it.
    *   Follow the configuration flow to set up your device.

## Provided Entities

This template provides examples for creating sensor entities. You will need to define the specific entities for your ModbusTCP device.
## Implementation

The files in `/custom_components/dachs_modbus/` provide the basic structure for a Home Assistant integration. You will need to modify these files to implement the specific functionality for your ModbusTCP device:
\
*   `__init__.py`: Integration entry point and setup.\
*   `api.py`: Placeholder for ModbusTCP communication.\
*   `config_flow.py`: Handles user configuration.\
*   `const.py`: Defines constants.\
\
*   `coordinator.py`: Manages data updates.\
\
*   `manifest.json`: Integration metadata.\
\
*   `sensor.py`: Example sensor entity creation.
