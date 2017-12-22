from enum import Enum, unique, auto
from abc import ABC


@unique
class AugmentType(Enum):
    TEXT = auto()
    BOX = auto()


class Augment(ABC):
    def __init__(self, type: AugmentType):
        self.type = type
