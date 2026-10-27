# 第 9 章 · 异常与上下文管理器

> **卷一 · 语言**　|　前置知识：第 4–8 章　|　建议用时：55 分钟

> 异常不是“崩溃”，而是另一种控制流：它把错误从发生地点带到能处理它的地方，同时保证清理代码仍然执行。

模块把代码组织成文件，异常把错误组织成控制流。这一章讲 `try`/`except`/`else`/`finally`、异常层次、异常链、自定义异常、异常组，以及 `with` 协议和 `contextlib`。

Python 的哲学是 **EAFP**（Easier to Ask Forgiveness than Permission）：先做，出问题再处理。这与 C 的返回码、C++ 的异常都有相似之处，但 Python 的异常类型更细、上下文管理器更常用。

## 9.1 本章语法地图

| 语法/概念 | 本章出现的位置 |
|-----------|----------------|
| `try` / `except` | 捕获异常 |
| `else` | 没有异常时执行 |
| `finally` | 无论如何都执行 |
| `raise` | 抛出/重新抛出异常 |
| `raise ... from ...` | 异常链 |
| 自定义异常 | `class ValidationError(ValueError):` |
| `ExceptionGroup` | 异常组（3.11） |
| `except*` | 分组捕获（3.11） |
| `with` | 上下文管理器 |
| `__enter__` / `__exit__` | 上下文管理器协议 |
| `contextlib.contextmanager` | 生成器式上下文管理器 |
| `contextlib.suppress` | 忽略指定异常 |
| `assert` | 调试断言 |

## 9.2 异常层次

Python 的异常是一棵类继承树：

```text
BaseException
├── SystemExit
├── KeyboardInterrupt
├── GeneratorExit
└── Exception
    ├── ArithmeticError
    │   ├── ZeroDivisionError
    │   └── OverflowError
    ├── LookupError
    │   ├── IndexError
    │   └── KeyError
    ├── ValueError
    ├── TypeError
    ├── OSError
    ├── RuntimeError
    └── ...
```

关键点：

- 大多数程序错误继承自 `Exception`；
- `SystemExit`、`KeyboardInterrupt`、`GeneratorExit` 直接继承 `BaseException`，不是 `Exception`；
- 不要捕获 `BaseException`，否则可能吞掉 Ctrl+C 和程序退出；
- 捕获 `Exception` 通常是安全的“兜底”，但也要想清楚是否应该吞掉。

```python
try:
    ...
except Exception as error:
    ...
```

### 什么时候捕获

- 你知道如何处理这个错误；
- 你需要添加上下文或转换异常；
- 你需要在清理后重新抛出；
- 你需要在边界处记录日志并继续/退出。

不要为了“让程序不崩”而捕获所有异常。隐藏错误比崩溃更难调试。

## 9.3 `try` / `except` / `else` / `finally`

```python
try:
    value = int(text)
except ValueError:
    print("not an integer")
else:
    print("parsed:", value)
finally:
    print("done")
```

执行顺序：

1. 执行 `try` 块；
2. 如果没有异常，执行 `else`；
3. 如果有异常，按 `except` 顺序匹配；
4. 无论是否异常，最后执行 `finally`。

`else` 只在没有异常时执行；它适合“成功后才做”的逻辑，避免把不想被 `except` 捕获的代码放进 `try`。

`finally` 总会执行，即使 `try` 里有 `return`、`break`、`continue` 或异常。它用于释放资源、关闭文件、恢复状态。

```python
def read_value():
    try:
        return 42
    finally:
        print("cleanup")
```

调用 `read_value()` 会先打印 `cleanup`，再返回 42。

### 多个 `except`

```python
try:
    value = int(text)
except ValueError:
    print("bad value")
except TypeError:
    print("bad type")
```

从上到下匹配，第一个匹配的 `except` 执行，后面的不再检查。

可以用元组捕获多种异常：

```python
except (ValueError, TypeError) as error:
    ...
```

### 裸 `except`

```python
try:
    ...
except:          # 捕获 BaseException
    ...
```

它会捕获 `KeyboardInterrupt`、`SystemExit` 等。除非你在写框架的最外层，否则不要这样写。至少要写 `except Exception:`。

## 9.4 抛出与异常链

```python
raise ValueError("bad input")
```

在 `except` 块里，`raise` 不带参数会重新抛出当前异常：

```python
try:
    ...
except ValueError:
    log()
    raise
```

### `raise ... from ...`

```python
try:
    value = int(text)
except ValueError as error:
    raise ValidationError("number", "not an integer") from error
```

`from` 设置 `__cause__`，表示“这个异常是由另一个异常引起的”。回溯会显示：

```text
ValueError: invalid literal for int() with base 10: 'abc'

The above exception was the direct cause of the following exception:

ValidationError: number: not an integer
```

如果不写 `from`，在 `except` 块里抛出的新异常会自动获得 `__context__`，表示“在处理另一个异常时发生了这个异常”。`from` 更明确，通常更好。

要刻意隐藏上下文：

```python
raise ValidationError(...) from None
```

这会设置 `__suppress_context__`。

### 异常对象

异常对象可以携带数据：

```python
class ValidationError(ValueError):
    def __init__(self, field, message):
        super().__init__(f"{field}: {message}")
        self.field = field
        self.message = message
```

`str(error)` 使用 `args` 里的消息；你也可以重写 `__str__`。异常对象可以被捕获、检查、重新抛出。

## 9.5 自定义异常

自定义异常通常继承 `Exception` 或更具体的异常：

```python
class ValidationError(ValueError):
    ...
```

选择基类：

- 输入格式错误：`ValueError`；
- 类型错误：`TypeError`；
- I/O 错误：`OSError`；
- 自定义领域错误：`Exception` 或专门的基类。

不要继承 `BaseException`，除非你确实在实现一种“不能被普通 `except Exception` 捕获”的控制流（如 `SystemExit`）。

异常的粒度要适中：太细会增加捕获负担，太粗会丢失信息。库通常定义自己的异常基类：

```python
class MyLibraryError(Exception):
    ...

class ConfigError(MyLibraryError):
    ...
```

## 9.6 异常组与 `except*`（3.11）

普通 `try` 一次只能抛出一个异常。异步任务、批量校验等场景可能需要同时报告多个错误。Python 3.11 引入 `ExceptionGroup`：

```python
errors = [ValueError("a"), TypeError("b")]
raise ExceptionGroup("validation failed", errors)
```

捕获：

```python
try:
    validate_all(...)
except* ValueError as group:
    for error in group.exceptions:
        ...
except* TypeError as group:
    ...
```

`except*` 会把异常组拆分成匹配的子组；每个匹配的子组交给对应的 `except*` 块。没有匹配的异常会继续传播。

注意：

- `except*` 不能和普通 `except` 混用在同一个 `try`；
- `except*` 块里不能使用 `return`、`break`、`continue`（3.11 的限制）；
- `ExceptionGroup` 可以嵌套；
- 它适合“批量错误”，不要为了炫技而使用。

## 9.7 `with` 与上下文管理器

`with` 保证资源在离开代码块时被释放：

```python
with open("data.txt", encoding="utf-8") as file:
    text = file.read()
```

等价于：

```python
file = open("data.txt", encoding="utf-8")
try:
    text = file.read()
finally:
    file.close()
```

上下文管理器协议：

```python
class Resource:
    def __enter__(self):
        print("enter")
        return self

    def __exit__(self, exc_type, exc, traceback):
        print("exit")
        return False
```

- `__enter__` 的返回值绑定到 `as` 后面的名字；
- `__exit__` 在离开 `with` 时调用；
- 如果 `with` 块正常结束，`exc_type` 等为 `None`；
- 如果发生异常，`__exit__` 收到异常信息；
- `__exit__` 返回 `True` 会**吞掉**异常，返回 `False`/`None` 会继续传播。

```python
with Resource() as resource:
    ...
```

多个上下文管理器：

```python
with open("in.txt") as source, open("out.txt", "w") as target:
    target.write(source.read())
```

进入顺序从左到右，退出顺序从右到左。

## 9.8 `contextlib`

`contextlib.contextmanager` 用生成器写上下文管理器：

```python
from contextlib import contextmanager

@contextmanager
def section(name):
    print(f"<{name}>")
    try:
        yield
    finally:
        print(f"</{name}>")

with section("chapter"):
    print("inside")
```

`yield` 之前是 `__enter__`，之后是 `__exit__`。如果 `with` 块里发生异常，异常会在 `yield` 处抛回生成器；用 `try`/`finally` 保证清理。

`contextlib.suppress` 忽略指定异常：

```python
from contextlib import suppress

with suppress(FileNotFoundError):
    os.remove("maybe-missing.txt")
```

`contextlib.ExitStack` 可以动态管理多个上下文管理器，适合“运行时才知道要打开几个资源”的场景。

## 9.9 EAFP、LBYL 与 `assert`

两种风格：

```python
# LBYL: Look Before You Leap
if os.path.exists(path):
    with open(path) as file:
        ...

# EAFP: Easier to Ask Forgiveness than Permission
try:
    with open(path) as file:
        ...
except FileNotFoundError:
    ...
```

EAFP 在 Python 里通常更自然，因为文件可能在检查和使用之间被删除；直接尝试并处理异常，避免了竞态。

但 EAFP 不是“随便捕获所有异常”。只捕获你预期且能处理的异常，让其他异常继续传播。

### `assert`

```python
assert value > 0, "value must be positive"
```

`assert` 用于调试和不变量检查。Python 用 `-O` 运行时，`assert` 语句会被移除：

```sh
python3 -O script.py
```

因此不要用 `assert` 做输入校验或安全边界。用户输入用显式 `if` + `raise`。

## 9.10 代码导览

[`exceptions.py`](exceptions.py) 分成五部分：

- `show_try()`：`try`/`except`/`else`/`finally`；
- `show_chaining()`：`raise ... from ...`、`__cause__`、`__context__`；
- `show_group()`：`ExceptionGroup` 与 `except*`；
- `show_context_manager()`：`with`、`__enter__`/`__exit__`、`contextmanager`、`suppress`；
- `show_assert()`：`assert` 的调试用途。

运行：

```sh
python3 09-exceptions/exceptions.py
```

## 9.11 常见陷阱

| 写法 | 问题 | 建议 |
|------|------|------|
| `except:` | 捕获 `BaseException` | 至少 `except Exception:` |
| 捕获后什么都不做 | 隐藏错误 | 记录/转换/重新抛出 |
| 用异常做常规控制流 | 慢、难读 | 用条件/循环 |
| `raise X` 丢失原始异常 | 调试信息丢失 | 用 `raise X from error` |
| `finally` 里 `return` | 吞掉异常/覆盖返回值 | 避免在 `finally` 返回 |
| `assert` 做输入校验 | `-O` 会移除 | 用显式 `raise` |
| `except*` 里 `return` | 语法限制 | 用普通函数/标志 |
| `__exit__` 返回真值 | 意外吞异常 | 明确返回 `False` |
| 在 `__init__` 里抛异常但资源未清理 | 半初始化对象 | 用 `with`/RAII 思路 |
| 捕获 `Exception` 后继续 | 状态可能已损坏 | 只处理能恢复的错误 |

## 9.12 语法卡片

| 术语 | 一句话定义 | 本章例子 |
|------|------------|----------|
| 异常 | 表示错误/异常情况的对象 | `ValueError("bad")` |
| `try` | 受保护的代码块 | `try: ...` |
| `except` | 捕获匹配的异常 | `except ValueError:` |
| `else` | 没有异常时执行 | `else: ...` |
| `finally` | 无论如何都执行 | `finally: ...` |
| `raise` | 抛出异常 | `raise ValueError(...)` |
| 异常链 | 用 `from` 关联因果 | `raise X from error` |
| `ExceptionGroup` | 同时携带多个异常 | `ExceptionGroup(...)` |
| `except*` | 分组捕获异常组 | `except* ValueError:` |
| 上下文管理器 | 用 `with` 管理资源 | `with open(...):` |
| `__enter__` / `__exit__` | 上下文管理器协议 | `with Resource():` |
| `contextmanager` | 用生成器写上下文管理器 | `@contextmanager` |

## 9.13 练习

1. **基本捕获**：写一个 `int()` 转换函数，分别捕获 `ValueError`，用 `else` 打印成功值，用 `finally` 打印结束。
2. **异常链**：在 `except ValueError` 里抛出 `ValidationError`，分别用 `from error` 和 `from None`，观察回溯。
3. **自定义异常**：定义 `ConfigError` 和 `ValidationError`，让它们继承不同的基类，捕获并打印字段。
4. **异常组**：写一个批量校验函数，收集所有错误后用 `ExceptionGroup` 抛出，用 `except*` 分组处理。
5. **上下文管理器**：手写一个 `Timer`/`Resource` 类，实现 `__enter__` 和 `__exit__`，打印进入/退出和异常信息。
6. **`contextmanager`**：用生成器写一个 `temp_directory` 或 `section` 上下文管理器。
7. **`suppress`**：用 `contextlib.suppress` 忽略 `FileNotFoundError`，删除一个不存在的文件。
8. **`assert`**：分别用 `python3` 和 `python3 -O` 运行带 `assert` 的脚本，观察差异。
9. **破坏实验**：在 `finally` 里写 `return`，观察它如何覆盖 `try` 里的返回值/异常。

## 9.14 下一章

**第 10 章 · 类型注解与协议**

异常处理的是运行时错误，类型注解处理的是“写代码时的意图”。下一章会讲 `list[int]`、`int | None`、`Protocol`、`TypedDict`、`Literal`、泛型和 PEP 695。

届时，为什么注解不会在运行时强制检查、`Protocol` 如何实现结构化子类型，会有完整的答案。
