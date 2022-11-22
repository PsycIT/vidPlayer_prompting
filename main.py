from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

from cwidget import CWidget
import sys

QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)


if __name__ == '__main__':
  
    pname = "jooyeongkim"

    app = QApplication(sys.argv)
    w = CWidget(pname)
    w.show()


    sys.exit(app.exec_())