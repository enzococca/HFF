from docx import Document
from sqlalchemy import create_engine, MetaData, Table, select
from sqlalchemy.orm import sessionmaker
from qgis.PyQt.QtWidgets import *
import socket
import time

# openai is imported lazily inside generate_report_with_openai so a broken
# pydantic/pydantic-core install in the host environment cannot block plugin
# load. The error surfaces only if the user actually triggers a report.


class ReportGenerator(QWidget):
    def __init__(self):
        super().__init__()

    @staticmethod
    def read_data_from_db(db_url, table_name):
        engine = create_engine(db_url)
        metadata = MetaData()
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
        metadata = MetaData()
        table = Table(table_name, metadata, autoload_with=engine)
        Session = sessionmaker(bind=engine)
        session = Session()

        # Adjust the query to only select the 'description' column
        query = select(table.c.description_i)
        result_proxy = session.execute(query)
        records = result_proxy.fetchall()  # This will be a list of tuples with one element each

        # Extract the descriptions from the tuples
        descriptions = [record[0] for record in records if record[0] is not None]

        session.close()
        return descriptions

    @staticmethod
    def generate_report_with_openai(descriptions_text, api_key, model):
        import openai
        prompt = descriptions_text
        prompt += "\n\nReport:"

        client = openai.OpenAI(api_key=api_key)
        try:
            # Newer OpenAI models (gpt-5.x / o-series) require max_completion_tokens
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": prompt}],
                max_completion_tokens=2000,
            )
            return response.choices[0].message.content
        except openai.OpenAIError as e:
            if "rate_limit" in str(e).lower():
                time.sleep(5)
                return ReportGenerator.generate_report_with_openai(descriptions_text, api_key, model)
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