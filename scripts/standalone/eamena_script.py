from openai import OpenAI
import pandas as pd
import openpyxl
from typing import Dict, List
import json
import os
from datetime import datetime
import random


class EAMENAMultiHeritageGenerator:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def generate_multi_heritage_data(self, user_prompt: str, num_sites: int, callback=None) -> List[Dict]:
        """
        Genera dati per multipli siti Heritage Place
        """
        messages = [
            {"role": "system", "content": """
            Sei un esperto del database EAMENA. Genera dati per multipli siti nel foglio Heritage Place.
            I siti possono essere correlati tra loro e avere geometrie diverse.
            Rispondi solo con JSON.
            """},
            {"role": "user", "content": f"""
            Genera un JSON con dati per {num_sites} siti Heritage Place per: {user_prompt}

            Il JSON DEVE essere un array di oggetti, ogni oggetto rappresenta un sito e segue questa struttura:
            {{
                "EAMENA_ID": "EAMENA-XXXX-XXXXXXX",
                "NAME": "nome del sito",
                "GRID_ID": "grid reference",
                "LOCATION_CERTAINTY": "Definite",
                "SITE_FEATURE_FORM": "Archaeological Feature|Archaeological Deposit|Structure",
                "SITE_FEATURE_INTERPRETATION": "Settlement|Burial|Religious|Military",
                "SITE_FEATURE_MORPHOLOGY": "Single|Multiple|Complex",
                "CULTURAL_PERIOD": "periodo culturale",
                "CULTURAL_PERIOD_CERTAINTY": "Definite|Probable|Possible",
                "OVERALL_ARCHAEOLOGICAL_CERTAINTY": "High|Medium|Low",
                "OVERALL_SITE_MORPHOLOGY": "Artifact Scatter|Building|Structure",
                "DAMAGE_EXTENT": "0-10%|11-30%|31-60%|61-90%|91-100%",
                "DAMAGE_DATE": "YYYY-MM-DD",
                "CAUSE_OF_DAMAGE": "Agricultural|Development|Natural",
                "EFFECT_OF_DAMAGE": "Structural Damage|Partial Collapse|Total Collapse",
                "COUNTRY": "paese",
                "ADMINISTRATIVE_DIVISION": "regione",
                "ASSESSMENT_ACTIVITY_TYPE": "Desk-Based Assessment|Field Survey|Remote Sensing",
                "ASSESSMENT_ACTIVITY_DATE": "YYYY-MM-DD",
                "INVESTIGATOR_NAME": "nome dell'investigatore",
                "GEOMETRY_TYPE": "Point|Polygon|Line",
                "RELATED_SITE_ID": "EAMENA-ID di un sito correlato o null se non correlato",
                "RELATIONSHIP_TYPE": "Part of|Contains|Near|null se non correlato"
            }}

            IMPORTANTE:
            1. Genera ID EAMENA unici per ogni sito
            2. Se ci sono siti correlati, usa RELATED_SITE_ID e RELATIONSHIP_TYPE
            3. Alcuni siti possono avere geometrie diverse (Point, Polygon, Line)
            4. Siti correlati possono condividere alcuni dati ma devono avere ID diversi
            """}
        ]

        if callback:
            callback("Generazione dati in corso...\n")

        accumulated_json = ""

        stream = self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=messages,
            temperature=0.7,
            response_format={"type": "json_object"},
            stream=True
        )

        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                accumulated_json += content
                if callback:
                    callback(content)

        if callback:
            callback("\n\nGenerazione completata.")

        try:
            data = json.loads(accumulated_json)
            # Assicuriamoci che il risultato sia una lista
            if isinstance(data, dict):
                data = [data]  # Se è un singolo oggetto, lo convertiamo in lista
            return data
        except json.JSONDecodeError:
            raise ValueError("OpenAI non ha generato un JSON valido")

    def get_master_cell(self, sheet, cell_coord):
        """
        Ottiene la cella principale per una cella unita
        """
        try:
            for merged_range in sheet.merged_cells.ranges:
                if cell_coord in merged_range:
                    return sheet.cell(row=merged_range.min_row, column=merged_range.min_col)
            return sheet[cell_coord]
        except Exception as e:
            print(f"Errore nel trovare la cella master {cell_coord}: {str(e)}")
            return None

    def safe_set_cell_value(self, sheet, cell_coord, value):
        """
        Imposta il valore di una cella in modo sicuro, gestendo le celle unite
        """
        try:
            master_cell = self.get_master_cell(sheet, cell_coord)
            if master_cell is not None:
                master_cell.value = value
                print(f"Inserito '{value}' nella cella {cell_coord}")
            else:
                print(f"Attenzione: Non è possibile trovare la cella master per {cell_coord}")
        except Exception as e:
            print(f"Attenzione: Impossibile impostare il valore per la cella {cell_coord}: {str(e)}")

    def fill_heritage_place(self, wb, data_list: List[Dict]) -> None:
        """
        Compila il foglio Heritage Place con multiple righe di dati
        """
        print("\nCompilazione foglio Heritage Place...")
        sheet = wb['Heritage Place']

        # Mappa dei campi alle colonne
        field_mapping = {
            'EAMENA_ID': 'A',
            'NAME': 'B',
            'GRID_ID': 'C',
            'LOCATION_CERTAINTY': 'D',
            'SITE_FEATURE_FORM': 'E',
            'SITE_FEATURE_INTERPRETATION': 'F',
            'SITE_FEATURE_MORPHOLOGY': 'G',
            'CULTURAL_PERIOD': 'H',
            'CULTURAL_PERIOD_CERTAINTY': 'I',
            'OVERALL_ARCHAEOLOGICAL_CERTAINTY': 'J',
            'OVERALL_SITE_MORPHOLOGY': 'K',
            'DAMAGE_EXTENT': 'L',
            'DAMAGE_DATE': 'M',
            'CAUSE_OF_DAMAGE': 'N',
            'EFFECT_OF_DAMAGE': 'O',
            'COUNTRY': 'P',
            'ADMINISTRATIVE_DIVISION': 'Q',
            'ASSESSMENT_ACTIVITY_TYPE': 'R',
            'ASSESSMENT_ACTIVITY_DATE': 'S',
            'INVESTIGATOR_NAME': 'T',
            'GEOMETRY_TYPE': 'U',
            'RELATED_SITE_ID': 'V',
            'RELATIONSHIP_TYPE': 'W'
        }

        # Inserisci i dati partendo dalla riga 4 (dopo le intestazioni)
        for i, data in enumerate(data_list, start=4):
            print(f"\nInserimento dati per il sito {i - 3}:")
            for field, value in data.items():
                if field in field_mapping:
                    cell_coord = f"{field_mapping[field]}{i}"
                    self.safe_set_cell_value(sheet, cell_coord, value)

        print("Compilazione completata")

    def create_heritage_excel(self, data_list: List[Dict], template_path: str, output_path: str) -> None:
        """
        Crea un nuovo file Excel basato sul template
        """
        try:
            print("\nCreazione file Excel...")

            # Carica il template
            print("Caricamento template...")
            wb = openpyxl.load_workbook(template_path)

            # Compila il foglio Heritage Place
            self.fill_heritage_place(wb, data_list)

            # Salva il nuovo file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            excel_path = f"{output_path}/EAMENA_Heritage_Multi_{timestamp}.xlsx"
            print(f"\nSalvataggio file in: {excel_path}")
            wb.save(excel_path)

            print("\nFile Excel creato con successo!")
            print(f"Sono stati inseriti {len(data_list)} siti nel foglio Heritage Place")
            return excel_path

        except Exception as e:
            print(f"\nErrore durante la creazione del file Excel: {str(e)}")
            raise


def main():
    print("=== EAMENA Multi-Heritage Data Generator ===")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        api_key = input("Inserisci la tua chiave API OpenAI: ")

    generator = EAMENAMultiHeritageGenerator(api_key)

    print("\nEsempi di prompt:")
    print("1. 'Genera dati per un complesso di siti romani in Giordania con strutture correlate'")
    print("2. 'Crea dati per un sito urbano bizantino con multiple aree e geometrie'")

    user_prompt = input("\nInserisci il tuo prompt per generare i dati: ")
    num_sites = int(input("Quanti siti vuoi generare? "))

    try:
        # Genera i dati
        data_list = generator.generate_multi_heritage_data(user_prompt, num_sites)

        # Crea la directory output se non esiste
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)

        # Crea il file Excel
        template_path = "BUS_withVocab_Template08122020.xlsx"
        generator.create_heritage_excel(data_list, template_path, output_dir)

    except Exception as e:
        print(f"\nSi è verificato un errore: {str(e)}")
        print("\nTraceback completo:")
        import traceback
        print(traceback.format_exc())


if __name__ == "__main__":
    main()