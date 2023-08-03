from sap_client import get_sap_client
from fastapi import APIRouter, Depends
from suds.client import Client
import json


router = APIRouter()

api_version = "v1"

@router.get(f"/api/{api_version}/client")
def get_client_info(sap_client: Client = Depends(get_sap_client)):
    """
    Obtiene información del cliente SAP
    """
    print(sap_client)
    
    return {"sap_client": "activo"}

@router.get(f"/api/{api_version}/orders")
async def check_episode_billed(sap_client: Client = Depends(get_sap_client)):
    # Código para consumir CheckEpisodeBilled
    sap_response = sap_client.service[0].ZppfmSelectOrders("F")
    print(sap_response)
    orders = json.loads(sap_response['EJsonOrdens'])
    components = json.loads(sap_response['EJsonCompon'])
    # Process each order and its corresponding components
    data = {
        "orders": orders,
        "components": components
    }
    # Create a dictionary to store the transformed data
    result = {}
    for order in data["orders"]:
        order_number = order["aufnr"]
        components = [component for component in data["components"] if component["aufnr"] == order_number]
        order["components"] = components
        result[order_number] = order

    # Create a new structure containing the orders and their components
    response = list(result.values())
    
    return response