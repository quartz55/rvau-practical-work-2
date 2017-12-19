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
        entry_gui: qt.QGraphicsItem = self.editor_scene.entry['gui']
        if entry_gui is not None:
            entry_rect = entry_gui.boundingRect().getCoords()
            aspect_ratio = (entry_rect[2] - entry_rect[0] / entry_rect[3] / entry_rect[1])
            # self.scale()

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
