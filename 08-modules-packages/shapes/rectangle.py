"""矩形。"""

from .base import Shape


class Rectangle(Shape):
    def __init__(self, width: float, height: float) -> None:
        super().__init__("rectangle")
        self.width = width
        self.height = height

    def area(self) -> float:
        return self.width * self.height
