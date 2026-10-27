# 第 10 章 · 类型注解与协议

> **卷一 · 语言**　|　前置知识：第 4、7 章　|　建议用时：55 分钟

> 类型注解不是运行时检查，而是写给静态分析工具、IDE 和未来读者的契约。

异常处理的是运行时错误，类型注解处理的是“写代码时的意图”。这一章讲 `list[int]`、`int | None`、`type` 别名、`TypedDict`、`Literal`、`Final`、泛型、`Protocol`、`overload` 和 `override`。

Python 仍然是动态类型语言：注解不会阻止你把 `str` 传给声明为 `int` 的参数。它们的主要价值是：

- 让静态检查器（mypy、pyright）提前发现错误；
- 让 IDE 提供补全和跳转；
- 让读者一眼看出接口契约；
- 让大型代码库更容易重构。

## 10.1 本章语法地图

| 语法/概念 | 本章出现的位置 |
|-----------|----------------|
| 变量注解 | `count: int = 0` |
| 参数/返回注解 | `def f(x: int) -> str:` |
| 内置泛型 | `list[int]`、`dict[str, int]` |
| 联合类型 | `int \| None`（3.10） |
| 类型别名 | `type Point = tuple[float, float]`（3.12） |
| `Final` | 常量 |
| `Literal` | 限定字面量值 |
| `TypedDict` | 字典的结构化类型 |
| 泛型函数 | `def first[T](items: list[T]) -> T:` |
| 泛型类 | `class Box[T]:` |
| `Protocol` | 结构化子类型 |
| `overload` | 重载签名（静态） |
| `override` | 标记覆盖（3.12） |
| `Self` | 返回自身类型（3.11） |

## 10.2 注解是元数据，不是强制检查

```python
def add(left: int, right: int) -> int:
    return left + right
```

调用 `add("a", "b")` 在运行时完全合法，返回 `"ab"`。解释器不会检查参数类型。

```python
print(add("a", "b"))   # ab
```

类型检查器会报错，但解释器不会。这是 Python 类型系统的核心：**静态检查可选，运行时保持动态**。

注解保存在 `__annotations__` 中：

```python
print(add.__annotations__)
# {'left': <class 'int'>, 'right': <class 'int'>, 'return': <class 'int'>}
```

## 10.3 内置泛型与联合类型

Python 3.9 起，内置容器可以直接下标：

```python
numbers: list[int] = [1, 2, 3]
mapping: dict[str, int] = {"a": 1}
point: tuple[float, float] = (1.0, 2.0)
unique: set[str] = {"a", "b"}
```

Python 3.10 起，用 `|` 表示联合类型：

```python
def find(key: str) -> int | None:
    ...
```

旧写法是 `Optional[int]` / `Union[int, str]`，仍然可用，但新代码通常用 `|`。

```python
value: int | str
```

`None` 不是“没有类型”，而是 `NoneType` 的唯一实例；`int | None` 表示“整数或 None”。

### `Any`

```python
from typing import Any

def parse(data: Any) -> Any:
    ...
```

`Any` 表示“放弃类型检查”。它会传染：从 `Any` 取出的值也是 `Any`。尽量少用，只在边界处（JSON、动态插件）使用。

### `Callable`

```python
from collections.abc import Callable

def apply(function: Callable[[int], int], value: int) -> int:
    return function(value)
```

`Callable[[参数类型], 返回类型]` 描述可调用对象。

## 10.4 类型别名

Python 3.12 的 `type` 语句：

```python
type Point = tuple[float, float]
type Handler = Callable[[int], str]
```

旧写法：

```python
Point = tuple[float, float]
```

`type` 别名是惰性求值的，可以引用后面才定义的类型；它还会创建独立的 `TypeAliasType`，在 `get_type_hints` 和类型检查器里有更清晰的语义。

类型别名适合：

- 给复杂类型起短名字；
- 表达领域概念（`UserId = int`）；
- 避免重复长泛型。

不要用别名隐藏重要语义，例如把 `str` 叫 `HTML` 却不做任何校验。

## 10.5 `TypedDict`、`Literal`、`Final`

### `TypedDict`

`TypedDict` 描述“有固定键的字典”：

```python
from typing import TypedDict

class Config(TypedDict):
    width: int
    height: int
    fullscreen: bool

config: Config = {"width": 800, "height": 600, "fullscreen": False}
```

它在运行时就是一个普通 `dict`，不会验证键；静态检查器会检查键名和值类型。

```python
area(config["width"], config["height"])
```

`total=False` 可以让所有键可选；`Required` / `NotRequired` 可以单独标记。

### `Literal`

`Literal` 限定值必须是某几个字面量之一：

```python
from typing import Literal

Level = Literal["debug", "info", "warning", "error"]

def log(level: Level, message: str) -> None:
    ...
```

调用 `log("verbose", ...)` 会被静态检查器拒绝；运行时仍然可以传。

### `Final`

`Final` 表示“不应再赋值”：

```python
from typing import Final

MAX_SIZE: Final = 100
```

静态检查器会阻止重新赋值；运行时不会。它适合模块级常量、类常量。

### `Annotated`

`Annotated` 给类型附加元数据：

```python
from typing import Annotated

UserId = Annotated[int, "database primary key"]
```

元数据可以被框架/验证库读取；标准库本身不会解释它。

## 10.6 泛型

### PEP 695（3.12）

```python
def first[T](items: list[T]) -> T:
    return items[0]


class Box[T]:
    def __init__(self, item: T) -> None:
        self.item = item

    def get(self) -> T:
        return self.item
```

`T` 是类型参数，作用域在函数/类内部。调用 `first([1, 2])` 时，静态检查器推导 `T = int`。

### 旧写法：`TypeVar` / `Generic`

```python
from typing import Generic, TypeVar

T = TypeVar("T")

def first(items: list[T]) -> T:
    return items[0]

class Box(Generic[T]):
    ...
```

旧写法仍然广泛存在于现有代码和库中。读代码时要能认出它；新代码在 3.12+ 可以优先用 PEP 695。

### 约束与边界

```python
def max_value[T: int | float](left: T, right: T) -> T:
    return left if left > right else right
```

`T: int | float` 是上界，表示 `T` 必须是 `int` 或 `float` 的子类型。

旧写法用 `TypeVar("T", bound=...)` 或 `TypeVar("T", int, float)`。

### 变型（variance）

- `list[int]` 不是 `list[object]` 的子类型（不变，invariant）；
- `Sequence[int]` 是 `Sequence[object]` 的子类型（协变，covariant）；
- `Callable[[object], int]` 与 `Callable[[int], object]` 的关系更复杂（逆变/协变）。

初学阶段先记住：**可变容器通常不变，只读容器/序列通常协变**。需要精确控制时查类型检查器文档。

## 10.7 `Protocol`：结构化子类型

`Protocol` 用“有哪些方法/属性”定义接口，而不是要求显式继承：

```python
from typing import Protocol

class SupportsArea(Protocol):
    def area(self) -> float:
        ...
```

任何有 `area() -> float` 的类都满足它：

```python
class Circle:
    def __init__(self, radius: float) -> None:
        self.radius = radius

    def area(self) -> float:
        return 3.141592653589793 * self.radius**2

def describe_area(shape: SupportsArea) -> str:
    return f"area = {shape.area():.2f}"
```

`Circle` 没有继承 `SupportsArea`，但静态检查器接受它。这就是**结构化子类型**（duck typing 的静态版本）。

### 运行时检查

```python
from typing import runtime_checkable

@runtime_checkable
class SupportsArea(Protocol):
    def area(self) -> float:
        ...
```

加了 `@runtime_checkable` 才能用 `isinstance(obj, SupportsArea)`。它只检查方法/属性是否存在，不检查签名；运行时检查能力有限。

### Protocol 与 ABC

| 维度 | `Protocol` | `ABC` |
|------|------------|-------|
| 子类型关系 | 结构化（隐式） | 名义（显式继承） |
| 运行时检查 | 需要 `runtime_checkable` | 原生支持 |
| 适用场景 | 第三方类型、解耦接口 | 自己控制的类层级 |
| 实现要求 | 方法/属性匹配 | 继承并实现抽象方法 |

## 10.8 `overload`、`override`、`Self`

### `overload`

`@overload` 给同一个函数声明多个签名：

```python
from typing import overload

@overload
def double(value: int) -> int:
    ...

@overload
def double(value: str) -> str:
    ...

def double(value: int | str) -> int | str:
    return value * 2
```

`@overload` 声明只对静态检查器可见；运行时只有最后一个实现。调用时按实现执行。

不要用它做运行时分派；需要运行时分派时用 `isinstance` 或 `singledispatch`。

### `override`

Python 3.12 的 `@override` 标记“这个方法覆盖了基类方法”：

```python
from typing import override

class LoudBox(Box[str]):
    @override
    def get(self) -> str:
        ...
```

静态检查器会验证基类确实有同名方法。它不会改变运行时行为。

### `Self`

`Self` 表示“当前类的类型”，适合返回 `self` 或克隆：

```python
from typing import Self

class Box[T]:
    def clone(self) -> Self:
        return type(self)(self.item)
```

子类调用 `clone()` 时，返回类型仍然是子类，而不是基类。

## 10.9 注解的求值时机

默认情况下，函数/类的注解在定义时求值：

```python
def f(x: UndefinedType) -> None:   # NameError
    ...
```

前向引用可以写成字符串：

```python
class Node:
    def __init__(self, next: "Node | None" = None) -> None:
        self.next = next
```

或者文件开头加：

```python
from __future__ import annotations
```

这会把所有注解保存为字符串，延迟解析。它能让前向引用和循环依赖更容易处理，但也会影响运行时读取注解的工具。

Python 3.14 起，注解默认惰性求值（PEP 649/749），`from __future__ import annotations` 的历史行为会逐渐退出主流。本书以 3.12 为基线，遇到需要运行时注解的库时要查版本。

## 10.10 静态检查工具

常见工具：

- **mypy**：最常用的类型检查器；
- **pyright**：基于 TypeScript 的类型检查器，VS Code 的 Pylance 使用它；
- **pyre**、**pytype**：其他实现。

运行示例：

```sh
mypy 10-typing/typing_demo.py
pyright 10-typing/typing_demo.py
```

它们会读取注解、推断类型、报告不匹配。解释器本身不会运行这些检查。

类型检查不是“写完注解就自动正确”；它需要：

- 注解准确；
- 检查器配置正确；
- 第三方库有 stub（`.pyi`）或 `py.typed`；
- 团队约定如何处理 `Any` 和 `# type: ignore`。

## 10.11 代码导览

[`typing_demo.py`](typing_demo.py) 分成六部分：

- `show_aliases()`：`type` 别名、`Final`、`get_type_hints`；
- `show_generics()`：PEP 695 泛型函数、泛型类、`Self`、`override`；
- `show_protocol()`：`Protocol`、`runtime_checkable`；
- `show_typed_dict()`：`TypedDict`；
- `show_overloads()`：`overload`、`Literal`；
- `show_runtime()`：注解不强制运行时类型。

运行：

```sh
python3 10-typing/typing_demo.py
```

## 10.12 常见陷阱

| 写法 | 问题 | 建议 |
|------|------|------|
| 以为注解会运行时检查 | 不会 | 用 mypy/pyright 或显式校验 |
| 用 `Any` 到处偷懒 | 失去类型安全 | 只在边界使用 |
| 可变默认值与类型注解混用 | 运行时仍共享 | 用 `default_factory`/`None` |
| `list[int]` 在 3.8 不可用 | 版本差异 | 3.9+ 或 `List[int]` |
| `int \| None` 在 3.9 不可用 | 版本差异 | 3.10+ 或 `Optional[int]` |
| `@overload` 写实现 | 运行时只保留最后一个 | 实现只写一次 |
| Protocol 忘记 `runtime_checkable` | `isinstance` 报错 | 加装饰器 |
| 把 `TypedDict` 当运行时验证 | 只是静态结构 | 用显式校验/库 |
| 循环引用注解不求值 | `NameError` | 字符串注解/`future` |
| `# type: ignore` 滥用 | 隐藏真实错误 | 尽量具体、加原因 |

## 10.13 语法卡片

| 术语 | 一句话定义 | 本章例子 |
|------|------------|----------|
| 类型注解 | 给变量/参数/返回值附加类型信息 | `x: int` |
| 内置泛型 | 用 `[]` 参数化容器 | `list[int]` |
| 联合类型 | 多个类型之一 | `int \| None` |
| 类型别名 | 给类型起名字 | `type Point = ...` |
| `TypedDict` | 固定键的字典类型 | `class Config(TypedDict):` |
| `Literal` | 限定字面量值 | `Literal["debug"]` |
| `Final` | 不应重新赋值 | `MAX: Final = 100` |
| 泛型 | 参数化类型 | `Box[T]` |
| `Protocol` | 结构化接口 | `class SupportsArea(Protocol):` |
| `overload` | 多个静态签名 | `@overload` |
| `override` | 标记覆盖 | `@override` |
| `Self` | 当前类类型 | `-> Self` |

## 10.14 练习

1. **基础注解**：给一个函数加上参数/返回注解，打印 `__annotations__`。
2. **联合类型**：写 `find` 返回 `int | None`，调用后检查 `is None`。
3. **泛型**：用 PEP 695 写 `first[T]` 和 `Box[T]`，用不同类型调用。
4. **Protocol**：定义 `SupportsArea`，让 `Circle` 不继承它也能传给 `describe_area`。
5. **TypedDict**：定义 `Config`，传入缺键/多键的字典，用 mypy 检查（如果安装）。
6. **Literal**：定义 `Level`，尝试传非法字符串，观察静态检查器报错。
7. **overload**：为 `double(int)` 和 `double(str)` 写重载签名，再用实现统一处理。
8. **Self**：给 `Box` 加 `clone`，子类调用时观察返回类型。
9. **运行时**：把 `"a", "b"` 传给 `add(int, int)`，确认解释器不报错；再运行 mypy 对比。
10. **破坏实验**：把 `type Point` 改成普通赋值 `Point = tuple[float, float]`，比较 `get_type_hints` 的输出。

## 10.15 下一章

**第 11 章 · 综合练习：一个小型表达式求值器**

前面十章分别讲了对象、表达式、控制流、函数、容器、字符串、类、模块、异常和类型注解。下一章不再引入新语法，而是把它们拼成一个真正能运行的小程序：一个支持 `+ - * /`、括号、一元正负号和十进制小数的表达式求值器。

届时，词法分析、递归下降、错误报告、`dataclass`、`Enum`、`match` 和自定义异常，会第一次同时出现在一个程序里。
