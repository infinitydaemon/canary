OpenCanary on CWD Appliance
===========================
CWD SYSTEMS & Thinkst Applied Research

Overview
----------

In essence, OpenCanary creates a network honeypot allowing you to catch hackers before they fully compromise your systems. As a technical definition, OpenCanary is a daemon that runs several canary versions of services that alerts when a service is (ab)used.

Features
----------

* Receive email alerts as soon as potential threats are detected, highlighting the threat source IP address and where the breach may have taken place.

Prerequisites
----------------

* Python 3.7 as 2.x will not be supported in the very near future.
* SNMP requires the Python library scapy
* RDP requires the Python library rdpy~ (this module has been removed; we are currently determining a way forward with this.)
* [Optional] Samba module needs a working installation of samba

Installation Linux
------------------

For Debian based distros,

```
$ sudo apt-get install python3-dev python3-pip python3-virtualenv python3-venv python3-scapy libssl-dev libpcap-dev
$ sudo apt install samba # if you plan to use the smb module
$ virtualenv env/
$ . env/bin/activate
$ pip install opencanary
$ pip install scapy pcapy rdpy
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

Docker Compose
----------------

> Requires [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) installed.

1. Edit the `data/.opencanary.conf` file to enable, disable or customize the services that will run.

1. Edit the `ports` section of the `docker-compose.yml` file to enable/disable the desired ports based on the services you have enabled in the config file.

1. Build and run the container.

    To run the latest Docker image (based on the code on a given branch) run:
    ```bash
    docker-compose up -d --build latest
    ```
    To run a Docker image based on what has been released in Pypi, run:
    ```bash
    docker-compose up -d --build stable
    ```

> To view the logs run `docker-compose logs latest` or `docker-compose logs stable`

> To stop the container run `docker-compose down`

Docker
----------------

> Requires [Docker](https://docs.docker.com/get-docker/) installed.

1. Edit the `data/.opencanary.conf` file to enable, disable or customize the services that will run.

1. Build a Docker image to run.
    
    To build the latest Docker image (based on the code on a given branch) run:

    ```bash
    docker build -t opencanary -f Dockerfile.latest .
    ```

    To build a Docker image based on what has been released in Pypi, run:

    ```bash
    docker build -t opencanary -f Dockerfile.stable .
    ```

1. Run the docker image with the following command:

```bash
# You will need to add/remove the ports you are using by listing them with `-p ##:##`
docker run --rm --detach -p 21:21 -p 80:80 -v "${PWD}/data/.opencanary.conf":"/root/.opencanary.conf" --name opencanary opencanary
```

> To view the logs run `docker logs opencanary`

> To stop the container run `docker stop opencanary`
