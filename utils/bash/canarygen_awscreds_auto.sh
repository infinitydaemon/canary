#!/bin/bash

export console=ab1234ef.canary.tools
export token=deadbeef02082f1ad8bbc9cdfbfffeef
export tokenmemo="Fake AWS Creds on host: $HOSTNAME username: $USER"
export flock='Default+Flock'
export filepath=~
export filedate=$(date "+%Y%m%d%H%M%S")

flockid=$(curl -s "https://${console}/api/v1/flocks/filter?auth_token=${token}&filter_str=${flock}" | grep -Eo '"flock_id":.*?[^\\]",' | awk -F '[":"]' '{print $5,$6}' OFS=":")
awscreds=$(curl -s https://$console/api/v1/canarytoken/create \
  -d auth_token=$token \
  -d memo="$tokenmemo" \
  -d kind=aws-id \
  -d flock_id=$flockid | grep -Eo '"aws-id":.*?[^\\]",' | awk -F '[":"},]' '{print $5,$6}')

# Write the token to a local text file
printf '%s\n' "$awscreds" > "$filepath/awscreds_$filedate.txt"
printf '\nCreds written to %s/awscreds_%s.txt\n' "$filepath" "$filedate"

# for security reasons, we should unset/wipe all variables that contained an auth token, or evidence of Canary/Canarytokens
unset console
unset token
unset tokenmemo
unset flock
unset flockid

exit
