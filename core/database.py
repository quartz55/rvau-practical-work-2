import pickle
from typing import List
from core import Image, Feature


class Entry:
    def __init__(self, name: str, image: Image, features: List[Feature]):
        self.name = name
        self.img: Image = image
        self.augments = []
        self.features = features

    @property
    def descriptors(self):
        des = []
        for f in self.features:
            des.append(f.descriptor)
        return des 

    @property
    def key_points(self):
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
            pickle.dump(self, file, pickle.HIGHEST_PROTOCOL)

    def add_entry(self, entry: Entry):
        self.__entries[entry.name] = entry

    @property
    def entries(self):
        return self.__entries.items()
