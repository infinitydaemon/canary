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
    self.location = "KyrgzRepublic";
    self.protonmail = "@cwdsystems";
    self.web = "https://cwd.systems";
    self.languages ="Python,Bash,C";
  
  def __str__(self):
    return self.name

if __name__ == '__main__':
    me = CWD_CANARY()
```
Overview <br>
----------

CWD Canary is a specialized honeypot solution designed for detecting and mitigating cyber threats within network environments. Tailored to the needs of security-conscious organizations, CWD Canary operates by emulating various network services and devices to lure potential attackers, allowing for the monitoring and analysis of their activities.

Honeypot Architecture: CWD Canary utilizes a sophisticated architecture that mimics legitimate network assets, such as servers, routers, and IoT devices, to create an enticing target for attackers. By simulating these services, CWD Canary effectively draws in malicious actors and provides insights into their tactics and techniques.

Decoy Services: CWD Canary offers a range of decoy services, including SSH, HTTP, FTP, and others, which can be customized and configured to match the specific needs of the network environment. These decoy services are designed to closely resemble their genuine counterparts, enhancing the believability of the honeypot.

Logging and Analysis: CWD Canary captures detailed logs of all interactions with decoy services, recording information such as IP addresses, connection attempts, commands executed, and payloads transmitted. These logs are invaluable for analyzing attacker behavior, identifying emerging threats, and informing incident response efforts.

Alerting Mechanisms: CWD Canary incorporates robust alerting mechanisms to promptly notify security personnel of suspicious activity. Alerts can be configured based on predefined thresholds and criteria, ensuring that potential threats are identified and addressed in a timely manner.

Customization Options: CWD Canary provides extensive customization options, allowing administrators to tailor the honeypot's behavior to suit their unique security requirements. This includes the ability to define custom protocols, deploy additional sensors, and fine-tune logging and alerting settings.

Integration Capabilities: CWD Canary seamlessly integrates with existing security infrastructure, enabling organizations to leverage its capabilities alongside other security tools and technologies. Integration with SIEM platforms, threat intelligence feeds, and incident response systems enhances visibility and coordination across the security ecosystem.

Scalability and Performance: CWD Canary is designed to scale gracefully to accommodate the needs of both small and large-scale deployments. Its lightweight footprint and efficient resource utilization ensure minimal impact on network performance while maximizing detection capabilities.

Continuous Improvement: CWD Canary benefits from ongoing development and support, with regular updates and enhancements to address emerging threats and vulnerabilities. The CWD Canary community actively contributes to its evolution, sharing insights, best practices, and additional features to strengthen its effectiveness.

Summary
----------

In summary, CWD Canary is a powerful tool for proactive threat detection and defense, offering advanced capabilities for monitoring and analyzing malicious activity within network environments. Its flexible architecture, extensive customization options, and seamless integration make it a valuable asset for organizations seeking to enhance their cybersecurity posture.

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
```bash
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
Samba Setup (preconfigured)
--------------------------
This is required for the `smb` module. Without the configured daemon, canary will throw error and fail to start. 
