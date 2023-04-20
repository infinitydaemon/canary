import requests
import json
import datetime

DOMAIN = 'ABC123'
APIKEY = 'ABC123'

def ping_console():

    start = datetime.datetime.now()

    print("Benchmarking time to ping Console...")

    url = f'https://{DOMAIN}.canary.tools/api/v1/ping'

    payload = {
        'auth_token': APIKEY
    }

    try:
        response = requests.get(url, params=payload)
        response.raise_for_status()
        data = response.json()
        end = datetime.datetime.now()
        diff = end - start
        print(f"Ping Console complete, time taken: {start} - {end}")
        print(f"Time Taken: {diff}\n")
        with open('Ping_Console_Result.txt', 'w') as export:
            json.dump(data, export, indent=4)
    except requests.exceptions.HTTPError as e:
        print(f"An HTTP error occurred: {e}")

def fetch_devices():

    url = f'https://{DOMAIN}.canary.tools/api/v1/devices/all'

    start = datetime.datetime.now()

    print("Benchmarking time to fetch all device details...")

    payload = {
        'auth_token': APIKEY
    }

    try:
        response = requests.get(url, params=payload)
        response.raise_for_status()
        data = response.json()
        end = datetime.datetime.now()
        diff = end - start
        print(f"Fetch Devices complete, time taken: {start} - {end}")
        print(f"Time Taken: {diff}\n")
        with open('Fetch_Devices_Result.txt', 'w') as export:
            json.dump(data, export, indent=4)
    except requests.exceptions.HTTPError as e:
        print(f"An HTTP error occurred: {e}")

def fetch_tokens():

    url = f'https://{DOMAIN}.canary.tools/api/v1/canarytokens/fetch'

    start = datetime.datetime.now()

    print("Benchmarking time to fetch all Tokens...")

    payload = {
        'auth_token': APIKEY
    }

    try:
        response = requests.get(url, params=payload)
        response.raise_for_status()
        data = response.json()
        end = datetime.datetime.now()
        diff = end - start
        print(f"Fetch Tokens complete, time taken: {start} - {end}")
        print(f"Time Taken: {diff}\n")
        with open('Fetch_Tokens_Result.txt', 'w') as export:
            json.dump(data, export, indent=4)
    except requests.exceptions.HTTPError as e:
        print(f"An HTTP error occurred: {e}")

def fetch_incidents():

    url = f'https://{DOMAIN}.canary.tools/api/v1/incidents/all'

    start = datetime.datetime.now()

    print("Benchmarking time to fetch all Incident data...")

    payload = {
        'auth_token': APIKEY
    }

    try:
        response = requests.get(url, params=payload)
        response.raise_for_status()
        data = response.json()
