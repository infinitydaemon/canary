# Delete Tokens
# delete_tokens.py
# Authors: Initially written by Jay then updated by Adrian to Python3. Improved and updated by  CWD SYSTEMS
#
# WARNING!!!!!  
#
# Be VERY careful with this script! It is designed to wipe out all tokens 
# after some heavy automated API testing. Don't use it if you have any
# production tokens that you've worked hard to create and deploy - you'll
# lose them and will have to redeploy!
#

import requests
import sys

def delete_all_canary_tokens(console_url, api_key):
    get_url = f"{console_url}/api/v1/canarytokens/fetch?auth_token={api_key}"
    resp = requests.get(get_url)
    resp_obj = resp.json()
    
    print("Current tokens on your console")
    print("-----------------------------------------------------------------------------------")
    print("kind\t\ttoken\t\t\t\t\tmemo")
    print("-----------------------------------------------------------------------------------")
    
    for token in resp_obj['tokens']:
        print("{}\t\t{}\t\t{}".format(token['kind'], token['canarytoken'], token['memo']))
        
    print("-----------------------------------------------------------------------------------")
    
    user_input = input("Are you sure you would like to delete all your Canarytokens? [Y\\n] PLEASE NOTE: This is irreversible!  ")
    
    if user_input != 'Y':
        print("Not deleting any canarytokens from your Canary console.")
        return
    
    delete_url = f"{console_url}/api/v1/canarytoken/delete"
    
    for token in resp_obj['tokens']:
        print(f"Deleting {token['canarytoken']}: {token['kind']}")
        data = {
            'auth_token': api_key,
            'canarytoken': token['canarytoken']
        }
        resp = requests.post(delete_url, data=data)
        
    print("-----------------------------------------------------------------------------------")
    print("All deleted. Go create some more! They're on us ;)")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("usage: python delete_tokens.py <console_url> <api_key>")
        sys.exit(1)

    console_url = sys.argv[1]
    api_key = sys.argv[2]
    delete_all_canary_tokens(console_url, api_key)
