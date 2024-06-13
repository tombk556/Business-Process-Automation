# Business Process Automation - Application 

© 2024 Hochschule für Wirtschaft und Technik Dresden. All rights reserved.

**Authors: Konrad Adamski, Tom Bischopink**

Co-Authors: Jessica Knick, Jakob Laufer, Tom Marinovic, Fabian Kuhne

Supervisor: Professor Dr. Dirk Reichelt

## Setup for Development

Please install Python 3.9 or higher.

### Create Virtual Environment

```bash
python3.9 -m venv .venv
```

### Acitvate Virtual Environment

```bash
Source .venv/bin/activate
```

### Install requirements.txt

```bash
pip install -r requirements.txt
```

### Add .env variables

- create a **.env** file
- put the following credentials into the .env file

```bash
OPCUA_URL_MOCKUP=...
OPCUA_URL=...
AAS_URL=...
MQTT_URL=...
MQTT_PORT=...
```

### Start the Flask-App

```bash 
python3 app.py
```

Open the following URL: **http://127.0.0.1:5000**


### Run docker-compose up:
- create a **.env** file
- put the following credentials into the .env file

```bash
OPCUA_URL_MOCKUP=...
OPCUA_URL=...
AAS_URL=...
MQTT_URL=...
MQTT_PORT=...
```
### Run docker-compose up

```bash
docker-compose up
```

## Run the OCUA-Simulationserver

```bash 
cd Simulation

python3 OPC_UA_SimServer.py
```

## Sphinx-Documentation

```bash
pip install sphinx 
```
Run the commands to generate the documentation:

```bash
cd docs 

sphinx-apidoc -o source/ ../src/ -f -e -M

make html

sphinx-build -b pdf source build/pdf
```

