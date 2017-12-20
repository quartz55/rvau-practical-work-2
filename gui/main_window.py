import os

from PyQt5 import (QtWidgets as qt,
                   QtGui as gui)
from PyQt5.QtCore import Qt
from core import Database, Image, Matcher
from gui import AddEntryWindow
from log import logger


class MainWindow(qt.QMainWindow):
    def __init__(self):
        super().__init__()
        self.database: Database = None
        self.matcher: Matcher = Matcher()
        with open('dev.db', 'rb') as db:
                self.database = Database.connect(db)
        self.configure_window()
        self.configure_menubar()
        self.__entryWindow = None
        self.scene = qt.QGraphicsScene()
        self.view = qt.QGraphicsView(self.scene)
        self.setCentralWidget(self.view)
        self.show()

    def configure_window(self):
        self.setWindowTitle('RVAU PW2')
        self.setGeometry(0, 0, 800, 400)
        screen_size = gui.QGuiApplication.primaryScreen().availableSize()
        self.resize(int(screen_size.width() * 3 / 5), int(screen_size.height() * 3 / 5))
        self.center()
        self.statusBar().showMessage('Ready')

    def configure_menubar(self):
        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)

        file_menu = menubar.addMenu('File')

        open_act = qt.QAction('Open', self)
        open_act.setShortcut('Ctrl+O')
        open_act.setStatusTip('Open image to augment')
        open_act.triggered.connect(self.open_image)
        file_menu.addAction(open_act)

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

    def open_image(self):
        filename, __ = qt.QFileDialog.getOpenFileName(self, 'Load Image', os.environ.get('HOME'),
                                                      'Images (*.png *.jpg)')
        if filename:
            image = Image.from_file(filename)
            image_eq = self.matcher.histogram_equalization(image)
            kp, des = self.matcher.features_raw(image_eq)
            for entry in self.database.entries:
                logger.debug("Trying to match against '%s'", entry.name)
                matches = self.matcher.match(entry.descriptors, des)
                logger.debug("Found %d/10 matches", len(matches))
                if len(matches) >= 10:
                    logger.info("Found a match in the database! (%s)", entry.name)
                    self.scene.clear()
                    h, w, d = image.dimensions
                    q_image = gui.QImage(image.rgb, w, h, w * d, gui.QImage.Format_RGB888)
                    item = self.scene.addPixmap(gui.QPixmap(q_image))
                    self.view.fitInView(item, Qt.KeepAspectRatio)
                    return
            info_box = qt.QMessageBox(self)
            info_box.setIcon(qt.QMessageBox.Warning)
            info_box.setText("Couldn't find a matching entry in the database")
            info_box.exec()

    def open_add_entry_window(self):
        logger.debug('Opening an add database entry window')
        self.__entryWindow = AddEntryWindow(self.database, self.matcher)
        pos = self.frameGeometry().topLeft()
        self.__entryWindow.move(pos.x() + 20, pos.y() + 20)
        self.__entryWindow.show()

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