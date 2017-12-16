import numpy as np
import cv2
import sys
from matplotlib import pyplot as plt
from PyQt5 import QtWidgets as qt, QtGui as gui
from core import Image, Matcher
from log import logger
from gui.add_entry_window import AddEntryWindow


class MainWindow(qt.QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()
        self.__entryWindow = None;

    def initUI(self):
        self.setWindowTitle('RVAU PW2')
        self.setGeometry(0, 0, 800, 400)
        self.center()

        self.statusBar().showMessage('Ready')

        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)

        fileMenu = menubar.addMenu('File')

        exitAction = qt.QAction('Quit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Quit application')
        exitAction.triggered.connect(qt.qApp.quit)
        fileMenu.addAction(exitAction)
        menubar.addAction(fileMenu.menuAction())

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


# matcher = Matcher()
# img1 = Image.from_file('resources/images/westminster-abbey-1.jpg')
#
# plt.imshow(img1.grayscale, 'gray')
# plt.show()
# kp, des = matcher.features(Image(img1.grayscale))
# print(len(kp), len(des))
# plt.imshow(Image(cv2.drawKeypoints(img1.src, kp, None)).rgb)
# plt.show()
#
# img1_heq = Matcher.histogram_equalization(img1)
# plt.imshow(img1_heq.src, 'gray')
# plt.show()
# kp_heq, des_heq = matcher.features(img1_heq)
# print(len(kp_heq), len(des_heq))
# plt.imshow(Image(cv2.drawKeypoints(img1.src, kp_heq, None)).rgb)
# plt.show()