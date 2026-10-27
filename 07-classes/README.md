# 第 7 章 · 类与对象模型

> **卷一 · 语言**　|　前置知识：第 1–6 章　|　建议用时：70 分钟

> Python 的类不是“把函数和数据包在一起”的模板。它是一套运行时的属性查找规则，以及一组可以被特殊语法调用的特殊方法。

字符串是标准库提供的不可变对象。这一章讲如何定义自己的对象：类、实例、方法、属性、特殊方法、继承、MRO、dataclass 和 `__slots__`。

Python 的对象模型有几个关键点：

- 类本身也是对象；
- 方法是通过描述符协议绑定到实例的函数；
- `obj.attr` 的查找顺序不是“先实例字典再类字典”这么简单；
- 特殊方法由解释器在类型上查找，而不是在实例上；
- 继承使用 C3 线性化，`super()` 不是“调用父类”，而是“按 MRO 找下一个”。

## 7.1 本章语法地图

| 语法/概念 | 本章出现的位置 |
|-----------|----------------|
| `class` | `class Vector:` |
| 实例属性 | `self.x = x` |
| 类属性 | `count: ClassVar[int] = 0` |
| 方法 | `def magnitude(self):` |
| `__init__` | 初始化实例 |
| `__repr__` / `__str__` | 对象表示 |
| `__eq__` | 相等比较 |
| `__len__` / `__getitem__` / `__iter__` | 容器协议 |
| `__add__` | 运算符重载 |
| `@property` | 计算属性 |
| `@classmethod` / `@staticmethod` | 类方法/静态方法 |
| 继承 | `class Circle(Shape):` |
| `super()` | 按 MRO 调用下一个实现 |
| `ABC` / `@abstractmethod` | 抽象基类 |
| `@dataclass` | 自动生成特殊方法 |
| `__slots__` | 限制实例属性 |
| 名称改编 | `__value` → `_Class__value` |

## 7.2 类与实例

```python
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

vector = Vector(3, 4)
```

`class` 语句做两件事：

1. 创建一个类对象；
2. 把类名绑定到这个对象上。

`Vector(3, 4)` 调用类对象，创建实例。实例是类的实例，类也是对象（通常是 `type` 的实例）：

```python
type(vector)       # <class '__main__.Vector'>
type(Vector)       # <class 'type'>
isinstance(vector, Vector)  # True
```

### 实例属性与类属性

```python
class Counter:
    total = 0          # 类属性

    def __init__(self):
        self.value = 0 # 实例属性
```

- 实例属性保存在实例的 `__dict__`（或 `__slots__`）；
- 类属性保存在类的 `__dict__`；
- 读取 `obj.attr` 时，先找实例，再找类/MRO；
- 给 `obj.attr` 赋值会创建/修改**实例**属性，不会修改类属性。

```python
first = Counter()
second = Counter()

first.value = 10
Counter.total = 5

print(first.value, second.value)   # 10 0
print(first.total, second.total)   # 5 5
```

可变类属性会被所有实例共享：

```python
class Bad:
    items = []

first = Bad()
second = Bad()
first.items.append(1)
print(second.items)   # [1]
```

需要每个实例独立容器时，在 `__init__` 里创建。

## 7.3 方法与 `self`

```python
class Vector:
    def magnitude(self):
        return (self.x**2 + self.y**2) ** 0.5
```

`self` 是实例方法的第一个参数，调用时由 Python 自动传入：

```python
vector.magnitude()
# 等价于
Vector.magnitude(vector)
```

`self` 不是关键字，只是约定；换成 `this` 也能运行，但没有人会感谢你。

方法本质上也是类属性，只是它是函数，函数实现了描述符协议，所以通过实例访问时会绑定成“方法对象”。

## 7.4 `__init__` 与 `__new__`

`__init__` 是初始化方法：

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
```

它负责把已经创建好的实例带入有效状态，返回值必须是 `None`。

真正的对象创建由 `__new__` 负责：

```python
class Point:
    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        return instance

    def __init__(self, x, y):
        ...
```

大多数类不需要重写 `__new__`。需要控制实例创建（单例、不可变类型、元类）时才用。

## 7.5 特殊方法

特殊方法（dunder methods）让对象支持内置语法：

| 特殊方法 | 触发方式 |
|----------|----------|
| `__repr__` | `repr(obj)`、调试输出 |
| `__str__` | `str(obj)`、`print(obj)` |
| `__eq__` | `obj == other` |
| `__hash__` | `hash(obj)`、字典键 |
| `__len__` | `len(obj)` |
| `__getitem__` | `obj[key]` |
| `__iter__` | `for x in obj` |
| `__contains__` | `x in obj` |
| `__add__` | `obj + other` |
| `__call__` | `obj(...)` |
| `__enter__` / `__exit__` | `with obj:` |
| `__bool__` | `bool(obj)` |

### `__repr__` 与 `__str__`

```python
class Vector:
    def __repr__(self):
        return f"Vector({self.x}, {self.y})"
```

- `__repr__` 面向开发者，目标是“尽量可重建”；
- `__str__` 面向用户，目标是可读；
- 如果只定义 `__repr__`，`str()` 会回退到它；
- 容器打印元素时使用 `repr`。

### `__eq__` 与 `__hash__`

```python
def __eq__(self, other):
    if not isinstance(other, Vector):
        return NotImplemented
    return (self.x, self.y) == (other.x, other.y)
```

返回 `NotImplemented` 表示“我不支持与这个类型比较”，让 Python 尝试对方的反射方法，而不是直接判为不相等。

定义 `__eq__` 后，Python 默认把 `__hash__` 设为 `None`，对象变成不可哈希。如果对象是不可变的，可以显式定义：

```python
def __hash__(self):
    return hash((self.x, self.y))
```

相等对象必须有相等哈希；可变对象通常不应该可哈希。

### 容器协议

```python
def __len__(self):
    return 2

def __iter__(self):
    return iter((self.x, self.y))

def __getitem__(self, index):
    return (self.x, self.y)[index]
```

实现这些方法后，对象就能用 `len()`、`for`、下标访问。`__contains__` 可以单独实现，否则 Python 会退回用 `__iter__` 线性搜索。

### 运算符重载

```python
def __add__(self, other):
    if not isinstance(other, Vector):
        return NotImplemented
    return Vector(self.x + other.x, self.y + other.y)
```

运算符重载不是“让对象看起来像数字”的装饰；它应该保持和内置类型一致的语义。不要重载 `+` 去做“保存到数据库”这种事。

### `__call__`

实现了 `__call__` 的实例可以像函数一样调用：

```python
class Adder:
    def __init__(self, amount):
        self.amount = amount

    def __call__(self, value):
        return value + self.amount
```

## 7.6 `property`、`classmethod`、`staticmethod`

### `property`

```python
class Circle:
    def __init__(self, radius):
        self.radius = radius

    @property
    def area(self):
        return 3.141592653589793 * self.radius**2
```

`circle.area` 看起来像属性，实际调用 getter。`property` 适合：

- 计算属性；
- 给属性加校验；
- 保持向后兼容的 API。

可写 property：

```python
class Temperature:
    def __init__(self, celsius):
        self._celsius = celsius

    @property
    def celsius(self):
        return self._celsius

    @celsius.setter
    def celsius(self, value):
        if value < -273.15:
            raise ValueError("below absolute zero")
        self._celsius = value
```

`property` 本身是描述符；第 7.10 节会从属性查找的角度解释它。

### `classmethod`

```python
class Vector:
    @classmethod
    def from_pair(cls, pair):
        return cls(pair[0], pair[1])
```

`classmethod` 的第一个参数是类，不是实例。它常用于替代构造函数、工厂方法、多态构造。

### `staticmethod`

```python
class Vector:
    @staticmethod
    def origin():
        return Vector(0, 0)
```

`staticmethod` 不接收实例或类，只是把函数放进类命名空间。它适合与类相关但不需要访问类状态的工具函数。

## 7.7 继承、MRO 与 `super`

```python
class Shape:
    def __init__(self, name):
        self.name = name

    def area(self):
        raise NotImplementedError

class Circle(Shape):
    def __init__(self, radius):
        super().__init__("circle")
        self.radius = radius

    def area(self):
        return 3.141592653589793 * self.radius**2
```

- 派生类自动获得基类的方法；
- 子类可以覆盖方法；
- `super()` 按 MRO 调用下一个实现；
- `isinstance(circle, Shape)` 为真；
- 多态：通过基类接口调用子类实现。

### MRO

Python 使用 C3 线性化计算方法解析顺序：

```python
class A: ...
class B(A): ...
class C(A): ...
class D(B, C): ...

D.__mro__   # (D, B, C, A, object)
```

查找属性时按 MRO 从左到右。`D().who()` 会先找 `D`，再找 `B`，再找 `C`，再找 `A`。

`super()` 不是“调用父类”，而是“调用 MRO 中当前类之后的下一个实现”。在多重继承里，这个区别很重要。

### 抽象基类

```python
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self):
        ...
```

`ABC` 和 `@abstractmethod` 让类不能被直接实例化，除非子类实现了所有抽象方法。它适合定义接口和强制契约。

### 组合优于继承

继承表达“是一种”（is-a）；组合表达“有一个”（has-a）。很多设计问题用组合更简单：

```python
class Engine:
    ...

class Car:
    def __init__(self):
        self.engine = Engine()
```

不要为了复用几行代码而建立复杂的继承层级。Python 的多重继承很强，但越强越容易失控。

## 7.8 `dataclass`

`dataclasses` 自动生成 `__init__`、`__repr__`、`__eq__` 等：

```python
from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int
```

生成的 `__init__` 接收 `x`、`y`，`__repr__` 打印 `Point(x=1, y=2)`，`__eq__` 按字段比较。

常用选项：

```python
@dataclass(frozen=True, order=True)
class Point:
    x: int
    y: int
```

- `frozen=True`：不可变，赋值抛 `FrozenInstanceError`；
- `order=True`：生成 `<`、`<=`、`>`、`>=`；
- `default_factory`：为可变字段提供工厂；
- `field(default=...)`：字段配置。

```python
from dataclasses import dataclass, field

@dataclass
class Inventory:
    items: list[str] = field(default_factory=list)
```

不要写 `items: list[str] = []`；可变默认值会被所有实例共享。

`dataclass` 是标准库工具，不是语法；它生成的特殊方法仍然遵循 Python 对象模型。

## 7.9 `__slots__` 与名称改编

### `__slots__`

```python
class Vector:
    __slots__ = ("x", "y")

    def __init__(self, x, y):
        self.x = x
        self.y = y
```

`__slots__` 告诉 Python 不要为实例创建 `__dict__`，只分配指定名字的存储。好处：

- 减少内存；
- 防止拼错属性名悄悄创建新属性；
- 访问速度可能更快。

限制：

- 不能动态添加未列出的属性；
- 继承时要小心：子类如果没有 `__slots__`，仍会有 `__dict__`；
- 不是访问控制，只是存储布局。

### 名称改编

```python
class Secret:
    def __init__(self):
        self.__value = 42
```

`__value` 会被改编为 `_Secret__value`，以避免子类意外覆盖。它不是“私有”，只是减少命名冲突：

```python
secret._Secret__value   # 仍然可以访问
```

不要用双下划线做安全边界；它只是命名约定 + 编译器改写。

## 7.10 属性查找与描述符

`obj.attr` 的查找大致是：

1. 在类型（及其 MRO）中找**数据描述符**（有 `__get__` 和 `__set__`）；
2. 如果没找到，找实例的 `__dict__`；
3. 再找类型中的非数据描述符/普通类属性；
4. 如果都没有，调用 `__getattr__`（如果定义了）；
5. 否则抛 `AttributeError`。

函数是**非数据描述符**：通过实例访问时，`__get__` 返回绑定方法。`property` 是**数据描述符**：它优先于实例字典，所以 `obj.area` 会调用 getter，而不是读取实例里同名属性。

这就是为什么：

```python
class Example:
    @property
    def value(self):
        return 42

example = Example()
example.__dict__["value"] = 99
print(example.value)   # 42，property 优先
```

`__getattr__` 只在正常查找失败后调用；`__getattribute__` 拦截所有属性访问，容易写坏，除非你非常清楚后果。

描述符是 Python 对象模型最底层的机制之一；`property`、`classmethod`、`staticmethod`、函数绑定都建立在它上面。

### 猴子补丁

Python 允许运行时修改类：

```python
def shout(self):
    return self.name.upper()

Circle.shout = shout
```

这叫猴子补丁（monkey patching）。它适合测试、调试、临时扩展，不适合作为常规设计。修改第三方类的行为会让代码难以推理。

## 7.11 代码导览

[`classes.py`](classes.py) 分成四部分：

- `show_vector()`：`Vector` 的 `__slots__`、类属性、`__repr__`、`__eq__`、`__add__`、`__len__`、`__iter__`、`__getitem__`、property、classmethod、staticmethod；
- `show_inheritance()`：`Shape` 抽象基类、`Circle`/`Rectangle`、MRO；
- `show_dataclass()`：`Point` 的 `frozen`/`order`；
- `show_name_mangling()`：`Secret` 的名称改编。

运行：

```sh
python3 07-classes/classes.py
```

## 7.12 常见陷阱

| 写法 | 问题 | 建议 |
|------|------|------|
| 在类里写可变类属性 | 所有实例共享 | 在 `__init__` 创建实例属性 |
| `__init__` 返回值不是 `None` | `TypeError` | 初始化方法不要返回值 |
| 定义 `__eq__` 不定义 `__hash__` | 实例不可哈希 | 需要时显式定义，保持契约 |
| `__repr__` 返回非字符串 | `TypeError` | 返回 `str` |
| 用 `is` 比较对象值 | 身份不是值 | 用 `==` |
| 多重继承层级过深 | MRO 难懂 | 优先组合 |
| 子类没有调用 `super().__init__` | 基类状态未初始化 | 需要时显式调用 |
| 用双下划线当私有 | 只是名称改编 | 用单下划线表达内部 |
| `__slots__` 后动态加属性 | `AttributeError` | 列出所有需要属性 |
| `deepcopy` 含锁/文件的对象 | 不可复制 | 自定义 `__deepcopy__` 或避免 |
| 猴子补丁修改第三方类 | 难调试 | 限制在测试/临时场景 |
| `dataclass` 可变默认值 | 共享 | 用 `default_factory` |

## 7.13 语法卡片

| 术语 | 一句话定义 | 本章例子 |
|------|------------|----------|
| 类 | 创建实例的对象 | `class Vector:` |
| 实例 | 类创建出来的对象 | `Vector(3, 4)` |
| 方法 | 定义在类里的函数 | `def magnitude(self):` |
| `self` | 实例方法的第一个参数 | `self.x` |
| 类属性 | 属于类、实例共享的属性 | `count = 0` |
| 实例属性 | 属于单个实例的属性 | `self.x = x` |
| 特殊方法 | 由内置语法调用的方法 | `__len__`、`__eq__` |
| `property` | 计算属性/带校验的属性 | `@property` |
| `classmethod` | 第一个参数是类的方法 | `@classmethod` |
| `staticmethod` | 不接收实例/类的方法 | `@staticmethod` |
| MRO | 方法解析顺序 | `D.__mro__` |
| `super()` | 按 MRO 调用下一个实现 | `super().__init__()` |
| ABC | 抽象基类 | `class Shape(ABC):` |
| dataclass | 自动生成特殊方法的类 | `@dataclass` |
| `__slots__` | 限制实例属性、节省内存 | `__slots__ = ("x",)` |

## 7.14 练习

1. **Vector**：实现 `Vector` 的 `__repr__`、`__eq__`、`__add__`、`__len__`、`__iter__`、`__getitem__`，用 `len()`、`for`、下标验证。
2. **Property**：实现 `Temperature`，用 property 校验摄氏温度不低于绝对零度。
3. **类方法**：给 `Vector` 加 `from_pair`、`origin`，比较 `classmethod` 和 `staticmethod` 的区别。
4. **继承**：定义 `Shape`、`Circle`、`Rectangle`，用 `ABC` 防止直接实例化 `Shape`。
5. **MRO**：定义 `A`、`B(A)`、`C(A)`、`D(B, C)`，打印 MRO，预测 `D().who()` 的结果。
6. **dataclass**：用 `@dataclass(frozen=True, order=True)` 定义 `Point`，比较、排序、尝试修改。
7. **`__slots__`**：给一个类加 `__slots__`，尝试添加未列出的属性，读 `AttributeError`。
8. **名称改编**：定义 `Secret`，从外部访问 `_Secret__value`，说明它不是安全边界。
9. **描述符**：给类加 property，再往实例 `__dict__` 写同名键，验证 property 优先。
10. **破坏实验**：删除 `__eq__` 里的 `isinstance` 检查，用不同类型的对象比较，观察 `AttributeError`；再改成返回 `NotImplemented`。

## 7.15 下一章

**第 8 章 · 模块、包与导入**

类把行为和数据组织成对象，模块把对象组织成可复用的文件。下一章会讲模块、包、`__init__.py`、相对导入、`sys.path`、模块缓存和 `__name__`。

届时，`import` 到底做了什么、为什么有时会循环导入、`python -m` 和直接运行有什么区别，会有完整的答案。
