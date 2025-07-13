# Senertec Dachs Modbus Integration for Home Assistant

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]][license]

[![hacs][hacs-shield]][hacs]

_Integration to connect the Senertec Dachs via Modbus._

**This integration will set up the following platforms.**

Platform | Description
-- | --
`sensor` | Show sensor values from the Senertec Dachs.

## Installation

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory (folder) there, you need to create it.
3. In the `custom_components` directory (folder) create a new folder called `dachs_modbus`.
4. Download all the files from the `custom_components/dachs_modbus/` directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Restart Home Assistant
7. In the HA UI go to "Configuration" -> "Integrations" -> "Add Integration" and search for "Senertec Dachs Modbus"

## Configuration is done in the UI

[commits-shield]: https://img.shields.io/github/commit-activity/y/jules-agent/ha-dachs-modbus.svg?style=for-the-badge
[commits]: https://github.com/jules-agent/ha-dachs-modbus/commits/main
[hacs]: https://hacs.xyz
[hacs-shield]: https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge
[license]: https://github.com/jules-agent/ha-dachs-modbus/blob/main/LICENSE
[license-shield]: https://img.shields.io/github/license/jules-agent/ha-dachs-modbus.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/jules-agent/ha-dachs-modbus.svg?style=for-the-badge
[releases]: https://github.com/jules-agent/ha-dachs-modbus/releases
