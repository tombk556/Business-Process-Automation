.. Business Process Automation documentation master file, created by
   sphinx-quickstart on Mon Jun 17 13:59:02 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

BPA SS24 Code Dokumentation!
=======================================================
**Authors**: Konrad Adamski, Tom Bischopink, Jessica Knick, Jakob Laufer, Tom Marinovic, Fabian Kuhne

Introduction
------------

Welcome to the documentation for BPA SS24. This documentation provides an overview of the code structure, usage examples, and detailed explanations of each module and function.

About This Project
------------------

The BPA SS24 code is a Python package that provides a set of tools for handling data from various sources, including OPCUA servers, MQTT brokers and AAS shells. The code is designed to be easy to use and flexible, allowing users to quickly and easily access and manipulate data from different sources.

Getting Started
---------------

Please install Python 3.9 or higher.

**Create Virtual Environment**

.. code-block:: bash

   python3.9 -m venv .venv

**Activate Virtual Environment**

.. code-block:: bash

   source .venv/bin/activate

**Install requirements.txt**

.. code-block:: bash

   pip install -r requirements.txt

**Add .env file**

- create a **.env** file
- put the following credentials into the .env file

.. code-block:: bash

   OPCUA_URL_MOCKUP=...
   OPCUA_URL=...
   AAS_URL=...
   MQTT_URL=...
   MQTT_PORT=...

**Start the Flask-App**

.. code-block:: bash

   python3 app.py

Open the following URL: **http://127.0.0.1:3000**

**Run the OPCUA Simulation Server**

.. code-block:: bash

   cd Simulation

   python3 OPC_UA_SimServer.py


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   modules

   
Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
