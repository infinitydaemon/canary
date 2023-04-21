#!/bin/bash

if ! command -v curl &> /dev/null || ! command -v jq &> /dev/null; then
    echo "curl and jq are required to run this script. Please install them first."
    exit 1
fi

read -r -p "Enter your API token: " token

export token
export console="ABC123.canary.tools"
export filename="$console-tokens.csv"
export baseurl="https://$console/api/v1/canarytokens/fetch?auth_token=$token"

echo "created_std,kind,memo" > "$filename"
curl -s "$baseurl" | jq -r '.tokens[] | [.created_printable, .kind, .memo | tostring] | @csv' >> "$filename"
echo "Results saved in $filename"
