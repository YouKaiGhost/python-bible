"""形状包的公共基类。"""

from abc import ABC, abstractmethod


class Shape(ABC):
    """所有形状的抽象基类。"""

    def __init__(self, name: str) -> None:
        self.name = name

    @abstractmethod
    def area(self) -> float:
        """返回面积。"""

    def __repr__(self) -> str:
        return f"{type(self).__name__}(name={self.name!r})"
