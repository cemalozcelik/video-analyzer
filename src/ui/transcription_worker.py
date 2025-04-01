from PySide6.QtCore import QObject, Signal, Slot
from core.transcriber import transcribe_audio

class TranscriptionWorker(QObject):
    finished = Signal(str)  # transcription result
    error = Signal(str)

    def __init__(self, audio_path, engine="Whisper (local)"):
        super().__init__()  
        self.audio_path = audio_path
        self.engine = engine



    @Slot()
    def run(self):
        try:
            result = transcribe_audio(self.audio_path, engine=self.engine)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))
