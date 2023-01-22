#! /bin/bash

CONF="/etc/opencanaryd/opencanary.conf"

if [ -f $CONF ]; then
	echo "INFO: Main configuration file found"
	env/bin/opencanaryd --start
else
	opencanaryd --copyconfig && echo "A Config file was generated at /etc/opencanaryd/.opencanary.conf."
	echo "INFO: Re-run the script to start the canary daemon"
fi

