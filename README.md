OpenCanary on CWD Appliance
===========================
CWD SYSTEMS & Thinkst Applied Research

Overview
----------

In essence, OpenCanary creates a network honeypot allowing you to catch hackers before they fully compromise your systems. As a technical definition, OpenCanary is a daemon that runs several canary versions of services that alerts when a service is (ab)used.

Features
----------

* Receive email alerts as soon as potential threats are detected, highlighting the threat source IP address and where the breach may have taken place. Google's Gmail has stopped accepting so called Less Secure Apps so that won't work. 

Prerequisites
----------------

* Python 3.7 as 2.x will not be supported in the very near future.
* SNMP requires the Python library scapy
* RDP requires the Python library rdpy~ (this module has been removed; we are currently determining a way forward with this.)
* [Optional] Samba module needs a working installation of samba
* [Mandatory] SMTP server to recieve real-time email alerts or email-to-SMS (if supported by your Telecom operator)

Installation Linux
------------------

For Debian based distros,

```
$ sudo apt-get install python3-dev python3-pip python3-virtualenv python3-venv python3-scapy libssl-dev libpcap-dev
$ sudo apt install samba # if you plan to use the smb module
$ virtualenv env/
$ . env/bin/activate
$ pip install opencanary
$ pip install scapy pcapy
```

OpenCanary is started by running:

```
$ . env/bin/activate
$ opencanaryd --start
```

On the first run, instructions are printed that will get to a working config.

```
$ opencanaryd --copyconfig
```

Which will create a folder, `/etc/opencanary` and a config file inside that folder `opencanary.conf`. You must now edit the config file to determine which services and logging options you would like to enable.

When OpenCanary starts it looks for config files in the following order:

1. ./opencanary.conf (i.e. the directory where OpenCanary is installed)
2. ~/.opencanary.conf (i.e. the home directory of the user, usually this will be root so /root/.opencanary.conf)
3. /etc/opencanary/opencanary.conf

It will use the first config file that exists.

Samba Setup (optional)
----------------------
This is required for the `smb` module.

Head over to our step by step wiki over [here](https://github.com/thinkst/opencanary/wiki/Opencanary-and-Samba)

FAQ
---
We have a FAQ over [here](https://github.com/thinkst/opencanary/wiki)
