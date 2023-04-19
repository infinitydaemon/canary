import os
import json
import requests

canary_hash = "your_canary_hash"
canary_api_key = "your_canary_api_key"
bird_id = "your_bird_id"
shodan_api_key = "your_shodan_api_key"

os.system("rm -rf outside* canary-ips-*.txt")

response = requests.get(f"https://{canary_hash}.canary.tools/api/v1/incidents/outside_bird/download/json?auth_token={canary_api_key}&node_id={bird_id}")
with open("outside_bird_alerts.json.zip", "wb") as f:
    f.write(response.content)

os.system("unzip outside_bird_alerts.json.zip")
with open(f"canary-ips-{datetime.datetime.now().strftime('%Y-%m-%d')}.txt", "w") as f:
    ips = sorted(list(set([ip.strip('"') for ip in json.load(open(f"outside-bird-{bird_id}.json"))[0]["outbound_network_traffic"].values() if ip])))
    f.write("\n".join(ips))

# Read through each line of the canary text file, send each IP through the Shodan API, and create a JSON report
with open(f"canary-ips-{datetime.datetime.now().strftime('%Y-%m-%d')}.txt") as f:
    ips = f.read().splitlines()

with open(f"Canary-Shodan-Threat-Intel-Report-{datetime.datetime.now().strftime('%Y-%m-%d')}.json", "w") as f:
    for ip in ips:
        response = requests.get(f"https://api.shodan.io/shodan/host/{ip}?key={shodan_api_key}")
        json.dump(response.json(), f)
        f.write("\n")
