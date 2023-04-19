import os
import datetime
import requests
import csv

# Define variables
token = "a1bc3e769fg832hij3" # Enter your API auth key. e.g a1bc3e769fg832hij3 Docs available here. https://help.canary.tools/hc/en-gb/articles/360012727537-How-does-the-API-work-
console = "1234abc.canary.tools" # Enter your Console domain between the quotes. e.g. 1234abc.canary.tools
dateformat = "1990-01-01-00:00:00" # Enter starting date of Alerts to retrieve e.g. YYYY-MM-DD-HH:MM:SS

filedate = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
filename = f"{filedate}-{console}-alert-export.csv"
baseurl = f"https://{console}/api/v1/incidents/all?auth_token={token}&shrink=true&newer_than={dateformat}"

# Retrieve alert data from the Canary API and write to CSV file
response = requests.get(baseurl)
alerts = response.json()["incidents"]
with open(filename, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Datetime", "Alert Description", "Target", "Target Port", "Attacker", "Attacker RevDNS"])
    for alert in alerts:
        description = alert["description"]
        created_std = alert["created_std"]
        dst_host = alert["dst_host"]
        dst_port = alert["dst_port"]
        src_host = alert["src_host"]
        src_host_reverse = str(alert["src_host_reverse"])
        writer.writerow([created_std, description, dst_host, dst_port, src_host, src_host_reverse])
