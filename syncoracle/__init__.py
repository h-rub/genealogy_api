import sys
import os

import cx_Oracle

try:
    if sys.platform.startswith("darwin"):
        lib_dir = os.path.join(os.environ.get("HOME"), "Downloads",
                               "instantclient_19_8")
        cx_Oracle.init_oracle_client(lib_dir=lib_dir)
    elif sys.platform.startswith("win32"):
        lib_dir=r"C:\oracle\instantclient_21_11"
        cx_Oracle.init_oracle_client(lib_dir=lib_dir)
except Exception as err:
    print(f"Whoops! Error de conexión: {err}")
    print(err)
    sys.exit(1)