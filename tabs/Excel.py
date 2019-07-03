import os

import psycopg2
import pandas as pd

from ..modules.db.pyarchinit_conn_strings import Connection

conn = Connection()

conn_str = conn.conn_str()

df = pd.read_sql_query('select * from "site_table"',con=conn_str)
col_names = []
# for i in df:
  # col_names.append(i[0])

pd.DataFrame(col_names,columns=col_names).to_excel("C:\\Users\\enzo\\HFF\\test1.xls",index=True) 