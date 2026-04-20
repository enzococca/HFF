import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton, \
    QListWidget, QListWidgetItem, QFrame, QFileDialog, QMessageBox, QTextBrowser, QDialog
from PyQt5.QtGui import QIcon, QDesktopServices, QPixmap, QImage
from PyQt5.QtCore import Qt, QUrl, QSize
from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QLabel
from PyQt5.QtWebEngineWidgets import QWebEngineView


import pyvista as pv
from pyvistaqt import QtInteractor
import numpy as np
from PIL import Image
from io import BytesIO


class GoogleLensDialog(QDialog):
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Google Lens Search")
        self.setMinimumSize(800, 600)

        layout = QVBoxLayout(self)

        # Istruzioni per l'utente
        instructions = QLabel("1. Clicca 'Carica immagine' per aprire Google Lens\n"
                              "2. Una volta aperto Google Lens, trascina l'immagine nella finestra del browser\n"
                              "3. Google Lens avvierà automaticamente la ricerca")
        layout.addWidget(instructions)

        # Pulsante per caricare l'immagine
        self.load_button = QPushButton("Carica immagine")
        self.load_button.clicked.connect(self.load_image)
        layout.addWidget(self.load_button)

        # Visualizzatore web
        self.web_view = QWebEngineView(self)
        layout.addWidget(self.web_view)

        self.image_path = image_path

    def load_image(self):
        # Apri Google Lens
        self.web_view.load(QUrl("https://lens.google.com/"))

        # Abilita il drag and drop dell'immagine
        self.web_view.loadFinished.connect(self.on_load_finished)

    def on_load_finished(self, ok):
        if ok:
            # Inserisci l'immagine nella pagina web
            js_code = f"""
                var img = new Image();
                img.src = 'file://{self.image_path}';
                img.onload = function() {{
                    document.body.appendChild(img);
                    img.style.position = 'fixed';
                    img.style.top = '10px';
                    img.style.left = '10px';
                    img.style.width = '100px';
                    img.style.height = 'auto';
                    img.style.zIndex = '9999';
                    img.style.cursor = 'move';

                    img.addEventListener('mousedown', function(e) {{
                        var startX = e.clientX - img.offsetLeft;
                        var startY = e.clientY - img.offsetTop;

                        function moveAt(e) {{
                            img.style.left = e.clientX - startX + 'px';
                            img.style.top = e.clientY - startY + 'px';
                        }}

                        document.addEventListener('mousemove', moveAt);

                        img.onmouseup = function() {{
                            document.removeEventListener('mousemove', moveAt);
                            img.onmouseup = null;
                        }};
                    }});
                }};
            """
            self.web_view.page().runJavaScript(js_code)


class ArchaeologicalViewer(QWidget):
    def __init__(self):
        super().__init__()

        # Layout principale
        main_layout = QHBoxLayout(self)

        # Viewer 3D per oggetti archeologici
        self.frame_3d = QFrame(self)
        self.layout_3d = QVBoxLayout(self.frame_3d)
        self.plotter = QtInteractor(self.frame_3d)
        self.layout_3d.addWidget(self.plotter.interactor)
        main_layout.addWidget(self.frame_3d, 2)  # Occupazione della parte sinistra

        # Pulsante per caricare un modello 3D
        self.load_button = QPushButton("Carica Modello 3D e Texture", self)
        self.load_button.clicked.connect(self.load_3d_model)
        self.layout_3d.addWidget(self.load_button)

        # Pulsante per interrogare Google Lens
        self.query_lens_button = QPushButton("Cerca su Google Lens", self)
        self.query_lens_button.clicked.connect(self.search_google_lens)
        self.layout_3d.addWidget(self.query_lens_button)

        self.setWindowTitle("Archaeological Research Interface")
        self.resize(1200, 800)

        self.model_filepath = None
        self.texture_filepath = None

    def load_3d_model(self):
        # Seleziona il file del modello 3D
        model_filepath, _ = QFileDialog.getOpenFileName(self, "Seleziona Modello 3D", "",
                                                        "3D Model Files (*.obj *.ply *.fbx *.3ds)")
        if not model_filepath:
            return

        # Seleziona il file della texture (opzionale)
        texture_filepath, _ = QFileDialog.getOpenFileName(self, "Seleziona Texture", "", "Image Files (*.jpg *.png)")

        # Carica il modello 3D
        self.model_filepath = model_filepath
        self.texture_filepath = texture_filepath
        mesh = pv.read(self.model_filepath)
        self.plotter.clear()

        if self.texture_filepath and os.path.exists(self.texture_filepath):
            texture = pv.read_texture(self.texture_filepath)
            self.plotter.add_mesh(mesh, texture=texture, show_edges=False)
        else:
            self.plotter.add_mesh(mesh, color="lightgray", show_edges=True)

        self.plotter.camera_position = 'xy'
        self.plotter.show()

    def search_google_lens(self):
        if not hasattr(self, 'plotter') or not self.plotter.mesh:
            QMessageBox.warning(self, "Nessun modello", "Carica prima un modello 3D.", QMessageBox.Ok)
            return

        # Cattura l'immagine dal visualizzatore 3D
        image = self.capture_3d_image()

        # Salva temporaneamente l'immagine
        temp_image_path = os.path.join(os.path.dirname(__file__), "temp_3d_image.png")
        image.save(temp_image_path)

        # Apri il dialogo di Google Lens
        dialog = GoogleLensDialog(temp_image_path, self)
        dialog.exec_()

        # Rimuovi l'immagine temporanea dopo la chiusura del dialogo
        os.remove(temp_image_path)

    def capture_3d_image(self):
        # Cattura l'immagine dal visualizzatore 3D
        image_array = self.plotter.screenshot()

        # Converti l'array NumPy in un'immagine PIL
        pil_image = Image.fromarray(image_array)

        # Converti l'immagine PIL in QPixmap
        buffer = BytesIO()
        pil_image.save(buffer, format="PNG")
        q_image = QImage()
        q_image.loadFromData(buffer.getvalue())

        return QPixmap.fromImage(q_image)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = ArchaeologicalViewer()
    viewer.show()
    sys.exit(app.exec_())