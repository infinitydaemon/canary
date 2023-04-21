import requests
import socket
import os

Domain = "ABC123.canary.tools"
FactoryAuth = "ABC123"
FlockID = "flock:default"

def drop_awsid_token():
    token_directory = os.path.expanduser('~')+'/.aws/'
    token_filename = 'config'
    token_type = 'aws-id'
  
    create_token_url = f"https://{Domain}/api/v1/canarytoken/factory/create"
    payload = {
        'factory_auth': FactoryAuth,
        'kind': token_type,
        'flock_id' : FlockID,
        'memo': f"{socket.gethostname()} - {token_directory+token_filename}",
    }
  
    create_token = requests.post(create_token_url, data=payload)
  
    if create_token.status_code != requests.codes.ok:
        print(f"[!] Creation of {token_directory+token_filename} failed.")
        exit()
    else:
        result = create_token.json()
  
    canarytoken_id = result['canarytoken']['canarytoken']
  
    download_token_url = f"https://{Domain}/api/v1/canarytoken/factory/download"
  
    payload = {
        'factory_auth': FactoryAuth,
        'canarytoken': canarytoken_id
    }
  
    fetch_token = requests.get(download_token_url, allow_redirects=True, params=payload)
  
    if fetch_token.status_code != requests.codes.ok:
        print(f"[!] Fetching of {token_directory+token_filename} failed.")
        exit()
    else:
        result = fetch_token.content

    if not os.path.exists(token_directory):
        os.makedirs(token_directory)
  
    if os.path.exists(token_directory+token_filename):
        open(token_directory+token_filename, 'a').write("\n")
        open(token_directory+token_filename, 'ab').write(result)
    else:
        open(token_directory+token_filename, 'wb').write(result)

    print("[*] AWS-API Key Token Dropped")

drop_awsid_token()
