import paramiko

def create_banner():
    return "MIKROTIK TESTING" # RB Faizal

def execute_ssh_command(hostname, command):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        client.connect(
            hostname=hostname,
            username="admin",
            password="tahubulat",
            port=8222,
            timeout=10
        )

        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode("utf-8", errors="ignore")
        client.close()

        return output

    except Exception as e:
        return f"ERROR: {str(e)}"

def ping_status(router_set):
    host = router_set["testing"]
    return execute_ssh_command(host, "ping 8.8.8.8 count=5")

def traceroute_status(router_set):
    host = router_set["testing"]
    return execute_ssh_command(host, "tool traceroute 8.8.8.8 count=5")

def traffic_status(router_set):
    host = router_set["testing"]
    command = "/interface monitor-traffic ether1 once"
    return execute_ssh_command(host, command)





