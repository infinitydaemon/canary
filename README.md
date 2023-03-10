 <p align="center">
 <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://cwd.systems/img/canary1.png">
    <img src="https://cwd.systems/img/canary1.png"  alt="CWD Canary">
  </picture>
  </p>
  <br>
  <p align="center">
<strong>CWD Canary Appliance Rev 1.0</strong><img height="40" src="https://emoji.gg/assets/emoji/7333-parrotdance.gif"> <br> 
 <br>
<strong> CWD SYSTEMS & Thinkst Applied Research </strong><br>
</p>

```python
class CWD_CANARY():
    
  def __init__(self):
    self.name = "cwd";
    self.username = "cwdsystems";
    self.location = "USA, Canada, Pakistan, KyrgzRepublic, Indonesia";
    self.protonmail = "@cwdsystems";
    self.web = "https://cwd.systems";
    self.languages ="Python,C";
  
  def __str__(self):
    return self.name

if __name__ == '__main__':
    me = CWD_CANARY()
```
Overview <br>
----------

In essence, OpenCanary creates a network honeypot allowing you to catch hackers before they fully compromise your systems. As a technical definition, OpenCanary is a daemon that runs several canary versions of services that alerts when a service is (ab)used. A simple example of CWD Canary implementation would be in a government or a large organizations where scale management requires a lot of network administration and manual intervention. CWD Canary will alert the designated staff about malicious activity before a malware or ransomware attack is set. 

Features
----------

* Receive email alerts as soon as potential threats are detected, highlighting the threat source IP address and where the breach may have taken place. Google's Gmail has stopped accepting so called Less Secure Apps so that won't work. The workaround has been applied by CWD SYSTEMS in its appliance.
<p align="center">
 <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://cwd.systems/img/canary2.png">
    <img src="https://cwd.systems/img/canary2.png"  alt="CWD Canary">
  </picture>
  </p>

Prerequisites
----------------

* Python 3.7 as 2.x will not be supported in the very near future.
* SNMP requires the Python library scapy
* [Mandatory] SMTP server to recieve real-time email alerts or email-to-SMS (if supported by your Telecom operator)
* A TLS based SMTP server

Installation Linux
------------------

For Debian based distros only,

```
$ sudo apt-get install python3-dev python3-pip python3-virtualenv python3-venv python3-scapy libssl-dev libpcap-dev
$ sudo apt install samba # if you plan to use the smb module
$ virtualenv env/
$ . env/bin/activate
$ pip install opencanary
$ pip install scapy pcapy
```

Canary is started by running:

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
2. ~/.opencanary.conf (i.e. the home directory of the user, usually this will be root so /home/user/.opencanary.conf)
3. /etc/opencanary/opencanary.conf

It will use the first config file that exists.

Sample Email Alert <br>
------------
```
{"dst_host": "10.3.1.27", "dst_port": "22", 
"local_time": "2023-02-04 07:21:50.860949",
"local_time_adjusted": "2023-02-04 07:21:50.861096",
"logdata": {"CWR": "", "DF": "", 
"ECE": "", "ID": "0", "IN": "eth0", "LEN": "64", 
"MAC": "e4:5f:01:a0:15:e6:9c:1e:95:3a:7b:a0:08:00",
"OUT": "", "PREC": "0x00", "PROTO": "TCP", "RES": "0x00",
"SYN": "", "TOS": "0x00", "TTL": "49",
"URGP": "0", "WINDOW": "65535"}, "logtype": 5001,
"node_id": "cwd-1", "src_host": "51.17.2.152", 
"src_port": "23087", "utc_time": "2023-02-04 07:21:50.861053"}
```
