import json
import os

from sap_client import get_sap_client

from fastapi import APIRouter, Depends
from dotenv import load_dotenv

from suds.client import Client

load_dotenv()

# Package para Conexión a Oracle
from syncoracle.connect import connect_to_oracle

# Package para Conexión a Microsoft SQL Server
from syncmssql.connect import connect_to_mssql

from utils import consolidate_result, jsonify_db_response

# Cargamos las variables de entorno para conexión a Micorosft SQL Server
SERVER_MSSQL = os.getenv("SERVER_MSSQL")
DATABASE_MSSQL = os.getenv("DATABASE_MSSQL")
USER_MSSQL = os.getenv('USER_MSSQL')
PASSWORD_MSSQL = os.getenv('PASSWORD_MSSQL')

cnxn_mssql, cursor_mssql = connect_to_mssql(server = SERVER_MSSQL, database = DATABASE_MSSQL, username = USER_MSSQL, password = PASSWORD_MSSQL)


USER_ORACLE = os.getenv('USER_ORACLE')
PASSWORD_ORACLE = os.getenv('PASSWORD_ORACLE')
DSN_ORACLE = os.getenv('DSN_ORACLE')

try:
    cursor_oracle = connect_to_oracle(USER_ORACLE, PASSWORD_ORACLE, DSN_ORACLE)
except:
    print("Error al crear cursor de oracle")

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


@router.get(f"/api/{api_version}/test-result")
async def test_results(barcode: str):
    query = '''
    SELECT TOP (1000) 
            rh.[SEQNO]
            ,rh.[BARCODE]
            ,rh.[DATE_TESTED]
            ,rh.[UNIT_ID]
            ,rh.[DEVICE_ID]
            ,rh.[LINE_ID]
            ,rh.[WORKSHIFT_ID]
            ,rh.[MODEL_ID]
            ,rh.[FAILCODE]
            ,fc.[DESCRIPTOR] AS [FAILCODE_DESCRIPTOR]
            ,fc.[CODE_TYPE]
            ,rh.[LIMITS_ID]
            ,rh.[LIMITS_HISTORY_ID]
            ,rh.[STATUS]
            ,rh.[AREA_ID]
            ,rh.[LIMITTYPE_ID]
            ,rh.[COMPLETE]
            ,rh.[LIMITS_DESCRIPTOR]
            ,rh.[DATE_START_TEST]
            ,rh.[SYNC_DATE]
            ,rh.[PROCESSOR_ID]
            ,lh.[DESCRIPTOR] AS [LIMITS_DESCRIPTOR]
        FROM [PLIS].[dbo].[RESULTS_HEADER] rh
        JOIN [PLIS].[dbo].[FAILCODES] fc ON rh.[FAILCODE] = fc.[ID] AND rh.[DEVICE_ID] = fc.[DEVICE_ID]
        LEFT JOIN [PLIS].[dbo].[LIMITS_HEADER] lh ON rh.[LIMITS_ID] = lh.[LIMITS_ID] AND rh.[LIMITS_HISTORY_ID] = lh.[HISTORY_ID]
        WHERE rh.[BARCODE] = ?
        ORDER BY rh.[DATE_TESTED] DESC
    '''
    cursor_mssql.execute(query, barcode)
    row_headers = [x[0] for x in cursor_mssql.description]
    json_data = []
    rows = cursor_mssql.fetchall()
    for result in rows:
        json_data.append(dict(zip(row_headers,result)))

    json_response = consolidate_result(json_data)
    return json_response

@router.get(f"/api/{api_version}/material-metadata")
async def get_material_metadata(id_material: str):
    # Query SQL
    query = """
            SELECT vcm.*, cm.*, v.*
            FROM valorescaractmateriais vcm
            JOIN caractmateriais cm ON vcm.ID_CARACTMATERIAL = cm.ID_CARACTMATERIAL
            JOIN valpossiveiscaractmateriais v ON vcm.ID_VALORCARACTMAT = v.ID_VALORCARACTMAT
            WHERE vcm.ID_MATERIAL = :id_material
        """

    # Ejecuta la consulta con el ID de material proporcionado
    cursor_oracle.execute(query, id_material=id_material)

    response = jsonify_db_response(cursor_oracle)
    cursor_oracle.close()
    return response