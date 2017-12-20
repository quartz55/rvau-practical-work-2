from log import logger
from typing import List
from PyQt5 import (QtWidgets as qt,
                   QtGui as gui,
                   QtCore as qtc)
from PyQt5.QtCore import Qt
from gui.entry_editor_scene import EntryEditorScene


class EntryEditorView(qt.QGraphicsView):
    def __init__(self, scene: EntryEditorScene):
        super().__init__(scene)
        self.editor_scene = scene
        scene.entry_changed.connect(self.handle_entry_changed)
        self.viewport().grabGesture(Qt.PinchGesture)
        self.setFrameStyle(0)

    def handle_entry_changed(self):
        self.reset_zoom()
        self.fit_to_entry()

    def fit_to_entry(self):
        if self.editor_scene.entry is not None:
            self.fitInView(self.editor_scene.entry['gui'], Qt.KeepAspectRatio)

    def reset_zoom(self):
        self.resetTransform()

    def resizeEvent(self, event: gui.QResizeEvent):
        self.fit_to_entry()
        # if self.editor_scene.entry is not None:
        #     entry_ui: qt.QGraphicsItem = self.editor_scene.entry['gui']
        #     entry_rect: qtc.QRectF = entry_ui.boundingRect()
        #     entry_ratio = entry_rect.width() / entry_rect.height()
        #     screen_ratio = event.size().width() / event.size().height()
        #     factor = event.size().height() / event.oldSize().height() if screen_ratio > entry_ratio else event.size().width() / event.oldSize().width()
        #     self.scale(factor, factor)
        super().resizeEvent(event)

    def viewportEvent(self, event: qtc.QEvent):
        if event.type() == qtc.QEvent.Gesture:
            return self.gesture_event(event)
        return super().viewportEvent(event)

    def gesture_event(self, event: qt.QGestureEvent) -> bool:
        pinch: qt.QPinchGesture = event.gesture(Qt.PinchGesture)
        if pinch is not None:
            zoom_factor = pinch.totalScaleFactor()
            self.setTransformationAnchor(qt.QGraphicsView.NoAnchor)
            self.setResizeAnchor(qt.QGraphicsView.NoAnchor)
            self.scale(zoom_factor, zoom_factor)
        return True
