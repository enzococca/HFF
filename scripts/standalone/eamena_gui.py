import sys
import json
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QTextEdit, QPushButton, QLabel,
                             QSpinBox, QLineEdit, QMessageBox, QDialog)
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from PyQt5.QtGui import QColor, QPalette, QTextCharFormat, QFont
import configparser
from pathlib import Path


class ConsoleOutput(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)

        # Imposta lo sfondo nero
        palette = self.palette()
        palette.setColor(QPalette.Base, QColor("#000000"))
        self.setPalette(palette)

        # Imposta il font
        font = QFont("Courier New", 10)
        self.setFont(font)

        # Formati per i diversi tipi di messaggi
        self.normal_format = QTextCharFormat()
        self.normal_format.setForeground(QColor("#FFFFFF"))

        self.success_format = QTextCharFormat()
        self.success_format.setForeground(QColor("#00FF00"))

        self.error_format = QTextCharFormat()
        self.error_format.setForeground(QColor("#FF0000"))

        self.info_format = QTextCharFormat()
        self.info_format.setForeground(QColor("#00FFFF"))

    def append_message(self, text, message_type="normal"):
        cursor = self.textCursor()
        cursor.movePosition(cursor.End)

        if message_type == "success":
            cursor.insertText(text, self.success_format)
        elif message_type == "error":
            cursor.insertText(text, self.error_format)
        elif message_type == "info":
            cursor.insertText(text, self.info_format)
        else:
            cursor.insertText(text, self.normal_format)

        self.setTextCursor(cursor)
        self.ensureCursorVisible()


class APIKeyDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configura API Key")
        self.setModal(True)

        layout = QVBoxLayout()

        # Campo per l'API key
        self.api_key_input = QLineEdit()
        layout.addWidget(QLabel("OpenAI API Key:"))
        layout.addWidget(self.api_key_input)

        # Pulsante di salvataggio
        save_button = QPushButton("Salva")
        save_button.clicked.connect(self.accept)
        layout.addWidget(save_button)

        self.setLayout(layout)


class GeneratorThread(QThread):
    output_signal = pyqtSignal(str, str)  # (text, message_type)
    finished_signal = pyqtSignal(list)  # Cambiato da dict a list
    error_signal = pyqtSignal(str)

    def __init__(self, generator, prompt, num_sites):
        super().__init__()
        self.generator = generator
        self.prompt = prompt
        self.num_sites = num_sites

    def emit_callback(self, text, message_type="normal"):
        self.output_signal.emit(text, message_type)

    def run(self):
        try:
            self.emit_callback("Inizializzazione generazione...\n", "info")
            data = self.generator.generate_multi_heritage_data(
                self.prompt,
                self.num_sites,
                callback=lambda x: self.emit_callback(x, "normal")
            )
            self.finished_signal.emit(data)
        except Exception as e:
            self.error_signal.emit(str(e))


class EAMENAGui(QMainWindow):
    def __init__(self):
        super().__init__()
        self.generator = None
        self.init_ui()
        self.load_api_key()

    def init_ui(self):
        self.setWindowTitle('EAMENA Data Generator')
        self.setGeometry(100, 100, 1000, 800)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
            }
            QLabel {
                color: #ffffff;
            }
            QPushButton {
                background-color: #0d47a1;
                color: white;
                padding: 5px;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
            QPushButton:pressed {
                background-color: #0a3d91;
            }
            QTextEdit {
                border: 1px solid #555555;
                border-radius: 3px;
            }
            QSpinBox {
                background-color: #ffffff;
                padding: 2px;
            }
        """)

        # Widget principale
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()

        # Area superiore per input
        input_layout = QHBoxLayout()

        # Area prompt
        prompt_layout = QVBoxLayout()
        prompt_label = QLabel("Prompt:")
        self.prompt_input = QTextEdit()
        self.prompt_input.setMaximumHeight(100)
        self.prompt_input.setStyleSheet("background-color: #ffffff; color: #000000;")
        prompt_layout.addWidget(prompt_label)
        prompt_layout.addWidget(self.prompt_input)
        input_layout.addLayout(prompt_layout, stretch=2)

        # Area per numero siti e pulsanti
        controls_layout = QVBoxLayout()

        # Spinner per numero siti
        sites_layout = QHBoxLayout()
        sites_label = QLabel("Numero siti:")
        self.sites_spinner = QSpinBox()
        self.sites_spinner.setMinimum(1)
        self.sites_spinner.setMaximum(10)
        sites_layout.addWidget(sites_label)
        sites_layout.addWidget(self.sites_spinner)
        controls_layout.addLayout(sites_layout)

        # Pulsanti
        self.generate_button = QPushButton('Genera')
        self.generate_button.clicked.connect(self.generate_data)
        controls_layout.addWidget(self.generate_button)

        self.api_key_button = QPushButton('Configura API Key')
        self.api_key_button.clicked.connect(self.show_api_key_dialog)
        controls_layout.addWidget(self.api_key_button)

        input_layout.addLayout(controls_layout, stretch=1)
        layout.addLayout(input_layout)

        # Console di output
        output_label = QLabel("Output:")
        self.output_console = ConsoleOutput()
        layout.addWidget(output_label)
        layout.addWidget(self.output_console)

        main_widget.setLayout(layout)

    def load_api_key(self):
        config = configparser.ConfigParser()
        config_file = Path.home() / '.eamena_config'

        if config_file.exists():
            config.read(config_file)
            if 'OpenAI' in config and 'api_key' in config['OpenAI']:
                api_key = config['OpenAI']['api_key']
                if api_key:
                    self.init_generator(api_key)
                    return

        self.show_api_key_dialog()

    def save_api_key(self, api_key):
        config = configparser.ConfigParser()
        config['OpenAI'] = {'api_key': api_key}

        config_file = Path.home() / '.eamena_config'
        with open(config_file, 'w') as f:
            config.write(f)

    def show_api_key_dialog(self):
        dialog = APIKeyDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            api_key = dialog.api_key_input.text().strip()
            if api_key:
                self.save_api_key(api_key)
                self.init_generator(api_key)

    def init_generator(self, api_key):
        from eamena_script import EAMENAMultiHeritageGenerator
        self.generator = EAMENAMultiHeritageGenerator(api_key)
        self.generate_button.setEnabled(True)
        self.output_console.append_message("Generator inizializzato con successo!\n", "success")

    def append_output(self, text, message_type="normal"):
        self.output_console.append_message(text, message_type)

    def generate_data(self):
        if not self.generator:
            QMessageBox.warning(self, "Errore", "Configura prima l'API Key")
            return

        prompt = self.prompt_input.toPlainText().strip()
        if not prompt:
            QMessageBox.warning(self, "Errore", "Inserisci un prompt")
            return

        self.output_console.clear()
        self.generate_button.setEnabled(False)

        # Avvia il thread di generazione
        self.thread = GeneratorThread(
            self.generator,
            prompt,
            self.sites_spinner.value()
        )
        self.thread.output_signal.connect(self.append_output)
        self.thread.finished_signal.connect(self.generation_finished)
        self.thread.error_signal.connect(self.generation_error)
        self.thread.start()

    def generation_finished(self, data):
        self.generate_button.setEnabled(True)
        self.append_output("\nGenerazione completata con successo!", "success")

        try:
            # Crea la directory output se non esiste
            output_dir = "output"
            os.makedirs(output_dir, exist_ok=True)

            # Crea il file Excel
            excel_path = self.generator.create_heritage_excel(
                data,
                "BUS_withVocab_Template08122020.xlsx",
                output_dir
            )
            self.append_output(f"\nFile Excel creato: {excel_path}\n", "success")
        except Exception as e:
            self.append_output(f"\nErrore durante la creazione del file Excel: {str(e)}\n", "error")

    def generation_error(self, error_msg):
        self.generate_button.setEnabled(True)
        self.append_output(f"\nErrore durante la generazione: {error_msg}\n", "error")
        QMessageBox.critical(self, "Errore", str(error_msg))


def main():
    app = QApplication(sys.argv)
    gui = EAMENAGui()
    gui.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()