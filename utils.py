from collections import defaultdict

def consolidate_result(original_response):
    grouped_data = defaultdict(list)
    all_visited = True  # Variable para determinar el global_status

    for item in original_response:
        key = (item['FAILCODE'], item['UNIT_ID'], item['DEVICE_ID'])
        grouped_data[key].append(item)

    new_structure = []

    for group_key, group_items in grouped_data.items():
        # Ordenar el grupo por SYNC_DATE en orden descendente
        group_items.sort(key=lambda x: x['SYNC_DATE'], reverse=True)

        # Tomar el elemento con la SYNC_DATE más reciente como el "padre" del grupo
        parent_item = group_items[0]

        # Verificar el estado de todos los items en el grupo
        group_status = all(item['STATUS'] == 1 for item in group_items)
        if not group_status:
            all_visited = False

        new_item = {
            'label': parent_item['FAILCODE_DESCRIPTOR'],
            'description': parent_item['FAILCODE_DESCRIPTOR'],
            'limit_description': parent_item['LIMITS_DESCRIPTOR'],
            'status': 'visited' if parent_item['STATUS'] == 1 else 'unvisited',
            'start_test': parent_item['DATE_START_TEST'],
            'sync_date': parent_item['SYNC_DATE']
        }
        new_structure.append(new_item)

    # Agregar las claves results y global_status
    result = {
        'results': new_structure,
        'global_status': 1 if all_visited else 0
    }

    return result

def jsonify_db_response(cursor):
    response = cursor.fetchall()
    if response:
        row_headers=[x[0] for x in cursor.description]

        json_data = [dict(zip(row_headers,row_values)) for row_values in response]
    else:
        json_data = None
    return json_data