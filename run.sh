#!/bin/bash

CONF="/etc/opencanaryd/opencanary.conf"

if [ -f "$CONF" ]; then
    echo "INFO: Main configuration file found"
    /home/cwd/env/bin/opencanaryd --start
else
    if opencanaryd --copyconfig >/dev/null 2>&1; then
        echo "INFO: A config file was generated at /etc/opencanaryd/.opencanary.conf"
        echo "INFO: Re-run the script to start the canary daemon"
    else
        echo "ERROR: Failed to generate config file. Exiting."
        exit 1
    fi
fi
