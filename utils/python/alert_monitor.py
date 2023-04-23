logo = """
          _nnnn_
         dGGGGMMb
        @p~qp~~qMb
        M|@||@) M|
        @,----.JM|
       JS^\__/  qKL
      dZP        qKRb
     dZP          qKKb
    fZP            SMMb
    HZM            MMMM
    FqM            MMMM
  __| ".        |\dS"qML
  |    `.       | `' \Zq
 _)      \.___.,|     .'
 \____   )MMMMMM|   .'
      `-'       `--' hjm
"""

print(logo)

import requests
import json
import time
import sys

def main():
    if len(sys.argv) != 3:
        print("Usage: python alert_monitor.py <appliance_url> <auth_token>")
        return

    server_url = sys.argv[1]
    auth_token = sys.argv[2]

    while True:
        try:
            response = requests.get(server_url + '/api/v1/alerts', headers={'Authorization': 'Bearer ' + auth_token})

            if response.status_code == 200:
                alerts = json.loads(response.text)
                if len(alerts) > 0:
                    print("New alert(s) detected:")
                    for alert in alerts:
                        print(alert['timestamp'], alert['description'], alert['src_host'], alert['dst_host'], alert['dst_port'])
            else:
                print("Error: " + response.text)

        except requests.exceptions.RequestException as e:
            print("Connection error:", e)

        time.sleep(10)

if __name__ == "__main__":
    main()
