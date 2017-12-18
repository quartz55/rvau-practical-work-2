import numpy as np
import cv2
import sys
from matplotlib import pyplot as plt
from PyQt5 import QtWidgets as qt, QtGui as gui, QtCore as qtc
from log import logger
from gui.add_entry_window import AddEntryWindow


class MainWindow(qt.QMainWindow):

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.__entryWindow = None

    def init_ui(self):
        self.setWindowTitle('RVAU PW2')
        self.setGeometry(0, 0, 800, 400)
        screen_size = gui.QGuiApplication.primaryScreen().availableSize()
        self.resize(int(screen_size.width() * 3 / 5), int(screen_size.height() * 3 / 5))
        self.center()

        self.statusBar().showMessage('Ready')

        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)

        file_menu = menubar.addMenu('File')

        exit_action = qt.QAction('Quit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Quit application')
        exit_action.triggered.connect(qt.qApp.quit)
        file_menu.addAction(exit_action)
        menubar.addAction(file_menu.menuAction())

        database_menu = menubar.addMenu('Database')

        add_database_action = qt.QAction('Add Entry', self)
        add_database_action.setShortcut('Ctrl+Shift+A')
        add_database_action.setStatusTip('Add a new entry to the image database')
        add_database_action.triggered.connect(self.open_add_entry_window)
        database_menu.addAction(add_database_action)

        menubar.addAction(database_menu.menuAction())

        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = qt.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def open_add_entry_window(self):
        logger.debug('Opening an add database entry window')
        self.__entryWindow = AddEntryWindow()
        pos = self.frameGeometry().topLeft()
        self.__entryWindow.move(pos.x() + 20, pos.y() + 20)
        self.__entryWindow.show()

    def closeEvent(self, event):
        reply = qt.QMessageBox.question(self, 'Message',
                                        "Are you sure to quit?", qt.QMessageBox.Yes |
                                        qt.QMessageBox.No, qt.QMessageBox.No)

        if reply == qt.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


if __name__ == '__main__':
    app = qt.QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())