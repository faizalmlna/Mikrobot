import paramiko
import os
import re
# Login Router
def create_banner(hostname):
    banner = f"{'#' * 33}\n# NETBOT ~ MIKROTIK DC #\n{'#' * 33}\n"
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

#router_840 COMMAND########################################################################################################################################################################


def internet_cbn_dc_status(hostname):
    hostname_12 = hostname["router_840"]
    try:
        combined_output = ""
        print ("test")
        output2 = execute_ssh_command(hostname_12, 'too traceroute x.x.x.x routing-table=CBN count=5')
        combined_output = f"{create_banner(hostname_12)}\nINTERNET CBN STATUS:\n{output2}\n"

        print(combined_output)
        return combined_output
    except Exception as e:
        return str(e)

def internet_sigma_dc_status(hostname):
    hostname_12 = hostname["router_840"]
    try:
        combined_output = ""
        output2 = execute_ssh_command(hostname_12, 'too traceroute address=x.x.x.x routing-table=SIGMA count=5 ')
        combined_output = f"{create_banner(hostname_12)}\nINTERNET SIGMA STATUS:\n{output2}\n"

        print(combined_output)
        return combined_output
    except Exception as e:
        return str(e)    


def block_ip_public_dc(hostname, ip_address):

    ip = ip_address.replace("<username_bot_tele>", "")

    print(hostname)

    
    hostname_1 = hostname["router_840"]

    print(hostname_1)
    try:
        output1 = execute_ssh_command(hostname_1, f'ip firewall address-list add address={ip} list=block_public')

        print(output1)
        
        return f"Success add block ip public dc {output1}"
    except Exception as e:
        return str(e)

    

def show_block_ip_public_dc(hostname):
    hostname_1 = hostname["router_840"]
    try:
        combined_output = ""
        output2 = execute_ssh_command(hostname_1, 'ip firewall address-list print where list="block_public"')
        combined_output = f"{create_banner(hostname_1)}\n LIST BLOCK IP PUBLIC DC:\n{output2}\n"

        print(combined_output)
        return combined_output
    except Exception as e:
        return str(e)
        