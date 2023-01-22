CWD Canary
===========

Welcome to the OpenCanary guide.

Please note we have a wiki on Github with FAQ and Samba Setup help over `here <https://github.com/infinitydaemon>`_.

OpenCanary is a daemon that runs canary services, which trigger alerts
when (ab) is used. The alerts can be sent to a variety of sources,
including Syslog, emails, and a companion daemon opencanary-correlator.

This project is maintained by `CWD SYSTEMS <https://cwd.systems>`_.

The Correlator coalesces multiple related events (eg. individual
brute-force login attempts) into a single alert sent via email or
SMS.


.. _getting-started:

Getting Started
---------------

The first section will get you quickly up and running with canary
services sending alerts.

.. toctree::
   :maxdepth: 1

   starting/opencanary
   starting/configuration
   starting/correlator

Services
---------

Try these out in the OpenCanary configs for more typical server personalities.

.. toctree::
   :maxdepth: 1

   services/webserver
   services/windows
   services/mysql
   services/mssql


Alerting
---------

:ref:`getting-started` walks through two different ways to configure alerting: logging directly to a file, and sending alerts to the Correlator for email and SMS alerts. Other possibilities are below:

.. toctree::
   :maxdepth: 2

   alerts/email
   alerts/hpfeeds
   alerts/webhook


Upgrading
---------

If you have a previous version of OpenCanary installed already, you can upgrade it easily.

Start by activating your virtual environment (`env` in the below example) that has your installed version of OpenCanary,

.. code-block:: sh

   $ . env/bin/activate


Inside the virtualenv, you can upgrade your OpenCanary by,

.. code-block:: sh

  $ pip install opencanary --upgrade
  This method is not applicable for CWD Canary appliance. The updates are pushed remotely as part of SLA and is deemed mandatory.

Please note that this will not wipe your existing OpenCanary config file. If you would like a new one (with the new settings), please regenerate the config file using,

.. code-block:: sh

  $ opencanaryd --copyconfig



Indices and tables
------------------
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
