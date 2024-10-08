## Ping Sweep with OS Match
Used for asset discovery across multiple subnets then exports its findings into a csv file.

### Requirements:
1. Need to have Python 3 and Nmap installed

### Before First Run:
- Edit the python script "PingSweepWithOSmatch.py"; modify the "SUBNET_NAMES" dictionary and the function "get_os_type" to match your environment. Ideally, the "SUBNET_NAMES" dictionary should match the subnets in your "subnets.txt" file.

### Running the script:
1. Navigate to the script directory
2. Run the script using the following formatting:
```python
python PingSweepWithOSmatch.py subnets.txt
```