import cx_Oracle

def connect_to_oracle(user, password, dsn):
    """
        Recibe user, password y dsn y retorna cursor para ejecutar consultas.
    """
    connection = cx_Oracle.connect(user = user, password = password, dsn = dsn)
    print("Conexión a Oracle realizada exitosamente")
    cursor = connection.cursor()
    print("Cursor Oracle creado exitosamente, ahora puedes ejecutar consultas")
    return cursor