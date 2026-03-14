import paramiko
import os
import re
# Login Router
def create_banner(hostname):
    banner = f"{'#' * 33}\n# NETBOT ~ MIKROTIK VMWARE#\n{'#' * 33}\n"
    return banner

def execute_ssh_command(hostname, command):
    try:
        # Inisialisasi Koneksi SSH ke Perangkat MikroTik
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())


        client.connect(
            hostname=hostname,
            username="asdfgh",
            password="12345",
            port=555,
        )

        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode('ascii')

        client.close()
        return output
    except Exception as e:
        return str(e)

#router_840 COMMAND########################################################################################################################################################################

def ping_status(router_set):
    host = router_set["vmware_720"]
    return execute_ssh_command(host, "ping 8.8.8.8 count=5")

def traceroute_status(router_set):
    host = router_set["vmware_720"]
    return execute_ssh_command(host, "tool traceroute 8.8.8.8 count=5")

def traffic_status(router_set):
    host = router_set["vmware_720"]
    return execute_ssh_command(host, "/interface monitor-traffic vlan3-LAN.NEOC  once")

