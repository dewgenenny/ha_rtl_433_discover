# Home Assistant rtl_433 Discovery

A custom component for Home Assistant that discovers devices from `rtl_433` MQTT events.

## Features
- **Auto-Discovery**: Listens to `rtl_433` MQTT events and discovers devices.
- **Manual Confirmation**: Discovered devices appear in Home Assistant's "Discovered" section and require approval before being added.
- **Ignore Logic**: ability to ignore specific devices to prevent them from resurfacing.
- **Sensor Creation**: Automatically creates sensors for temperature, humidity, wind, rain, light, battery, etc.

## Installation

### Via HACS (Recommended)
1.  Ensure [HACS](https://hacs.xyz/) is installed.
2.  Go to **HACS** > **Integrations**.
3.  Click the 3 dots in the top right corner and select **Custom repositories**.
4.  Enter the URL of this repository: `https://github.com/dewgenenny/ha_rtl_433_discover`
5.  Select **Integration** as the category.
6.  Click **Add**.
7.  Search for "rtl_433 Discovery" and install it.
8.  Restart Home Assistant.

### Manual Installation
1.  Download the `custom_components/rtl_433_discover` folder from this repository.
2.  Copy it to your Home Assistant `config/custom_components/` directory.
3.  Restart Home Assistant.

## Configuration

### 1. Prerequisite
Ensure the official **MQTT integration** is installed and configured in Home Assistant.

### 2. Add the Bridge
1.  Go to **Settings** > **Devices & Services**.
2.  Click **Add Integration**.
3.  Search for **rtl_433 Discovery**.
4.  Enter your MQTT Topic Prefix (default: `rtl_433/+/events`).
5.  This creates the "Bridge" which listens for devices.

### 3. Adding Devices
1.  When a new device is detected via MQTT, it will appear in the **Discovered** section of the Integrations dashboard.
2.  Click **Configure** on the discovered item.
3.  Confirm that you want to add the device.
4.  The device and its sensors will now be available.

### 4. Ignoring Devices
If you have neighbors' devices you don't want to see:
1.  Go to the **rtl_433 Discovery** Bridge entry.
2.  Click **Configure**.
3.  Enter the Device IDs you want to ignore (comma separated), e.g., `Bresser-7in1-43951, 12345`.
4.  These devices will no longer trigger the discovery flow.