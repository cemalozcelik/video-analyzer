from PySide6.QtCore import QObject, Signal, Slot
from core.analyzer import analyze_transcript

class AIAnalysisWorker(QObject):
    finished = Signal(str)  # analysis result
    error = Signal(str)

    def __init__(self, transcript: str, selected_model: str = "OpenAI GPT"):
        super().__init__()
        self.transcript = transcript
        self.selected_model = selected_model

    @Slot()
    def run(self):
        try:
            result = analyze_transcript(self.transcript, self.selected_model)
            if "result" in result:
                self.finished.emit(result["result"])
            else:
                self.error.emit(result.get("error", "Unknown error"))
        except Exception as e:
            self.error.emit(str(e))
