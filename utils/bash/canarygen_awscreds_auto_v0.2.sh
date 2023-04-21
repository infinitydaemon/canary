#!/bin/bash

console=ab1234ef.canary.tools
token=deadbeef02082f1ad8bbc9cdfbfffeef
tokenmemo="Fake AWS Creds on host: $HOSTNAME username: $USER"
flock='Default+Flock'
filepath=~
filename='credentials.txt'
filedate=$(date "+%Y%m%d%H%M%S")
flockid=$(curl -s -k "https://${console}/api/v1/flocks/filter?auth_token=${token}&filter_str=${flock}" | grep -Eo '"flock_id":.*?[^\\]",' | awk -F '[":"]' '{print $5,$6}' OFS=":")
echo -e "\nFlockID is $flockid"

echo -e "Creating token"
awscreds=$(curl -s https://$console/api/v1/canarytoken/create \
  -d auth_token=$token \
  -d memo="'$tokenmemo'" \
  -d kind=aws-id \
  -d flock_id=$flockid)

# Write the token to a local text file
echo "[default]" > "$filepath/$filename"
echo $awscreds | grep -oE "aws_access_key_id = .{20}" >> "$filepath/$filename"
echo $awscreds | grep -Eo "aws_secret_access_key = .{40}" >> "$filepath/$filename"
echo -e "\nCreds written to $filepath/$filename"

# for security reasons, we should unset/wipe all variables that contained an auth token, or evidence of Canary/Canarytokens
unset console
unset token
unset tokenmemo
unset flock
unset ping
unset flockid
unset filename

exit
