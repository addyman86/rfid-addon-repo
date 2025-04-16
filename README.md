# RFID Lookup Add-on for Home Assistant

This is a custom Home Assistant add-on that listens to an MQTT topic for RFID UIDs,
queries a MariaDB database for product info, and updates the inventory via MQTT.

## Features

- Listens to UID from `rfid-mini/sensor/rfid_uid/state`
- Looks up product info in MariaDB
- Publishes product name and inventory
- Allows updating stock level via MQTT

## Installation

1. Clone or fork this repo
2. Add the GitHub URL as a custom repository in Home Assistant
3. Install the `RFID Lookup` add-on from the "Add-on Store"
