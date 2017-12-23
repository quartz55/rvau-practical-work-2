import os

import cv2
import numpy as np
from PyQt5 import (QtWidgets as qt,
                   QtGui as gui,
                   QtCore as qtc)
from PyQt5.QtCore import Qt

import gui.utils as utils
from gui.augment_items import BoxAugmentItem, ArrowAugmentItem, EllipseAugmentItem
from core import Database, Image, Matcher, Entry
from core.augments import AugmentType
from gui import AddEntryWindow
from log import logger


class MainWindow(qt.QMainWindow):
    def __init__(self):
        super().__init__()
        self.database: Database = None
        self.matcher: Matcher = Matcher()
        self.database = Database.connect('dev.db')
        self.configure_window()
        self.configure_menubar()
        self.__entryWindow = None
        self.scene = qt.QGraphicsScene()
        self.view = qt.QGraphicsView(self.scene)
        self.popup_list: EntriesList = None
        self.dev_console: DevConsole = None
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

        list_entries_act = qt.QAction('List Entries', self)
        list_entries_act.setStatusTip('List all entries in the database')
        list_entries_act.triggered.connect(self.list_entries)
        database_menu.addAction(list_entries_act)

        menubar.addAction(database_menu.menuAction())

        developer_menu = menubar.addMenu('Developer')

        results_view_act = qt.QAction('Results View', self)
        results_view_act.setStatusTip('Shows intermediate results')
        results_view_act.triggered.connect(self.open_dev_console)
        developer_menu.addAction(results_view_act)

        menubar.addAction(developer_menu.menuAction())

    def open_image(self):
        filename, __ = qt.QFileDialog.getOpenFileName(self, 'Load Image', os.environ.get('HOME'),
                                                      'Images (*.png *.jpg)')
        if filename:
            image = Image.from_file(filename)
            image_eq = self.matcher.histogram_equalization(image)
            self.add_dev_result("Loaded imagem in grayscale", image.grayscale)
            self.add_dev_result("Histogram Equalization", image_eq.src)
            kp, des = self.matcher.features_raw(image_eq)
            self.add_dev_result("Features in equalized image", Image(cv2.drawKeypoints(image_eq.src, kp, None)).rgb)
            for entry in self.database.entries:
                logger.debug("Trying to match against '%s'", entry.name)
                matches = self.matcher.match(entry.descriptors, des)
                logger.debug("Found %d/10 matches", len(matches))
                if len(matches) >= 10:
                    logger.info("Found a match in the database! (%s)", entry.name)
                    src_pts = np.float32([entry.key_points[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
                    dst_pts = np.float32([kp[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
                    matrix, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
                    matches_mask = mask.ravel().tolist()
                    h, w, __ = entry.img.dimensions
                    pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
                    dst = cv2.perspectiveTransform(pts, matrix)
                    img_with_box = Image(cv2.polylines(np.copy(image.src), [np.int32(dst)], True, 255, 3, cv2.LINE_AA))
                    match_res_img = Image(
                        cv2.drawMatches(entry.img.src, entry.key_points, img_with_box.src, kp, matches,
                                        None,
                                        matchesMask=matches_mask,
                                        flags=2, matchColor=(0, 255, 0),
                                        singlePointColor=False))
                    self.add_dev_result("Matching result with homography", match_res_img.rgb)
                    # Prepare augments
                    self.scene.clear()
                    pen = gui.QPen()
                    pen.setColor(Qt.red)
                    pen.setWidth(5)
                    for augment in entry.augments:
                        if augment.type is AugmentType.BOX:
                            box = BoxAugmentItem(augment.w, augment.h)
                            box.setPos(augment.x, augment.y)
                            self.scene.addItem(box)
                        elif augment.type is AugmentType.ARROW:
                            arrow = ArrowAugmentItem(augment.length)
                            arrow.setPos(augment.x, augment.y)
                            arrow.setRotation(augment.rotation)
                            self.scene.addItem(arrow)
                        elif augment.type is AugmentType.ELLIPSE:
                            ellipse = EllipseAugmentItem(augment.w, augment.h)
                            ellipse.setPos(augment.x, augment.y)
                            self.scene.addItem(ellipse)
                    # Save augments to image
                    self.scene.setSceneRect(0, 0, w, h)
                    augments_image = gui.QImage(w, h, gui.QImage.Format_ARGB32)
                    augments_image.fill(Qt.transparent)
                    painter = gui.QPainter(augments_image)
                    self.scene.render(painter)
                    painter.end()
                    # Warp augments image based on homography matrix calculated above
                    w, h, __ = image.dimensions
                    augments_wrapped = cv2.warpPerspective(utils.qimage_to_numpy(augments_image), matrix,
                                                           (w + 200, h + 200))
                    augments_wrapped_image = gui.QImage(augments_wrapped, w + 200, h + 200, gui.QImage.Format_ARGB32)
                    # Draw final result on screen
                    self.scene.clear()
                    item = self.scene.addPixmap(gui.QPixmap(utils.image_to_qimage(image)))
                    self.scene.addPixmap(gui.QPixmap(augments_wrapped_image))
                    self.scene.setSceneRect(item.boundingRect())
                    self.view.fitInView(item, Qt.KeepAspectRatio)
                    self.update()
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

    def list_entries(self):
        self.popup_list = EntriesList(self, self.database)

    def open_dev_console(self):
        self.dev_console = DevConsole()
        self.dev_console.show()

    def add_dev_result(self, text: str, img: np.array):
        if self.dev_console:
            self.dev_console.add_result(text, img)

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


class EntriesList(qt.QWidget):
    class ListEntry(qt.QWidget):
        deleted = qtc.pyqtSignal(qt.QWidget)

        def __init__(self, parent, entry: Entry):
            super().__init__(parent)
            self.entry = entry
            layout = qt.QGridLayout()
            image = qt.QLabel()
            image.setPixmap(gui.QPixmap(utils.image_to_qimage(entry.img)).scaledToWidth(300))
            layout.addWidget(image, 0, 0, Qt.AlignCenter)
            layout.addWidget(qt.QLabel("%s (%s)" % (entry.name, entry.group)), 1, 0, Qt.AlignCenter)
            delete_btn = qt.QPushButton("Delete", self)
            delete_btn.released.connect(lambda: self.deleted.emit(self))
            layout.addWidget(delete_btn, 2, 0, Qt.AlignCenter)
            self.setLayout(layout)

    def __init__(self, parent, database):
        super().__init__(parent)
        self.database = database

        self.area = qt.QScrollArea()
        widget = qt.QWidget()
        self.layout = qt.QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        for e in self.database.entries:
            list_entry = self.ListEntry(self, e)
            list_entry.deleted.connect(self.delete_entry)
            self.layout.addWidget(list_entry)

        widget.setLayout(self.layout)
        self.area.setWidget(widget)
        self.area.show()

    def delete_entry(self, entry: ListEntry):
        self.database.remove_entry(entry.entry)
        self.layout.removeWidget(entry)
        entry.deleteLater()
        self.layout.update()


class DevConsole(qt.QWidget):
    def __init__(self):
        super().__init__()
        self.main_layout = qt.QVBoxLayout()
        self.scroll_area = qt.QScrollArea()
        self.scroll_widget = qt.QWidget()
        self.scroll_layout = qt.QVBoxLayout()
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_widget.setLayout(self.scroll_layout)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.scroll_widget)
        self.main_layout.addWidget(self.scroll_area)
        self.setLayout(self.main_layout)

    def add_result(self, text: str, image: np.array):
        widget = qt.QWidget()
        layout = qt.QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        img = utils.numpy_to_qimage(image)
        label = qt.QLabel()
        label.setPixmap(gui.QPixmap(img))
        layout.addWidget(label, 0, 0, Qt.AlignCenter)
        layout.addWidget(qt.QLabel(text), 1, 0, Qt.AlignCenter)
        widget.setLayout(layout)
        self.scroll_layout.insertWidget(0, widget)
