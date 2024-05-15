from dotenv import load_dotenv
import os
load_dotenv()


class Settings:
    def __init__(self):
        self.url = os.getenv("URL")
        self.opcua_url = os.getenv("OPCUA_URL")
        
settings = Settings()