import paramiko
import time
from colorama import Fore, Style, init

init(autoreset=True)

USERNAME = 'canary'
PASSWORD = 'cwdsystems'
LOG_FILE = '/path/to/open_canary.log'

def ssh_connect(host, port, username, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, port, username, password)
    return client

def tail_log_file(ssh_client, log_file):
    stdin, stdout, stderr = ssh_client.exec_command(f'tail -f {log_file}')
    return stdout

def display_logs(log_stream):
        for line in log_stream:
            if "ERROR" in line:
                print(Fore.RED + line.strip())
            elif "WARNING" in line:
                print(Fore.YELLOW + line.strip())
            elif "INFO" in line:
                print(Fore.GREEN + line.strip())
            else:
                print(line.strip())

if __name__ == '__main__':
    HOST = input("Enter the IP address of the OpenCanary server: ")
    PORT = 22  # Default SSH port

    try:
        ssh_client = ssh_connect(HOST, PORT, USERNAME, PASSWORD)
        log_stream = tail_log_file(ssh_client, LOG_FILE)
        display_logs(log_stream)
    except Exception as e:
        print(Fore.RED + f"Error: {e}")
    finally:
        ssh_client.close()
