import os
from suds.client import Client
from dotenv import load_dotenv

load_dotenv()  # Carga las variables de entorno desde el archivo .env

USERNAME = os.getenv("SAP_USERNAME")
PASSWORD = os.getenv("SAP_PASSWORD")

def get_sap_client():
    wsdl_url = "http://sapeccqas.embraco.com/sap/bc/srt/wsdl/flv_10002A1011D1/bndg_url/sap/bc/srt/scs/sap/zppws_palletizing?sap-client=100"
    client = Client(url=wsdl_url, username=USERNAME, password=PASSWORD)
    return client