import paramiko
import os
import re
# Login Router
def create_banner(hostname):
    banner = f"{'#' * 33}\n# NETBOT ~ MIKROTIK DRC CBN 40 #\n{'#' * 33}\n"
    return banner

def execute_ssh_command(hostname, command):
    try:
        # Inisialisasi Koneksi SSH ke Perangkat MikroTik
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())


        client.connect(
            hostname=hostname,
            username=os.getenv('MKT_LOGIN_USER'),
            password=os.getenv('MKT_LOGIN_PASSWORD'),
            port=int(os.getenv('MKT_LOGIN_PORT')),
        )

        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode('ascii')

        client.close()
        return output
    except Exception as e:
        return str(e)

#DRC-40-CBN COMMAND########################################################################################################################################################################


def internet_cbn_drc_status(hostname):
    hostname_42 = hostname["router_940"]
    try:
        combined_output = ""
        output1 = execute_ssh_command(hostname_42, 'tool traceroute address=x.x.x.x count=5')
        combined_output = f"{create_banner(hostname_42)}\n INTERNET CBN DRC STATUS :\n{output1}\n"

        print(combined_output)
        return combined_output
    except Exception as e:
        return str(e)

def block_ip_public_drc_40(hostname, ip_address):

    ip = ip_address.replace("<username_bot>", "")

    print(hostname)

    
    hostname_1 = hostname["router_940"]

    print(hostname_1)
    try:
        output1 = execute_ssh_command(hostname_1, f'ip firewall address-list add address={ip} list=block-public')

        print(output1)
        
        return f"Success add block ip public drc {output1}"
    except Exception as e:
        return str(e)

    

def show_block_ip_public_drc_40(hostname):
    hostname_1 = hostname["router_940"]
    try:
        combined_output = ""
        output2 = execute_ssh_command(hostname_1, 'ip firewall address-list print where list="block-public"')
        combined_output = f"{create_banner(hostname_1)}\n LIST BLOCK IP PUBLIC DRC CBN:\n{output2}\n"

        print(combined_output)
        return combined_output
    except Exception as e:
        return str(e)
        
