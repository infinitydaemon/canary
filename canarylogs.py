import paramiko
import time
from colorama import Fore, Style, init
import re

# Initialize colorama for automatic reset after each line
init(autoreset=True)

USERNAME = 'canary'
PASSWORD = 'cwdsystems'
LOG_FILE = '/path/to/open_canary.log'

def ssh_connect(host, port, username, password):
    """
    Establish SSH connection using paramiko.
    """
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host, port, username, password, timeout=10)
        return client
    except Exception as e:
        print(Fore.RED + f"SSH connection failed: {e}")
        return None

def tail_log_file(ssh_client, log_file):
    """
    Run 'tail -f' on the specified log file via SSH and return stdout stream.
    """
    try:
        stdin, stdout, stderr = ssh_client.exec_command(f'tail -f {log_file}')
        return stdout
    except Exception as e:
        print(Fore.RED + f"Failed to execute tail command: {e}")
        return None

def display_logs(log_stream):
    """
    Process and display log lines with color-coded messages based on log level.
    """
    try:
        for line in log_stream:
            line = line.strip()
            if not line:
                continue

            if re.search(r"\bERROR\b", line):
                print(Fore.RED + line)
            elif re.search(r"\bWARNING\b", line):
                print(Fore.YELLOW + line)
            elif re.search(r"\bINFO\b", line):
                print(Fore.GREEN + line)
            else:
                print(line)
    except KeyboardInterrupt:
        print(Fore.BLUE + "\nStopped log streaming.")
    except Exception as e:
        print(Fore.RED + f"Error while displaying logs: {e}")

if __name__ == '__main__':
    HOST = input("Enter the IP address of the OpenCanary server: ").strip()
    PORT = 22  # Default SSH port

    # Validate IP address format
    if not re.match(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$", HOST):
        print(Fore.RED + "Invalid IP address format.")
    else:
        ssh_client = ssh_connect(HOST, PORT, USERNAME, PASSWORD)

        if ssh_client:
            log_stream = tail_log_file(ssh_client, LOG_FILE)
            if log_stream:
                try:
                    display_logs(log_stream)
                finally:
                    print(Fore.BLUE + "Closing SSH connection.")
                    ssh_client.close()
        else:
            print(Fore.RED + "Unable to establish SSH connection.")
