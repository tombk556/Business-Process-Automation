import json

# Pfad zur JSON-Datei
dateipfad = 'Inspection_Plan.json'

# JSON-Datei öffnen und laden
with open(dateipfad, 'r') as datei:
    daten = json.load(datei)

# Jetzt sind die Daten in der Variable 'daten' gespeichert
print(daten)
