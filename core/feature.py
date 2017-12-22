from typing import Tuple
import cv2
import numpy as np

# A Feature é a abstração escolhida para tratar os pontos chave da imagem
#
class Feature:
    def __init__(self, key_point: cv2.KeyPoint, descriptor: np.ndarray):
        self.descriptor: np.ndarray = descriptor
        self._key_point: dict = {
            'x': key_point.pt[0],
            'y': key_point.pt[1],
            'angle': key_point.angle, # orientação do key point
            'response': key_point.response, # response pela qual os key_points mais fortes foram selecionados. Pode ser usado para a posterior classificação ou subamostragem
            'octave': key_point.octave, # (pyramid layer) a partir do qual o key_point foi extraído
            'class_id': key_point.class_id # classe objeto (se os pontos de chave precisarem ser agrupados por um objeto ao qual pertencem)
        }
    # retorna o key_point
    @property
    def key_point(self) -> cv2.KeyPoint:
        kp = self._key_point
        return cv2.KeyPoint(kp['x'], kp['y'],
                            kp['angle'],
                            kp['response'],
                            kp['octave'],
                            kp['class_id'])

    # retorna a orientação do key_point
    @property
    def angle(self) -> float:
        return self.key_point.angle
    # retorna a posição x,y como tuplo
    @property
    def position(self) -> Tuple[float, float]:
        return self.key_point.pt
