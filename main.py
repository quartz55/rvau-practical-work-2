import sys
from PyQt5 import QtWidgets as qt
from gui import MainWindow
from log import logger

if __name__ == '__main__':
    app = qt.QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())