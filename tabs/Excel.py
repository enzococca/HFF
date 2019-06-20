import psycopg2
import pandas as pd

        
   
conn = psycopg2.connect("dbname='den19' user='postgres' host='localhost' password='postgres' port =5433")

cur = conn.cursor()

cur.execute("SELECT * FROM site_table;")

rows = cur.fetchall()
col_names = []
for i in cur.description:
  col_names.append(i[0])

pd.DataFrame(rows,columns=col_names).to_excel("C:\\Users\\enzo\\Desktop\\sample\\site.xls",index=True)
        
