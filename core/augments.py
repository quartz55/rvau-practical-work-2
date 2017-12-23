from enum import Enum, unique, auto
from abc import ABC


@unique
class AugmentType(Enum):
    TEXT = auto()
    BOX = auto()
    ARROW = auto()
    ELLIPSE = auto()


class Augment(ABC):
    def __init__(self, type: AugmentType):
        self.type = type


class BoxAugment(Augment):
    def __init__(self, x, y, w, h):
        super().__init__(AugmentType.BOX)
        self.x = x
        self.y = y
        self.w = w
        self.h = h


class ArrowAugment(Augment):
    def __init__(self, x, y, length, rotation):
        super().__init__(AugmentType.ARROW)
        self.x = x
        self.y = y
        self.length = length
        self.rotation = rotation


class EllipseAugment(Augment):
    def __init__(self, x, y, w, h):
        super().__init__(AugmentType.ELLIPSE)
        self.x = x
        self.y = y
        self.w = w
        self.h = h
