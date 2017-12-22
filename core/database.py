import pickle
from cv2 import KeyPoint
from typing import List, Optional

import numpy as np

from core import Image, Feature
from log import logger


# Entry é a classe onde usamos para guardar a imagem, as suas features,e as suas propriedades de aumento
# Ver o feature.py, image.py dentro desta pasta

class Entry:
    def __init__(self, name: str, image: Image, features: List[Feature], group=None):
        self.name = name
        self.img: Image = image
        self.augments = []
        self.features = features
        self.group: Optional[str] = group

    # função que retorna o array com os descritores de cada feature
    @property
    def descriptors(self) -> np.ndarray:
        return np.array([f.descriptor for f in self.features])

    # retorna uma lista com todos os pontos-chave de todas as features
    @property
    def key_points(self) -> List[KeyPoint]:
        return [f.key_point for f in self.features]

# abstração onde se guarda o conjunto das Entry para se poder gerir uma base de dados
class Database:
    def __init__(self, filename):
        self.filename = filename
        self.__entries = dict()

    # método para a ligação à base de dados
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
    # gravação do estado da base de dados para permitir que se reutilize as Entry
    def save(self):
        with open(self.filename, 'wb') as file:
            logger.info('Saving database: %s', self.filename)
            pickle.dump(self, file, pickle.HIGHEST_PROTOCOL)
    # inserir Entry na database
    def add_entry(self, entry: Entry):
        self.__entries[entry.name] = entry
        self.save()
    # retornar o array de Entry
    @property
    def entries(self):
        return self.__entries.values()

    def entry(self, name) -> Optional[Entry]:
        return self.__entries.get(name)
