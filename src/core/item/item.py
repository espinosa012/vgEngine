
from core import GameObject


class BaseItem(GameObject):


    def render(self, renderer):
        pass

    def update(self, delta_time: float):
        pass