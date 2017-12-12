import numpy as np
import cv2
import sys
from matplotlib import pyplot as plt
from PyQt5 import QtWidgets as qt, QtGui as gui

resources = 'resources/'

img = cv2.imread(resources + '/images/taj-mahal-1.jpg')

# Initiate ORB detector
orb = cv2.ORB_create()
# find the keypoints with ORB
kp = orb.detect(img, None)
# compute the descriptors with ORB
kp, des = orb.compute(img, kp)
# draw only keypoints location,not size and orientation
img2 = cv2.drawKeypoints(img, kp, None, color=(0, 255, 0), flags=0)
plt.imshow(img2)
plt.show()


class MainWindow(qt.QMainWindow):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('RVAU PW2')
        self.setGeometry(0, 0, 800, 400)
        self.center()

        hbox = qt.QHBoxLayout()

        lbl = qt.QLabel(self)
        lbl.setPixmap(gui.QPixmap(resources + '/images/taj-mahal-1.jpg'))
        hbox.addWidget(lbl)

        self.setLayout(hbox)

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
        database_menu.addAction(add_database_action)

        menubar.addAction(database_menu.menuAction())

        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = qt.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def closeEvent(self, event):
        reply = qt.QMessageBox.question(self, 'Message',
                                        "Are you sure to quit?", qt.QMessageBox.Yes |
                                        qt.QMessageBox.No, qt.QMessageBox.No)

        if reply == qt.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


app = qt.QApplication(sys.argv)
window = MainWindow()
sys.exit(app.exec_())
