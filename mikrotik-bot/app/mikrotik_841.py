import paramiko
import os
import re
# Login Router
def create_banner(hostname):
    banner = f"{'#' * 33}\n# NETBOT ~ MIKROTIK DC 841 #\n{'#' * 33}\n"
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

#DC FW COMMAND########################################################################################################################################################################


def interconnect_dc_status(hostname):
    hostname_1 = hostname["841_dc"]
    try:
        combined_output = ""
        output1 = execute_ssh_command(hostname_1, 'routing bgp peer print detail status where name="name bgp"')

        def filter_established_and_uptime(output1):
            lines = output1.split("\n")
            state = ""
            uptime = ""

            for line in lines:
                if "state=" in line:
                    state = line.strip().split("state=")[-1]
                elif "uptime=" in line:
                    uptime = line.strip().split("uptime=")[-1].split()[0] 

            return f"state={state}\nuptime={uptime}"
        
        output1 = filter_established_and_uptime(output1)
        output2 = execute_ssh_command(hostname_1, 'ping x.x.x.x  count=10')
        output3 = execute_ssh_command(hostname_1, 'routing bgp peer print detail status where name="name bgp"')
        def filter_established_and_uptime(output3):
            lines = output3.split("\n")
            state = ""
            uptime = ""

            for line in lines:
                if "state=" in line:
                    state = line.strip().split("state=")[-1]
                elif "uptime=" in line:
                    uptime = line.strip().split("uptime=")[-1].split()[0] 

            return f"state={state}\nuptime={uptime}"
        
        output3 = filter_established_and_uptime(output3)
        output4 = execute_ssh_command(hostname_1, 'ping x.x.x.x count=10')

        combined_output = f"{create_banner(hostname_1)}\nBGP INTERCONNECT a STATUS :\n{output1}\n\nINTERCONNECT DC a STATUS:\n{output2}\n \nBGP INTERCONNECT b STATUS :\n{output3}\n\nINTERCONNECT DC b STATUS:\n{output4}\n"

        print(combined_output)
        return combined_output
    except Exception as e:
        return str(e)


def Database_dc_status(hostname):
    hostname_12 = hostname["841_dc"]
    try:
        combined_output = ""
        output2 = execute_ssh_command(hostname_12, 'ping x.x.x.x count=10')
        combined_output = f"{create_banner(hostname_12)}\nDatabase DC STATUS:\n{output2}\n"

        print(combined_output)
        return combined_output
    except Exception as e:
        return str(e)    
