from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from ui.video_import import VideoImportPanel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video Analyzer")
        self.resize(1000, 700)

        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(VideoImportPanel())

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
