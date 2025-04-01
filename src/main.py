#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PySide6.QtWidgets import QApplication
import sys
from ui.main_window import MainWindow
from utils.logger import log_info

def main():
    log_info("Starting application")
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    exit_code = app.exec()
    log_info("Application closed.")
    sys.exit(exit_code)
    

if __name__ == "__main__":
    main()
