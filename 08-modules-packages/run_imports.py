#!/usr/bin/env python3
"""
============================================================================
 Python 语言圣经 · 第 8 章
 模块、包与导入
============================================================================

 本文件观察：

    1. __name__ 与“直接运行 / 被导入”的区别
    2. 包、__init__.py、相对导入
    3. import、from ... import、模块缓存
    4. __all__ 与公共接口
    5. sys.path 与脚本目录

 运行：
     python3 run_imports.py

============================================================================
"""

import sys

import shapes
import shapes.circle as circle_module
from shapes import Circle, Rectangle


def show_module() -> None:
    print("== module ==")
    print("__name__:", __name__)
    print("sys.path[0]:", sys.path[0])
    print("shapes.__file__:", shapes.__file__)
    print("shapes.__all__:", shapes.__all__)


def show_imports() -> None:
    print("\n== imports ==")

    circle = Circle(2.0)
    rectangle = Rectangle(3.0, 4.0)

    print("circle:", circle, ", area =", circle.area())
    print("rectangle:", rectangle, ", area =", rectangle.area())

    print("Circle is shapes.Circle:", Circle is shapes.Circle)
    print("circle module:", circle_module.__name__)

    # 模块对象会被缓存到 sys.modules；再次 import 得到同一个对象。
    import shapes as shapes_again

    print("same module object:", shapes is shapes_again)
    print("cached:", "shapes" in sys.modules)


def show_public_api() -> None:
    print("\n== public API ==")

    for name in shapes.__all__:
        value = getattr(shapes, name)
        print(f"{name}: {value.__name__}")

    # 包可以隐藏内部模块；下面的导入仍然可行，但它不属于 __all__ 的公共约定。
    from shapes.base import Shape

    print("Shape is abstract:", Shape.__abstractmethods__)


def main() -> None:
    show_module()
    show_imports()
    show_public_api()


if __name__ == "__main__":
    main()
