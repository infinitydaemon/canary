#!/bin/bash

CONF="/etc/opencanaryd/opencanary.conf"
OPENCANARYD="/home/cwd/env/bin/opencanaryd"

# Check if the main configuration file exists
if [ -f "$CONF" ]; then
    echo "INFO: Main configuration file found at $CONF"
    # Start the OpenCanary daemon
    if [ -x "$OPENCANARYD" ]; then
        "$OPENCANARYD" --start
    else
        echo "ERROR: $OPENCANARYD does not exist or is not executable. Exiting."
        exit 1
    fi
else
    # Generate the configuration file if it doesn't exist
    if opencanaryd --copyconfig >/dev/null 2>&1; then
        echo "INFO: A config file was generated at /etc/opencanaryd/opencanary.conf"
        echo "INFO: Re-run the script to start the canary daemon"
    else
        echo "ERROR: Failed to generate config file. Exiting."
        exit 1
    fi
fi
