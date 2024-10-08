#!/usr/bin/env python3.12
#######################################
# Author: Tyler Wynkoop
# Edited: 2024-10-07
#######################################
import subprocess
import csv
import re
import sys

# Define a dictionary mapping subnets to names
SUBNET_NAMES = {
    '192.168.1.0/24': 'Secure Lan',
    '192.168.2.0/24': 'Server/Infra',
    '192.168.3.0/24': 'IoT'
}

def get_subnet_name(subnet):
    # Match the subnet to its corresponding name
    return SUBNET_NAMES.get(subnet, 'Unknown')

def get_os_type(os_line):
    # Check for specific OS keywords in the line passed to the function
    if 'ESXi' in os_line:
        return 'ESXi'
    elif 'Linux' in os_line:
        return 'Linux'
    elif 'Windows' in os_line:
        return 'Windows'
    elif 'Cisco' in os_line:
        return 'Cisco'
    else:
        return 'Other'

def scan_subnet(subnet):
    # Run nmap with OS detection (-O) and hostname resolution (-R)
    try:
        result = subprocess.run(['nmap', '-O', '-R', subnet], capture_output=True, text=True)
    except Exception as e:
        print(f"Error scanning subnet {subnet}: {e}")
        return []

    output = result.stdout
    results = []
    
    # Used to capture IP, hostname, and OS details from NMAP output
    host_pattern = re.compile(r'Nmap scan report for (.+) \(([\d\.]+)\)|Nmap scan report for ([\d\.]+)')
    os_pattern = re.compile(r'(OS details: .+|Aggressive OS guesses: .+)')
    
    hosts = host_pattern.finditer(output)
    
    for host in hosts:
        hostname, ip_address_1, ip_address_2 = host.groups()
        ip_address = ip_address_1 if ip_address_1 else ip_address_2
        hostname = hostname if hostname else 'Unknown'
        
        # Searches for the OS in the output after the host match
        os_match = os_pattern.search(output, host.end())
        os_line = os_match.group(0) if os_match else 'Unknown'
        
        os_type = get_os_type(os_line)
        subnet_name = get_subnet_name(subnet)
        
        results.append({
            'IP': ip_address,
            'Hostname': hostname,
            'OS Type': os_type,
            'Subnet Name': subnet_name
        })
    return results

def read_subnets(file_path):
    with open(file_path, 'r') as file:
        subnets = [line.strip() for line in file if line.strip()]
    return subnets

def write_to_csv(data, output_file):
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['IP', 'Hostname', 'OS Type', 'Subnet Name']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for entry in data:
            writer.writerow(entry)

def main():
    if len(sys.argv) != 2:
        print("Usage: python script_name.py <subnets.txt>")
        sys.exit(1)
    
    subnet_file = sys.argv[1]
    subnets = read_subnets(subnet_file)
    all_results = []

    for subnet in subnets:
        print(f"Scanning subnet: {subnet}")
        all_results.extend(scan_subnet(subnet))
    
    write_to_csv(all_results, 'scan_results.csv')
    print("Scan complete. Results saved to 'scan_results.csv'.")

if __name__ == "__main__":
    main()