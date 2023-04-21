# CanaryToken_UploadtoS3.py
# Make sure AWS Boto3 is installed with "pip install boto3"
# Make sure the requests package is installed with "pip install requests"

# Imports
import requests
import os
import re
import socket
import json
import boto3
from botocore.exceptions import NoCredentialsError

# Variables

DOMAIN = 'XXXXXX.canary.tools'  # Enter your Console domain between the . e.g. 1234abc.canary.tools
FACTORYAUTH = 'XXXXX'  # Enter your Factory auth key. e.g a1bc3e769fg832hij3 Docs available here. https://docs.canary.tools/canarytokens/factory.html#create-canarytoken-factory-auth-string
MEMO = socket.gethostname() + ' S3 Token Upload'
TOKENTYPE = 'aws-id'  # Enter your required token type. Full list available here. https://docs.canary.tools/canarytokens/factory.html#list-canarytokens-available-via-canarytoken-factory
ACCESS_KEY = 'YOUR_ACCESS_KEY'
SECRET_KEY = 'YOUR_SECRET_KEY'

# Create token on console

create_url = 'https://' + DOMAIN + '/api/v1/canarytoken/factory/create'

payload = {
    'factory_auth': FACTORYAUTH,
    'memo': MEMO,
    'kind': TOKENTYPE
}

token_creation = requests.post(create_url, data=payload)
token_creation_result = token_creation.json()
token_id = token_creation_result["canarytoken"]["canarytoken"]

# Download token locally

download_url = 'https://' + DOMAIN + '/api/v1/canarytoken/factory/download'

payload = {
    'factory_auth': FACTORYAUTH,
    'canarytoken': token_id
}

download_request = requests.get(download_url, allow_redirects=True, params=payload)
filename = re.findall("filename=(.+)", download_request.headers["Content-Disposition"])[0]
with open(filename, 'wb') as f:
    f.write(download_request.content)

# Upload token to S3

def upload_to_aws(local_file, bucket, s3_file):
    s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
    try:
        s3.upload_file(local_file, bucket, s3_file)
        print("Upload Successful")
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False

uploaded = upload_to_aws(filename, 'YOUR_BUCKET_NAME', 'YOUR_FILE_NAME')

# Clean up local token.

os.remove(filename)

# User feedback.

print("Token Upload to S3 complete")
