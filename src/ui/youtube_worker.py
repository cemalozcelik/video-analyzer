from PySide6.QtCore import QObject, Signal, Slot
from core.video_processor import download_youtube_video

class YouTubeDownloaderWorker(QObject):
    finished = Signal(str)  # İndirme tamamlandığında: dosya yolu
    error = Signal(str)
    progress = Signal(int)

    def __init__(self, url: str):
        super().__init__()
        self.url = url

    @Slot()
    def run(self):
        try:
            file_path = download_youtube_video(self.url, progress_callback=self.progress.emit)
            self.finished.emit(file_path)
        except Exception as e:
            self.error.emit(str(e))
