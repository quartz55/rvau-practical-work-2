from enum import Enum, unique, auto
from abc import ABC


@unique
class AugmentType(Enum):
    TEXT = auto()
    BOX = auto()


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
