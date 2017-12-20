from log import logger
import pickle
import numpy as np
from typing import List, Optional
from core import Image, Feature
from cv2 import KeyPoint


class Entry:
    def __init__(self, name: str, image: Image, features: List[Feature], group=None):
        self.name = name
        self.img: Image = image
        self.augments = []
        self.features = features
        self.group: Optional[str] = group

    @property
    def descriptors(self) -> np.ndarray:
        des = []
        for f in self.features:
            des.append(f.descriptor)
        return np.array(des)

    @property
    def key_points(self) -> List[KeyPoint]:
        kp = []
        for f in self.features:
            kp.append(f.key_point)
        return kp


class Database:
    def __init__(self, filename):
        self.filename = filename
        self.__entries = dict()

    @classmethod
    def connect(cls, file):
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
