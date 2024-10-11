#!/usr/bin/env python3.12
#######################################
# Author: Tyler Wynkoop and David Tobin
# Edited: 2024-10-10
#######################################
import subprocess
import re
import socket
from netmiko import ConnectHandler
from getpass import getpass

# List of switch IP/Hostnames
switch_ips = [
    '192.168.2.2',
    '192.168.2.3',
    '192.168.2.4'
]

def resolve_hostname_to_ip(hostname):
    try:
        ip_address = socket.gethostbyname(hostname)
        return ip_address
    except socket.gaierror:
        return None

def get_juniper_mac(client_identifier):
    try:
        if not client_identifier.replace('.', '').isdigit():  # Check for IP format
            client_identifier = resolve_hostname_to_ip(client_identifier)
            if not client_identifier:
                return "Failed to resolve hostname to IP."

        # PowerShell command to get the MAC address from a specific DHCP server
        command = f'Get-DhcpServerv4Lease -ComputerName 192.168.2.53 -IPAddress {client_identifier} | Select-Object -ExpandProperty ClientId'
        result = subprocess.run(['powershell', '-Command', command], capture_output=True, text=True)

        # Extract the MAC address from the output
        mac_address = result.stdout.strip()

        if mac_address:
            # Format MAC address in the desired format
            mac_parts = mac_address.replace('-', ':').lower().split(':')
            formatted_mac = ':'.join(mac_parts)
            return formatted_mac
        else:
            return None
    except Exception as e:
        print(f"An error occurred while getting MAC address: {e}")
        return None

def find_device_on_network(ip_address):
    # Ask for SSH credentials
    username = input("Enter your SSH username: ")
    password = getpass("Enter your SSH password: ")
    print()

    # Get the MAC address for the given IP/hostname
    mac_address = get_juniper_mac(ip_address)

    if not mac_address:
        print(f"MAC address for {ip_address} not found.")
        return

    # Loop through the list of switches
    for switch_ip in switch_ips:
        # Define the device for Juniper
        juniper_device = {
            'device_type': 'juniper',
            'host': switch_ip,
            'username': username,
            'password': password,
        }

        try:
            # Connect to the switch
            print(f"Connecting to {switch_ip}...")
            net_connect = ConnectHandler(**juniper_device)

            # Send command to get the MAC address table
            mac_address_table = net_connect.send_command('show ethernet-switching table')

            # Find the port associated with the MAC address
            port = None
            for line in mac_address_table.splitlines():
                if mac_address in line:
                    # Match only physical Ethernet ports, remove ".0"
                    match = re.search(r'ge-(\d+)/0/(\d+)\.0$', line)
                    if match:
                        port = f"ge-{match.group(1)}/0/{match.group(2)}"
                        break

            if port:
                print(f"The device {ip_address} is connected to port {port} on switch {switch_ip}.")
                net_connect.disconnect()
                return  # Exit after finding the device
            else:
                print(f"MAC address {mac_address} not found in MAC address table on {switch_ip}.")

            # Disconnect from the switch
            net_connect.disconnect()

        except Exception as e:
            print(f"An error occurred while connecting to {switch_ip}: {e}")

    print(f"The device {ip_address} was not found on any of the specified switches.")

if __name__ == "__main__":
    print()
    target_ip = input("Enter the IP address or hostname: ")
    find_device_on_network(target_ip)
