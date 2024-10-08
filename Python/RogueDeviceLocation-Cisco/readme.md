## Cisco - Rogue Asset Locator
Used this to locate the switch and port a device is connected to.

### Requirements:
1. Need to have Python 3 installed
2. From Python install the netmiko library:
```python
pip install netmiko
```

### Before First Run:
- Edit the python script "RogueAssetLocator.py"; modify the "switch_ips" list and the Windows Server DHCP IP/Hostname (found in the function "get_cisco_mac") to match your environment.

### Running the script:
1. Navigate to the script directory
2. Run the script using the following formatting:
```python
python RogueAssetLocator.py
```