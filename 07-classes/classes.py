#!/usr/bin/env python3
"""
============================================================================
 Python 语言圣经 · 第 7 章
 类与对象模型
============================================================================

 本文件观察：

    1. class、实例属性、类属性、方法
    2. 构造、表示、相等、运算符重载
    3. property、classmethod、staticmethod
    4. 继承、super、MRO、抽象基类
    5. dataclass、__slots__、名称改编

 运行：
     python3 classes.py

============================================================================
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import ClassVar


class Vector:
    """二维向量：一个最小的特殊方法示例。"""

    __slots__ = ("x", "y")
    count: ClassVar[int] = 0

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
        type(self).count += 1

    def __repr__(self) -> str:
        return f"Vector({self.x}, {self.y})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vector):
            return NotImplemented
        return (self.x, self.y) == (other.x, other.y)

    def __add__(self, other: "Vector") -> "Vector":
        if not isinstance(other, Vector):
            return NotImplemented
        return Vector(self.x + other.x, self.y + other.y)

    def __len__(self) -> int:
        return 2

    def __iter__(self):
        return iter((self.x, self.y))

    def __getitem__(self, index):
        return (self.x, self.y)[index]

    @property
    def magnitude(self) -> float:
        return (self.x * self.x + self.y * self.y) ** 0.5

    @classmethod
    def from_pair(cls, pair: tuple[int, int]) -> "Vector":
        return cls(pair[0], pair[1])

    @staticmethod
    def origin() -> "Vector":
        return Vector(0, 0)

    @classmethod
    def created(cls) -> int:
        return cls.count


class Shape(ABC):
    def __init__(self, name: str) -> None:
        self.name = name

    @abstractmethod
    def area(self) -> float:
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"{type(self).__name__}(name={self.name!r})"


class Circle(Shape):
    def __init__(self, radius: float) -> None:
        super().__init__("circle")
        self.radius = radius

    def area(self) -> float:
        return 3.141592653589793 * self.radius**2


class Rectangle(Shape):
    def __init__(self, width: float, height: float) -> None:
        super().__init__("rectangle")
        self.width = width
        self.height = height

    def area(self) -> float:
        return self.width * self.height


@dataclass(frozen=True, order=True)
class Point:
    x: int
    y: int


class Secret:
    def __init__(self) -> None:
        self.__value = 42

    def reveal(self) -> int:
        return self.__value


class A:
    def who(self) -> str:
        return "A"


class B(A):
    def who(self) -> str:
        return "B"


class C(A):
    def who(self) -> str:
        return "C"


class D(B, C):
    pass


def show_vector() -> None:
    print("== Vector ==")

    first = Vector(3, 4)
    second = Vector(1, 2)
    third = Vector.from_pair((3, 4))

    print("first:", first)
    print("second:", second)
    print("first + second:", first + second)
    print("first == third:", first == third)
    print("first is third:", first is third)
    print("len(first):", len(first))
    print("list(first):", list(first))
    print("first[0]:", first[0])
    print("first.magnitude:", first.magnitude)
    print("Vector.origin():", Vector.origin())
    print("created:", Vector.created())
    print("count is shared:", first.count, second.count)

    try:
        first.z = 9
    except AttributeError as error:
        print("__slots__ prevents z ->", type(error).__name__, error)

    print("__dict__ exists:", hasattr(first, "__dict__"))


def show_inheritance() -> None:
    print("\n== inheritance ==")

    shapes: list[Shape] = [Circle(2), Rectangle(3, 4)]
    for shape in shapes:
        print(repr(shape), "area =", shape.area())

    print("D.__mro__:")
    for cls in D.__mro__:
        print(" ", cls.__name__)
    print("D().who():", D().who())


def show_dataclass() -> None:
    print("\n== dataclass ==")

    first = Point(1, 2)
    second = Point(1, 3)

    print("first:", first)
    print("first == Point(1, 2):", first == Point(1, 2))
    print("first < second:", first < second)

    try:
        first.x = 99
    except Exception as error:
        print("frozen dataclass ->", type(error).__name__, error)


def show_name_mangling() -> None:
    print("\n== name mangling ==")

    secret = Secret()
    print("secret.reveal():", secret.reveal())
    print("secret._Secret__value:", secret._Secret__value)
    print("has __value:", hasattr(secret, "__value"))


def main() -> None:
    show_vector()
    show_inheritance()
    show_dataclass()
    show_name_mangling()
    print("\nfinal Vector count:", Vector.created())


if __name__ == "__main__":
    main()
