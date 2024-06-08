import json
import requests
from config.env_config import settings
from src.utils.util_functions import encode_to_base64
from requests_toolbelt.multipart.encoder import MultipartEncoder
from src.utils.Logger import SingletonLogger

logger = SingletonLogger()


class AASManager:
    AAS_Registry_URL = settings.aas_url
    ID = "idShort"

    def __init__(self):
        logger.info("Initializing AAS Manager")

    def get_inspection_plan(self, auto_id):
        """
        Get inspection plan by auto_id.
        :param auto_id: The ID of the auto for which to fetch the inspection plan.
        :return: The inspection plan or the auto_id if an error occurs.
        """
        try:
            response = requests.get(self.AAS_Registry_URL)
            if response.status_code == 200:
                asset_href = self._get_asset_href(response.json(), auto_id)
                if asset_href:
                    ip = asset_href.split("/")[2]
                    logger.info(f"IP found in AAS Shell: {ip} for Auto ID: {auto_id}")
                    submodelIdentifier = self._get_submodelIdentifier(ip, "Inspection_Plan")
                    inspection_plan = self._get_attachment(ip, submodelIdentifier, "Inspection_Plan")
                    return inspection_plan
        except Exception as e:
            logger.error(e)
        return None

    def get_inspection_response(self, auto_id):
        """
        Get inspection response by auto_id.
        :param auto_id:
        :return:
        """
        try:
            response = requests.get(self.AAS_Registry_URL)
            if response.status_code == 200:
                asset_href = self._get_asset_href(response.json(), auto_id)
                if asset_href:
                    ip = asset_href.split("/")[2]
                    logger.info(f"IP found in AAS Shell: {ip} for Auto ID: {auto_id}")
                    submodelIdentifier = self._get_submodelIdentifier(ip, "Response_Plan")
                    inspection_plan = self._get_attachment(ip, submodelIdentifier, "Response_Placeholder")
                    return inspection_plan
        except Exception as e:
            logger.error(e)
        return None

    def put_inspection_response(self, auto_id, json_dict):
        """
        Put inspection response (JSON) by auto_id .
        :param auto_id:
        :param json_dict:
        :return:
        """
        try:
            response = requests.get(self.AAS_Registry_URL)
            if response.status_code == 200:
                asset_href = self._get_asset_href(response.json(), auto_id)
                if asset_href:
                    ip = asset_href.split("/")[2]
                    logger.info(f"IP found in AAS Shell: {ip} for Auto ID: {auto_id}")
                    submodelIdentifier = self._get_submodelIdentifier(ip, "Response_Plan")
                    self._put_attachment(ip, submodelIdentifier, "Response_Placeholder",
                                         "InspectionResponse.json", json_dict)

        except Exception as e:
            logger.error(e)
        return None

    def _get_asset_href(self, data, id_short):
        """
        Get asset href by id_short.
        :param data: JSON data from which to find the href.
        :param id_short: The short identifier for the asset.
        :return: The href if found, otherwise None.
        """
        if isinstance(data, dict):
            if data.get(self.ID) == id_short:
                endpoints = data.get("endpoints")
                if endpoints:
                    return endpoints[0].get("protocolInformation", {}).get("href")
            for value in data.values():
                if isinstance(value, (dict, list)):
                    result = self._get_asset_href(value, id_short)
                    if result:
                        return result
        elif isinstance(data, list):
            for item in data:
                result = self._get_asset_href(item, id_short)
                if result:
                    return result
        return None

    def _get_submodelIdentifier(self, aas_ip_port, idShort):
        """
        Fetch the submodel identifier.
        :param aas_ip_port: IP and port for AAS.
        :return: Submodel identifier or None.
        """
        url = f"http://{aas_ip_port}/submodels?encodedCursor=string&decodedCursor=string&level=deep&extent=withoutBlobValue"
        response = requests.get(url)
        submodels = response.json()
        for model in submodels["result"]:
            if model["idShort"] == str(idShort):
                id_base64 = encode_to_base64(model["id"])
                logger.info(f"Submodel Identifier: {id_base64}")
                return id_base64
        logger.warning(f"No submodel identifier found for AAS: {aas_ip_port}")
        return None

    def _get_attachment(self, ip_port, submodelIdentifier, idShortPath):
        """
        Fetch the inspection plan.
        :param ip_port: IP and port for AAS.
        :param submodelIdentifier: Identifier for the submodel.
        :return: Inspection plan if found, otherwise a string indicating no plan was found.
        """
        url = f"http://{ip_port}/submodels/{submodelIdentifier}/submodel-elements/{idShortPath}/attachment"
        submodel_name = idShortPath.replace("_", " ")
        response = requests.get(url)
        if response.status_code == 200:
            inspection_plan = response.json()
            logger.info(f"{submodel_name}: {inspection_plan}")
            return inspection_plan
        else:
            logger.warning(f"No {submodel_name} found for AAS: {ip_port}")
            return None

    def _put_attachment(self, ip_address, submodelIdentifier, idShortPath, ass_file_name, json_data):
        url = f"http://{ip_address}/submodels/{submodelIdentifier}/submodel-elements/{idShortPath}/attachment?fileName={ass_file_name}"
        json_string = json.dumps(json_data, indent=4).encode('utf-8')

        # Multipart/Form-Data Encoder mit dem Dateiinhalt (oder leeren JSON)
        multipart_data = MultipartEncoder(
            fields={
                'file': (ass_file_name, json_string, 'application/json')
            }
        )

        # Die PUT-Anfrage durchführen
        response = requests.put(url, data=multipart_data, headers={'Content-Type': multipart_data.content_type})

        # Antwort prüfen
        if response.status_code == 200:
            print("Attachment erfolgreich hinzugefügt.")
        else:
            print("Fehler beim Hinzufügen des Attachments:", response.status_code, response.text)
