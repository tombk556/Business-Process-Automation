# 1. Registry ansprechen

http://141.56.180.118:8080/shell-descriptors

- anhand von "text", "idShort" (je nach RFID Chip) Item identifizieren
- href extrahieren (bis zum Port)

# 2. AAS ansprechen

## 2.1 Alle Submodells bekommen

http://141.56.180.118:8081/submodels?encodedCursor=string&decodedCursor=string&level=deep&extent=withoutBlobValue

- für Submodel mit idShort "<JSON Prüfplan>" die "id" extrahieren
- die "id" base64 encoden --> "submodelIdentifier"

## 2.2 Abfrage

Paramter:
- submodelIdentifier (von vorhin)
- idShortPath: es ist vergeben vom Team => 'Inspection_Plan'

http://141.56.180.118:8081/submodels/aHR0cHM6Ly9leGFtcGxlLmNvbS9pZHMvc20vODU1NF84MDAxXzQwNDJfMzUyMQ%3D%3D/submodel-elements/Vorlage/attachment


http://141.56.180.118:8081/submodels/<submodelIdentifier>/submodel-elements/<path>/attachment