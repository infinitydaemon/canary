import paramiko
import os

def download_canary_logs(ip_address, username, password, local_path):
    try:
        # Establish SSH connection
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(ip_address, username=username, password=password)

        # SCP client for file transfer
        scp_client = ssh_client.open_sftp()

        # Remote file path
        remote_path = '/var/log/opencanary.log'

        # Local file path for saving logs
        local_file_path = os.path.join(local_path, f'{ip_address}_opencanary.log')

        # Download file
        scp_client.get(remote_path, local_file_path)
        print(f"Canary logs downloaded from {ip_address} successfully.")

        # Close SCP and SSH connections
        scp_client.close()
        ssh_client.close()

    except Exception as e:
        print(f"Error: {e}")
        return

def main():
    num_ips = int(input("Enter the number of OpenCanary IP addresses: "))

    for i in range(num_ips):
        ip_address = input(f"Enter IP address {i+1}: ")
        username = input("Enter SSH username: ")
        password = input("Enter SSH password: ")
        local_path = input("Enter local directory to save logs: ")

        # Ensure local path exists
        if not os.path.exists(local_path):
            os.makedirs(local_path)

        download_canary_logs(ip_address, username, password, local_path)

if __name__ == "__main__":
    main()
