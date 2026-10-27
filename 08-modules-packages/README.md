# 第 8 章 · 模块、包与导入

> **卷一 · 语言**　|　前置知识：第 1–7 章　|　建议用时：50 分钟

> `import` 不是“把文件内容粘进来”。它是在运行时找到模块、执行一次、缓存起来，然后把名字绑定到当前命名空间。

类把行为和数据组织成对象，模块把对象组织成可复用的文件。这一章讲模块、包、`__init__.py`、相对导入、`sys.path`、模块缓存、`__all__` 和 `__name__`。

Python 没有 C/C++ 的“编译-链接”阶段，但导入系统有自己的规则：模块只执行一次，模块对象被缓存，包用目录组织，相对导入依赖包上下文。理解这些规则，才能解释“为什么我的 import 找不到”“为什么循环导入会失败”。

## 8.1 本章语法地图

| 语法/概念 | 本章出现的位置 |
|-----------|----------------|
| 模块 | 一个 `.py` 文件 |
| `import` | `import shapes` |
| `from ... import` | `from shapes import Circle` |
| 别名 | `import numpy as np` |
| 包 | 含 `__init__.py` 的目录 |
| 相对导入 | `from .circle import Circle` |
| `__name__` | 模块名或 `"__main__"` |
| `__file__` | 模块文件路径 |
| `__all__` | 公共导出名字 |
| `sys.path` | 模块搜索路径 |
| `sys.modules` | 模块缓存 |
| `python -m` | 以模块方式运行 |
| `__main__.py` | 包的入口模块 |

## 8.2 模块与脚本

每个 `.py` 文件都是一个**模块**。模块有自己的命名空间，模块里的顶层名字不会自动进入导入者的命名空间。

```python
# greeting.py
message = "hello"

def greet(name):
    return f"{message}, {name}"
```

```python
# main.py
import greeting

print(greeting.message)       # hello
print(greeting.greet("Ada"))  # hello, Ada
```

`import greeting` 做了几件事：

1. 在 `sys.path` 中查找 `greeting.py`；
2. 如果找到，创建模块对象；
3. 执行模块顶层代码；
4. 把模块对象缓存到 `sys.modules["greeting"]`；
5. 在当前命名空间绑定名字 `greeting`。

模块顶层代码只执行一次；再次 `import` 会直接复用缓存。

### `__name__`

模块的 `__name__` 由解释器设置：

- 直接运行脚本时，`__name__ == "__main__"`；
- 被导入时，`__name__` 是模块名。

```python
if __name__ == "__main__":
    main()
```

这个条件让文件既能当脚本，又能当模块。它不是语言强制的入口，而是约定。

### `__file__`

`__file__` 是模块的文件路径（可能不存在于某些动态创建的模块）：

```python
print(__file__)
```

可以用它定位与模块同目录的资源，但更现代的方式是 `importlib.resources`。

## 8.3 导入的几种写法

```python
import shapes                     # 绑定模块名
import shapes.circle              # 绑定顶层包名 shapes
import shapes.circle as circle    # 绑定 circle
from shapes import Circle         # 绑定 Circle
from shapes.circle import Circle  # 绑定 Circle
from shapes import *              # 导入 __all__ 或所有非下划线名字
```

区别：

| 写法 | 绑定到当前命名空间的名字 |
|------|--------------------------|
| `import shapes` | `shapes` |
| `import shapes.circle` | `shapes`（但会加载子模块） |
| `import shapes.circle as circle` | `circle` |
| `from shapes import Circle` | `Circle` |
| `from shapes import *` | `__all__` 中的名字（或所有非下划线名字） |

`import shapes.circle` 不会把 `circle` 直接绑定到当前命名空间；你需要 `shapes.circle` 或 `import ... as ...`。

### 别名

```python
import numpy as np
from collections import Counter as Count
```

别名可以避免命名冲突、缩短长名字。不要用无意义的别名。

### `from ... import *`

不推荐在生产代码中使用：

- 不清楚导入了哪些名字；
- 可能覆盖已有名字；
- 静态工具难以分析。

如果库确实需要支持 `*`，用 `__all__` 明确列出公共名字：

```python
__all__ = ["Circle", "Rectangle"]
```

## 8.4 导入系统与 `sys.path`

导入时，Python 按 `sys.path` 的顺序查找模块：

1. 脚本所在目录（直接运行脚本时）；或当前目录（`-m`、交互式）；
2. `PYTHONPATH` 环境变量中的目录；
3. 标准库目录；
4. 安装的第三方包目录（`site-packages`）。

```python
import sys
print(sys.path)
```

你可以修改 `sys.path`，但通常不要：

```python
sys.path.insert(0, "/some/path")   # 临时可以，生产环境谨慎
```

更好的方式：

- 把项目安装成包（`pip install -e .`）；
- 用 `PYTHONPATH`（开发时）；
- 用 `python -m` 从项目根目录运行；
- 用 `importlib` 显式加载。

### 当前目录与脚本目录

直接运行：

```sh
python3 08-modules-packages/run_imports.py
```

`sys.path[0]` 是 `08-modules-packages/`，所以脚本旁边的 `shapes/` 可以被导入。

用 `-m`：

```sh
python3 -m somepackage.module
```

`sys.path[0]` 是当前工作目录，`somepackage` 必须在当前目录或搜索路径中。

### 不要遮蔽标准库

如果你在自己的目录里创建 `random.py`，然后 `import random`，Python 可能导入你的文件，而不是标准库。这类 bug 很难查。避免用标准库模块名命名自己的文件。

## 8.5 包与 `__init__.py`

包是含 `__init__.py` 的目录：

```text
shapes/
├── __init__.py
├── base.py
├── circle.py
└── rectangle.py
```

`__init__.py` 在包被导入时执行，可以：

- 初始化包的状态；
- 从子模块导入公共名字；
- 定义 `__all__`；
- 选择合适的公开 API。

```python
# shapes/__init__.py
from .base import Shape
from .circle import Circle
from .rectangle import Rectangle

__all__ = ["Shape", "Circle", "Rectangle"]
```

这样：

```python
from shapes import Circle
```

就能直接拿到 `Circle`，而不需要知道它在 `shapes.circle` 里。

### 相对导入

包内模块用相对导入：

```python
# shapes/circle.py
from .base import Shape
```

- `.` 表示当前包；
- `..` 表示上一级包；
- 相对导入只能在包内使用；直接运行 `python shapes/circle.py` 会失败，因为此时模块没有包上下文。

正确运行方式：

```sh
python3 -m shapes.circle   # 从 shapes 的父目录运行
```

或者通过包的入口模块运行。

### 命名空间包

PEP 420 允许没有 `__init__.py` 的目录作为命名空间包，把多个目录合并到同一个包名下。它适合大型项目/插件系统，但也让“包从哪里来”更隐蔽。日常项目用常规包（有 `__init__.py`）更直观。

### `__main__.py`

如果包目录里有 `__main__.py`，可以：

```sh
python3 -m shapes
```

执行 `shapes/__main__.py`。它适合给包提供命令行入口。

## 8.6 模块缓存与循环导入

### 模块缓存

```python
import shapes
import shapes as again

shapes is again   # True
```

模块对象缓存在 `sys.modules`。再次导入不会重新执行模块顶层代码（除非用 `importlib.reload`）。

```python
import sys
print("shapes" in sys.modules)
```

`importlib.reload(module)` 会重新执行模块代码，但不会自动更新已经 `from ... import` 到其他命名空间的名字。热重载很复杂，生产代码少用。

### 循环导入

```python
# a.py
import b

def f():
    return b.value

# b.py
import a

value = 42
```

如果 `a` 在 `b` 完成定义前导入 `b`，可能拿到部分初始化的模块，导致 `AttributeError`。常见修复：

- 把导入移到函数内部（延迟导入）；
- 重构依赖，抽出公共模块；
- 用依赖注入；
- 避免模块顶层执行有副作用的代码。

循环导入不是“语法错误”，而是设计信号：两个模块可能耦合过紧。

### 导入时的副作用

模块顶层代码在导入时执行。不要在导入时做耗时操作、读文件、连数据库、打印日志；这些副作用会让测试和工具难以使用。

把副作用放进 `main()` 或显式的初始化函数。

## 8.7 `__all__` 与公共 API

`__all__` 是一个字符串列表，定义 `from module import *` 时导出哪些名字：

```python
__all__ = ["Circle", "Rectangle"]
```

它不影响：

- `import module`；
- `from module import SpecificName`；
- `module.__dict__`。

它只是公共 API 的约定，也是文档工具和 IDE 的提示。

以下划线开头的名字是“内部”约定：

```python
def _helper():
    ...
```

Python 不会强制阻止外部访问，但读者应该把它当作实现细节。

## 8.8 `python -m` 与脚本

```sh
python3 script.py          # 运行脚本，sys.path[0] 是脚本目录
python3 -m package.module  # 以模块方式运行，sys.path[0] 是当前目录
```

`-m` 的好处：

- 包的相对导入有正确上下文；
- 可以用包的 `__main__.py`；
- 不依赖脚本路径。

对于包内的命令行工具，推荐：

```text
mypackage/
├── __init__.py
├── __main__.py
└── cli.py
```

```sh
python3 -m mypackage
```

## 8.9 代码导览

本章是一个多文件程序：

- [`shapes/__init__.py`](shapes/__init__.py)：包入口，导出 `Shape`、`Circle`、`Rectangle`；
- [`shapes/base.py`](shapes/base.py)：抽象基类；
- [`shapes/circle.py`](shapes/circle.py)：圆；
- [`shapes/rectangle.py`](shapes/rectangle.py)：矩形；
- [`run_imports.py`](run_imports.py)：演示 `import`、`from`、模块缓存、`__all__`、`sys.path`。

运行：

```sh
python3 08-modules-packages/run_imports.py
```

输出里重点关注：

- `__name__` 是 `"__main__"`；
- `sys.path[0]` 是脚本目录；
- `shapes.__file__` 指向包的 `__init__.py`；
- 两次 `import shapes` 得到同一个模块对象；
- `shapes.__all__` 列出公共名字。

## 8.10 常见陷阱

| 写法 | 问题 | 建议 |
|------|------|------|
| 文件命名为 `random.py` | 遮蔽标准库 | 避免与标准库同名 |
| 直接运行包内模块 | 相对导入失败 | 用 `python -m` |
| 在 `__init__.py` 里做重活 | 导入变慢/有副作用 | 只做轻量初始化 |
| 循环导入 | 模块部分初始化 | 重构/延迟导入 |
| 用 `from x import *` | 名字来源不清 | 显式导入 |
| 修改 `sys.path` 到处加目录 | 环境依赖、难复现 | 安装包/用 `-m` |
| 依赖导入顺序 | 难以推理 | 让模块无副作用 |
| `importlib.reload` 后旧引用未更新 | 混用新旧对象 | 避免热重载 |
| 忘记 `__init__.py` | 旧版本下不是包 | 常规包加上它 |
| 相对导入超出顶层包 | `ImportError` | 检查包结构 |

## 8.11 语法卡片

| 术语 | 一句话定义 | 本章例子 |
|------|------------|----------|
| 模块 | 一个 `.py` 文件对应的命名空间 | `shapes` |
| 包 | 含 `__init__.py` 的目录 | `shapes/` |
| `import` | 加载模块并绑定模块名 | `import shapes` |
| `from ... import` | 从模块绑定具体名字 | `from shapes import Circle` |
| 相对导入 | 包内用 `.` 定位模块 | `from .base import Shape` |
| `__name__` | 模块名或 `"__main__"` | `if __name__ == "__main__":` |
| `__all__` | `import *` 的公共名字列表 | `__all__ = [...]` |
| `sys.path` | 模块搜索路径 | `import sys` |
| `sys.modules` | 已加载模块缓存 | `"shapes" in sys.modules` |
| `python -m` | 以模块方式运行 | `python3 -m mypackage` |

## 8.12 练习

1. **模块**：创建 `greeting.py` 和 `main.py`，在 `main.py` 中 `import greeting`，调用函数并打印 `greeting.__name__`。
2. **入口**：给 `greeting.py` 加 `if __name__ == "__main__":`，分别直接运行和导入，观察输出。
3. **包**：创建 `mathx/` 包，含 `__init__.py`、`add.py`、`sub.py`，从包顶层导出函数。
4. **相对导入**：在包内用 `from .add import add`，分别直接运行模块和用 `python -m` 运行，比较结果。
5. **`__all__`**：给包定义 `__all__`，用 `from package import *`，观察哪些名字被导入。
6. **缓存**：在同一进程中两次 `import` 同一个模块，打印模块对象身份，验证缓存。
7. **循环导入**：故意让 `a.py` 和 `b.py` 互相导入，观察错误；再用延迟导入修复。
8. **`sys.path`**：打印 `sys.path`，指出脚本目录、标准库目录和 site-packages。
9. **破坏实验**：把包内相对导入改成绝对导入，在不同的运行方式下观察差异。

## 8.13 下一章

**第 9 章 · 异常与上下文管理器**

模块把代码组织成文件，异常把错误组织成控制流。下一章会讲 `try`/`except`/`else`/`finally`、异常链、异常组、`with` 协议和 `contextlib`。

届时，`import` 失败、文件打开失败、JSON 解析失败，为什么会以不同异常类型出现，会有完整的答案。
