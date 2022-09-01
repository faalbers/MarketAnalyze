from PyQt6.QtWidgets import QApplication
from STWindow import *
import sys

app = QApplication(sys.argv)

window = STWindow()
window.show()

sys.exit(app.exec())
