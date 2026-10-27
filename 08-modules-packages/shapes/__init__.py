"""shapes 包：把形状相关模块组织在一起。

__init__.py 让目录成为常规包，并定义导入这个包时暴露的公共名字。
"""

from .base import Shape
from .circle import Circle
from .rectangle import Rectangle

__all__ = ["Shape", "Circle", "Rectangle"]
