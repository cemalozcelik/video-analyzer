from PySide6.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QFileDialog,
    QLabel, QLineEdit, QMessageBox, QTextEdit
)
from core.video_processor import process_video, download_youtube_video, extract_audio
from core.transcriber import transcribe_audio
from utils.logger import log_info, log_error
from PySide6.QtWidgets import QProgressBar, QComboBox
from PySide6.QtCore import Signal, QObject, QThread
from ui.youtube_worker import YouTubeDownloaderWorker
from PySide6.QtCore import Slot
from core.analyzer import analyze_transcript
from ui.transcription_worker import TranscriptionWorker
from ui.analysis_worker import AIAnalysisWorker

class ProgressBridge(QObject):
    progress_changed = Signal(int)




class VideoImportPanel(QWidget):
    def __init__(self):
        super().__init__()

        # 1. Progress bar'ı önce oluştur
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)

        # 2. ProgressBridge oluştur ve sinyali bağla
        self.progress_bridge = ProgressBridge()
        self.progress_bridge.progress_changed.connect(self.progress_bar.setValue)

        # Diğer bileşenler
        self.label = QLabel("No video selected")
        self.youtube_input = QLineEdit()
        self.youtube_input.setPlaceholderText("Paste YouTube URL here")
        self.transcript_output = QTextEdit()
        self.transcript_output.setPlaceholderText("Transcript will appear here...")
        self.transcript_output.setReadOnly(True)
        
        self.analyze_button = QPushButton("Analyze Transcript with AI")
        self.analyze_button.clicked.connect(self.run_analysis)

        self.analysis_output = QTextEdit()
        self.analysis_output.setPlaceholderText("AI analysis will appear here...")
        self.analysis_output.setReadOnly(True)


        self.button_local = QPushButton("Import Local Video")
        self.button_youtube = QPushButton("Download from YouTube")
        self.button_local.clicked.connect(self.import_video)
        self.button_youtube.clicked.connect(self.download_youtube)
        
        self.analysis_selector = QComboBox()
        self.analysis_selector.addItems(["OpenAI GPT", "Claude (Anthropic)"])
        self.analysis_selector.setCurrentIndex(0)
        
        # Engine selectors
        self.transcription_selector = QComboBox()
        self.transcription_selector.addItems(["Whisper (local)", "OpenAI Whisper", "Claude (summarize only)"])
        self.transcription_selector.setCurrentIndex(0)
        
        self.save_button = QPushButton("💾 Save Analysis")
        self.save_button.clicked.connect(self.save_analysis)


        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.button_local)
        layout.addWidget(self.label)
        layout.addWidget(self.youtube_input)
        layout.addWidget(self.button_youtube)
        layout.addWidget(QLabel("Transcription Engine:"))
        layout.addWidget(self.transcription_selector)
        layout.addWidget(self.transcript_output)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.analyze_button)
        layout.addWidget(QLabel("Analysis Engine:"))
        layout.addWidget(self.analysis_selector)
        layout.addWidget(self.analysis_output)
        layout.addWidget(self.save_button)
        layout.addWidget(QLabel("Transcription Engine:"))
        layout.addWidget(self.transcription_selector)
        layout.addWidget(QLabel("Analysis Engine:"))
        layout.addWidget(self.analysis_selector)



        self.setLayout(layout)

    def import_video(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Video File", "", "Videos (*.mp4 *.avi *.mov)")
        if file_path:
            self.label.setText(f"Selected: {file_path}")
            self.handle_transcription(file_path)
            
    def download_youtube(self):
        url = self.youtube_input.text()
        if not url:
            QMessageBox.warning(self, "Missing URL", "Please enter a YouTube video URL.")
            return

        self.label.setText("🔽 Downloading from YouTube...")
        self.progress_bar.setValue(0)

        # Worker ve Thread oluştur
        self.thread = QThread()
        self.worker = YouTubeDownloaderWorker(url)
        self.worker.moveToThread(self.thread)
        self.worker.progress.connect(self.update_progress)

        # Sinyalleri bağla
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.finished.connect(self.on_download_finished)
        self.worker.error.connect(self.on_download_error)
        self.thread.started.connect(self.worker.run)

        # Thread bittiğinde temizle
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        # Thread başlat
        self.thread.start()
    
    @Slot(int)
    def update_progress(self, value):
        self.progress_bar.setValue(value)

    @Slot(str)
    def on_download_finished(self, file_path):
        self.label.setText(f"✅ Downloaded: {file_path}")
        self.handle_transcription(file_path)

    @Slot(str)
    def on_download_error(self, message):
        log_error(f"Download failed: {message}")
        QMessageBox.critical(self, "Download Failed", message)


    def handle_transcription(self, video_path):
        try:
            audio_path = extract_audio(video_path)
            self.transcript_output.setPlainText("🔊 Transcribing audio...")
            
            # Get selected engine from dropdown
            selected_engine = self.transcription_selector.currentText()
        
                        
            # Start transcription in a new thread
            self.transcription_thread = QThread()
            self.transcription_worker = TranscriptionWorker(audio_path,selected_engine)
            self.transcription_worker.moveToThread(self.transcription_thread)

            # Connect signals
            self.transcription_thread.started.connect(self.transcription_worker.run)
            self.transcription_worker.finished.connect(self.on_transcription_complete)
            self.transcription_worker.error.connect(self.on_transcription_error)

            # Cleanup
            self.transcription_worker.finished.connect(self.transcription_thread.quit)
            self.transcription_worker.finished.connect(self.transcription_worker.deleteLater)
            self.transcription_thread.finished.connect(self.transcription_thread.deleteLater)

            self.transcription_thread.start()

        except Exception as e:
            log_error(f"Transcription process failed: {e}")
            QMessageBox.critical(self, "Error", "Something went wrong during transcription.")
    
    Slot(str)
    def on_transcription_complete(self, text):
        self.transcript_output.setPlainText(text)

    Slot(str)
    def on_transcription_error(self, message):
        log_error(f"Transcription failed: {message}")
        QMessageBox.critical(self, "Transcription Error", message)

    def run_analysis(self):
        try:
            transcript = self.transcript_output.toPlainText()
            if not transcript.strip():
                QMessageBox.warning(self, "Empty Transcript", "Please transcribe a video first.")
                return
            
            self.analysis_thread = QThread()
            
        except Exception as e:
            log_error(f"Error during analysis: {e}")
            QMessageBox.critical(self, "Error", "Something went wrong during analysis.")
            return
    
    
    def run_analysis(self):
        transcript = self.transcript_output.toPlainText()
        if not transcript.strip():
            QMessageBox.warning(self, "Empty Transcript", "Please transcribe a video first.")
            return

        self.analysis_output.setPlainText("⏳ Analyzing transcript with AI...")
        
        engine = self.analysis_selector.currentText()

        self.analysis_thread = QThread()
        self.analysis_worker = AIAnalysisWorker(transcript, engine)
        self.analysis_worker.moveToThread(self.analysis_thread)

        self.analysis_thread.started.connect(self.analysis_worker.run)
        self.analysis_worker.finished.connect(self.on_analysis_complete)
        self.analysis_worker.error.connect(self.on_analysis_error)

        self.analysis_worker.finished.connect(self.analysis_thread.quit)
        self.analysis_worker.finished.connect(self.analysis_worker.deleteLater)
        self.analysis_thread.finished.connect(self.analysis_thread.deleteLater)

        self.analysis_thread.start()
    
    Slot(str)
    def on_analysis_complete(self, result: str):
        self.analysis_output.setPlainText(result)

    Slot(str)
    def on_analysis_error(self, error: str):
        log_error(f"Analysis failed: {error}")
        self.analysis_output.setPlainText(f"❌ AI Analysis failed:\n{error}")
        
    @Slot()
    def save_analysis(self):
        content = self.analysis_output.toPlainText()
        if not content.strip():
            QMessageBox.warning(self, "Empty Analysis", "There's no analysis to save.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Analysis As",
            "analysis.md",
            "Markdown Files (*.md);;Text Files (*.txt)"
        )
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                QMessageBox.information(self, "Success", f"Analysis saved to:\n{file_path}")
            except Exception as e:
                log_error(f"Failed to save file: {e}")
                QMessageBox.critical(self, "Error", f"Failed to save file:\n{e}")
