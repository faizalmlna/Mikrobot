import paramiko
import os
import re
# Login Router
def create_banner(hostname):
    banner = f"{'#' * 33}\n# NETBOT ~ MIKROTIK CLOUD GATOT#\n{'#' * 33}\n"
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

#COMMAND########################################################################################################################################################################


def gatot_dc_cbn_status(hostname):
    hostname_8 = hostname["gatot"]
    try:
        combined_output = ""
        output2 = execute_ssh_command(hostname_8, 'ping x.x.x.x count=10')
        combined_output = f"{create_banner(hostname_8)}\ngatot - DC-CBN STATUS:\n{output2}\n"

        print(combined_output)
        return combined_output
    except Exception as e:
        return str(e)      

def gatot_nginx_dc_status(hostname):
    hostname_8 = hostname["gatot"]
    try:
        combined_output = ""
        output2 = execute_ssh_command(hostname_8, 'x.x.x.x count=10')
        combined_output = f"{create_banner(hostname_8)}\ngatot - Nginx DC STATUS:\n{output2}\n"

        print(combined_output)
        return combined_output
    except Exception as e:
        return str(e)  

def gatot_drc_cbn_status(hostname):
    hostname_8 = hostname["gatot"]
    try:
        combined_output = ""
        output2 = execute_ssh_command(hostname_8, 'ping x.x.x.x count=10')
        combined_output = f"{create_banner(hostname_8)}\ngatot - DRC-CBN STATUS:\n{output2}\n"

        print(combined_output)
        return combined_output
    except Exception as e:
        return str(e) 

def gatot_nginx_drc_status(hostname):
    hostname_8 = hostname["gatot"]
    try:
        combined_output = ""
        output2 = execute_ssh_command(hostname_8, 'ping x.x.x.x count=10')
        combined_output = f"{create_banner(hostname_8)}\ngatot - Nginx DRC STATUS:\n{output2}\n"

        print(combined_output)
        return combined_output
    except Exception as e:
        return str(e)     

