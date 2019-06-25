import psycopg2
import pandas as pd
import os
from builtins import object
from builtins import range
from builtins import str
from ..gui.pyarchinitConfigDialog import *
from ..modules.utility.settings import Settings

class EXCEL(QDialog):
	HOME = os.environ['HFF_HOME']
	
	
	def __init__(self, iface):
        super().__init__()
        self.iface = iface
	def export(self):
		
		cfg_rel_path = os.path.join(os.sep, 'HFF_DB_folder', 'config.cfg')
		file_path = '{}{}'.format(self.HOME, cfg_rel_path)
		conf = open(file_path, "r")
		con_sett = conf.read()
		conf.close()

		settings = Settings(con_sett)
		settings.set_configuration()
		
		if settings.SERVER == 'sqlite':
			sqliteDB_path = os.path.join(os.sep, 'HFF_DB_folder', settings.DATABASE)
			db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)        

		elif settings.SERVER == 'postgres':   
			
			conn = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s' port ='%s'")%(self.lineEdit_DBname(),self.lineEdit_User(), self.lineEdit_Host(), self.lineEdit_Password(), self.lineEdit_Port())

			cur = conn.cursor()

			cur.execute("SELECT * FROM anchor_table;")

			rows = cur.fetchall()
			col_names = []
			for i in cur.description:
			  col_names.append(i[0])

			pd.DataFrame(rows,columns=col_names).to_excel(self.HOME + "anchor.xls",index=True)
        
