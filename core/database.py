import pickle
from cv2 import KeyPoint
from typing import List, Optional

import numpy as np

from core import Image, Feature
from core.augments import Augment
from log import logger


class Entry:
    def __init__(self, name: str, image: Image, features: List[Feature], augments: Optional[List[Augment]] = None,
                 group=None):
        self.name = name
        self.img: Image = image
        self.augments = augments if augments is not None else []
        self.features = features
        self.group: Optional[str] = group

    @property
    def descriptors(self) -> np.ndarray:
        return np.array([f.descriptor for f in self.features])

    @property
    def key_points(self) -> List[KeyPoint]:
        return [f.key_point for f in self.features]


class Database:
    def __init__(self, filename):
        self.filename = filename
        self.__entries = dict()

    @classmethod
    def connect(cls, filename):
        try:
            file = open(filename, 'rb')
        except FileNotFoundError:
            db = cls(filename)
            db.save()
            return db
        else:
            return pickle.load(file)

    def save(self):
        with open(self.filename, 'wb') as file:
            logger.info('Saving database: %s', self.filename)
            pickle.dump(self, file, pickle.HIGHEST_PROTOCOL)

    def add_entry(self, entry: Entry):
        self.__entries[entry.name] = entry
        self.save()

    @property
    def entries(self):
        return self.__entries.values()

    def entry(self, name) -> Optional[Entry]:
        return self.__entries.get(name)
