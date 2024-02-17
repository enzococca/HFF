from docx import Document
from sqlalchemy import create_engine, MetaData, Table, select
from sqlalchemy.orm import sessionmaker
from qgis.PyQt.QtWidgets import *
import socket
import sys, subprocess

try:
    import openai

    print("openai is already installed")
except ImportError:
    print("openai is not installed, installing...")
    try:
        if sys.platform.startswith("win"):
            subprocess.check_call(["pip", "install", "openai"], shell=True)
        elif sys.platform.startswith("darwin") or sys.platform.startswith("linux"):
            subprocess.check_call(["python3", "-m", "pip", "install", "openai"], shell=False)
        else:
            raise Exception(f"Unsupported platform: {sys.platform}")
        print("openai installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while installing openai: {e}")
        sys.exit(1)
try:
    import docx

    print("docx is already installed")
except ImportError:
    print("docx is not installed, installing...")
    try:
        if sys.platform.startswith("win"):
            subprocess.check_call(["pip", "install", "python-docx"], shell=True)
        elif sys.platform.startswith("darwin") or sys.platform.startswith("linux"):
            subprocess.check_call(["python3", "-m", "pip", "install", "python-docx"], shell=False)
        else:
            raise Exception(f"Unsupported platform: {sys.platform}")
        print("openai installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while installing python-docx: {e}")
        sys.exit(1)


import time


class ReportGenerator(QWidget):
    def __init__(self):
        super().__init__()

    @staticmethod
    def read_data_from_db(db_url, table_name):
        engine = create_engine(db_url)
        metadata = MetaData(bind=engine)
        table = Table(table_name, metadata, autoload_with=engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        query = session.query(table)
        records = query.all()
        columns = [column.name for column in table.columns]
        session.close()
        return records, columns

    @staticmethod
    def read_data_from_db_description_only(db_url, table_name):
        engine = create_engine(db_url)
        metadata = MetaData(bind=engine)
        table = Table(table_name, metadata, autoload_with=engine)
        Session = sessionmaker(bind=engine)
        session = Session()

        # Adjust the query to only select the 'description' column
        query = select([table.c.description_i])
        result_proxy = session.execute(query)
        records = result_proxy.fetchall()  # This will be a list of tuples with one element each

        # Extract the descriptions from the tuples
        descriptions = [record[0] for record in records if record[0] is not None]

        session.close()
        return descriptions


    @staticmethod
    def generate_report_with_openai(descriptions_text, api_key, model):
        prompt = descriptions_text
        prompt += "\n\nReport:"

        openai.api_key = api_key
        #while True:
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content": prompt}]
            )
            return response['choices'][0]['message']['content']
        except openai.error.OpenAIError as e:
            if isinstance(e, openai.error.RateLimitError):
                time.sleep(5)
                return ReportGenerator.generate_report_with_openai(descriptions_text, api_key, model)  # Retry
            else:
                raise e

    @staticmethod
    def is_connected():
        try:
            # Try to connect to one of the DNS servers
            socket.create_connection(("1.1.1.1", 53))
            return True
        except OSError:
            pass
        return False

    @staticmethod
    def save_report_to_file(report, file_path):
        # Create a new Document
        doc = Document()
        # Add the report text to the document
        doc.add_paragraph(report)
        # Save the document to the specified file path
        doc.save(file_path)