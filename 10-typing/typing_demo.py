#!/usr/bin/env python3
"""
============================================================================
 Python 语言圣经 · 第 10 章
 类型注解与协议
============================================================================

 本文件观察：

    1. 变量、参数、返回值的类型注解
    2. 内置泛型与联合类型
    3. Protocol、TypedDict、Literal、Final
    4. 泛型函数/类（PEP 695，3.12）
    5. 运行时不强制类型

 运行：
     python3 typing_demo.py

注意：
    类型注解主要服务于静态检查工具（mypy、pyright 等）；
    Python 解释器不会因为类型不匹配而自动报错。

============================================================================
"""

from typing import Final, Literal, Protocol, Self, TypedDict, get_type_hints, overload, override, runtime_checkable

type Point = tuple[float, float]

MAX_SIZE: Final = 100
Level = Literal["debug", "info", "warning", "error"]


def distance(first: Point, second: Point) -> float:
    dx = first[0] - second[0]
    dy = first[1] - second[1]
    return (dx * dx + dy * dy) ** 0.5


def first[T](items: list[T]) -> T:
    return items[0]


class Box[T]:
    def __init__(self, item: T) -> None:
        self.item = item

    def get(self) -> T:
        return self.item

    def clone(self) -> Self:
        return type(self)(self.item)


class LoudBox[T](Box[T]):
    @override
    def get(self) -> T:
        value = super().get()
        print("LOUD:", value)
        return value


@runtime_checkable
class SupportsArea(Protocol):
    def area(self) -> float:
        ...


class Circle:
    def __init__(self, radius: float) -> None:
        self.radius = radius

    def area(self) -> float:
        return 3.141592653589793 * self.radius**2


class Config(TypedDict):
    width: int
    height: int
    fullscreen: bool


def area(config: Config) -> int:
    return config["width"] * config["height"]


def log(level: Level, message: str) -> None:
    print(f"[{level}] {message}")


@overload
def double(value: int) -> int:
    ...


@overload
def double(value: str) -> str:
    ...


def double(value: int | str) -> int | str:
    return value * 2


def describe_area(shape: SupportsArea) -> str:
    return f"area = {shape.area():.2f}"


def show_aliases() -> None:
    print("== aliases ==")
    print("Point:", Point)
    print("MAX_SIZE:", MAX_SIZE)
    print("distance:", distance((0.0, 0.0), (3.0, 4.0)))
    print("type hints:", get_type_hints(distance))


def show_generics() -> None:
    print("\n== generics ==")

    print("first([1, 2, 3]):", first([1, 2, 3]))
    print("first(['a', 'b']):", first(["a", "b"]))

    box = Box(42)
    print("box.get():", box.get())
    print("box.clone().get():", box.clone().get())

    loud = LoudBox("hello")
    print("loud.get():", loud.get())


def show_protocol() -> None:
    print("\n== Protocol ==")

    circle = Circle(2.0)
    print("describe_area(circle):", describe_area(circle))
    print("runtime protocol check:", isinstance(circle, SupportsArea))


def show_typed_dict() -> None:
    print("\n== TypedDict ==")

    config: Config = {"width": 800, "height": 600, "fullscreen": False}
    print("config:", config)
    print("area:", area(config))


def show_overloads() -> None:
    print("\n== overload / Literal ==")

    log("info", "starting")
    print("double(21):", double(21))
    print("double('ab'):", double("ab"))


def show_runtime() -> None:
    print("\n== runtime is not enforced ==")

    def annotated_add(left: int, right: int) -> int:
        return left + right

    # 这行在运行时完全合法；静态检查器才会抱怨。
    print("annotated_add('a', 'b'):", annotated_add("a", "b"))  # type: ignore[arg-type]

    # 注解只是对象上的元数据，不会改变函数行为。
    print("distance annotations:", distance.__annotations__)


def main() -> None:
    show_aliases()
    show_generics()
    show_protocol()
    show_typed_dict()
    show_overloads()
    show_runtime()


if __name__ == "__main__":
    main()
