from netmiko import ConnectHandler
import sys

def get_trunk_vlan_status(device, vlan_id):
    try:
        conn = ConnectHandler(**device)
        output = conn.send_command("show interfaces trunk")
        conn.disconnect()
    except Exception as e:
        print(f"Connection error: {e}")
        sys.exit(1)

    interfaces = []
    capture = False

    for line in output.splitlines():
        if "Port" in line and "Vlans allowed" in line:
            capture = True
            continue
        if capture and line.strip() == "":
            break  # End of table
        if capture:
            fields = line.split()
            if len(fields) < 4:
                continue
            port = fields[0]
            vlans = fields[-1]
            # Expand VLAN ranges (e.g., "1-5,10")
            allowed = []
            for part in vlans.split(','):
                if '-' in part:
                    start, end = part.split('-')
                    allowed.extend(range(int(start), int(end)+1))
                else:
                    allowed.append(int(part))
            if int(vlan_id) in allowed:
                interfaces.append(port)

    if interfaces:
        print(f"VLAN {vlan_id} is allowed on trunks: {', '.join(interfaces)}")
    else:
        print(f"VLAN {vlan_id} not found on any trunk interfaces.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python vlanwalk.py <vlan_id>")
        sys.exit(1)

    vlan_id = sys.argv[1]

    # Define your Cisco device
    device = {
        'device_type': 'cisco_ios',
        'ip': '192.168.1.2',
        'username': 'admin',
        'password': 'password',
    }

    get_trunk_vlan_status(device, vlan_id)
