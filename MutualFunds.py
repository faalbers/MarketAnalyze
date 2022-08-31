from PyQt6.QtWidgets import QApplication
from MFWIndow import *
import sys

app = QApplication(sys.argv)

# window = Window()
window = MFWindow()
window.show()

sys.exit(app.exec())
