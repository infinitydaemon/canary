#!/bin/bash

rm -rf outside* canary-ips-*.txt

curl -XGET https://$CANARY_HASH.canary.tools/api/v1/incidents/outside_bird/download/json \
  -d auth_token=$CANARY_API_KEY \
  -d node_id=$BIRD_ID \
  -G -O -J \
  && unzip outside_bird_alerts.json.zip \
  && cat outside-bird-$BIRD_ID.json | jq '.[].ip_address' | sed 's/\"//g' | sort > canary-ips-$(date +%Y-%m-%d).txt

file="canary-ips-$(date +%Y-%m-%d).txt"
lines=$(cat $file)

for line in $lines
do
	curl "https://api.shodan.io/shodan/host/$line?key={$SHODAN_API_KEY}" | jq '.' | cat >> Canary-Shodan-Threat-Intel-Report-$(date +%Y-%m-%d).json
done
