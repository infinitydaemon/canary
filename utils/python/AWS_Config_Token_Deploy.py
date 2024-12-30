import requests
import socket
import os

# Constants
DOMAIN = "ABC123.canary.tools"
FACTORY_AUTH = "ABC123"
FLOCK_ID = "flock:default"
TOKEN_DIRECTORY = os.path.expanduser('~') + '/.aws/'
TOKEN_FILENAME = 'config'
TOKEN_TYPE = 'aws-id'

def create_canary_token():
    """Create a new canary token."""
    url = f"https://{DOMAIN}/api/v1/canarytoken/factory/create"
    payload = {
        'factory_auth': FACTORY_AUTH,
        'kind': TOKEN_TYPE,
        'flock_id': FLOCK_ID,
        'memo': f"{socket.gethostname()} - {TOKEN_DIRECTORY}{TOKEN_FILENAME}",
    }
    
    response = requests.post(url, data=payload)
    response.raise_for_status()  # Raises HTTPError for bad responses
    return response.json()['canarytoken']['canarytoken']

def download_canary_token(canarytoken_id):
    """Download the content of the canary token."""
    url = f"https://{DOMAIN}/api/v1/canarytoken/factory/download"
    params = {
        'factory_auth': FACTORY_AUTH,
        'canarytoken': canarytoken_id
    }
    
    response = requests.get(url, allow_redirects=True, params=params)
    response.raise_for_status()
    return response.content

def drop_awsid_token():
    """Drop an AWS ID token into the specified AWS config file."""
    try:
        # Create token
        canarytoken_id = create_canary_token()
        
        # Download token content
        token_content = download_canary_token(canarytoken_id)
        
        # Ensure directory exists
        os.makedirs(TOKEN_DIRECTORY, exist_ok=True)
        
        # Write to file
        file_path = os.path.join(TOKEN_DIRECTORY, TOKEN_FILENAME)
        mode = 'ab' if os.path.exists(file_path) else 'wb'
        with open(file_path, mode) as file:
            if mode == 'ab':
                file.write(b'\n')  # Add newline for appending
            file.write(token_content)
        
        print("[*] AWS-API Key Token Dropped")
    
    except requests.HTTPError as e:
        print(f"[!] Token operation failed: {e}")
        exit(1)
    except Exception as e:
        print(f"[!] An unexpected error occurred: {e}")
        exit(1)

if __name__ == "__main__":
    drop_awsid_token()
