# 附录 A · Python 3.10–3.14 与异步速览

> 主线以 Python 3.12 为基线。本附录补齐 3.10–3.14 的重要语言/实现变化，并给出 `async`/`await`/`asyncio` 的速览。附录中的代码是示意，不进入 `make` 构建；较新的特性需要对应版本的 Python。

Python 的版本节奏很快。主线不可能把每个版本的新语法都塞进 12 章，但读现代代码时又会遇到它们。本附录只给“这是什么、解决什么问题、代码长什么样”，不展开实现细节。

## A.1 Python 3.10

### 结构化模式匹配

```python
match command:
    case ["go", direction]:
        move(direction)
    case ["quit"]:
        quit()
    case _:
        unknown(command)
```

第 3 章已经讲过。它是 3.10 最重要的语法新增，不是 `switch` 的替代品，而是解构 + 分支。

### `X | Y` 联合类型

```python
def find(key: str) -> int | None:
    ...
```

PEP 604 让类型注解可以用 `|` 表示联合，不再必须写 `Union[int, str]`。运行时也支持 `int | str` 得到一个 `types.UnionType` 对象。

### 括号化的上下文管理器

```python
with (
    open("input.txt", encoding="utf-8") as source,
    open("output.txt", "w", encoding="utf-8") as target,
):
    target.write(source.read())
```

多行 `with` 可以用括号组织，不需要反斜杠。

### 更精确的错误位置

3.10 起，很多 `SyntaxError` 会给出更精确的列号和插入符，读诊断比以前容易。

### 其他

- `dataclass(slots=True)`；
- `zip(..., strict=True)`；
- `int.bit_count()`；
- `typing.ParamSpec`、`TypeAlias` 等改进。

## A.2 Python 3.11

### 异常组与 `except*`

```python
try:
    validate_all(values)
except* ValueError as group:
    for error in group.exceptions:
        print(error)
```

`ExceptionGroup` 可以同时携带多个异常；`except*` 按类型拆分组。适合批量校验、异步任务汇总错误。第 9 章有示例。

### `tomllib`

```python
import tomllib

with open("config.toml", "rb") as file:
    config = tomllib.load(file)
```

标准库终于有了 TOML 解析器。它只读，不写。

### `typing.Self`

```python
from typing import Self

class Box:
    def clone(self) -> Self:
        return type(self)()
```

`Self` 表示“当前类”，比写死类名更适合继承。

### `typing.LiteralString`

```python
from typing import LiteralString

def execute(query: LiteralString) -> None:
    ...
```

它要求传入的字符串是字面量或由字面量拼接而来，用于降低 SQL 注入等风险。它是静态检查工具，不是运行时消毒器。

### `asyncio.TaskGroup` 与 `asyncio.timeout`

```python
async with asyncio.TaskGroup() as group:
    first = group.create_task(fetch(url1))
    second = group.create_task(fetch(url2))
```

`TaskGroup` 提供结构化并发：组内任务的生命期受 `async with` 管理，异常会汇总成 `ExceptionGroup`。

```python
async with asyncio.timeout(5):
    await slow_operation()
```

超时会抛 `TimeoutError`，比手动 `wait_for` 更容易组合。

### 其他

- `Exception.add_note()`；
- `enum.StrEnum`；
- `datetime.UTC`；
- 更精确的 traceback；
- `typing.Never`、`assert_never`。

## A.3 Python 3.12

### PEP 695：类型参数与 `type` 别名

```python
type Point = tuple[float, float]

def first[T](items: list[T]) -> T:
    return items[0]

class Box[T]:
    def __init__(self, item: T) -> None:
        self.item = item
```

不再需要显式 `TypeVar`/`Generic`。类型参数有清晰的作用域，`type` 别名是惰性求值的。

### `@override`

```python
from typing import override

class Child(Base):
    @override
    def method(self) -> None:
        ...
```

静态检查器验证基类确实有同名方法。它不会改变运行时行为。

### f-string 语法改进

PEP 701 让 f-string 的解析更统一：

```python
value = 42
print(f"{value + 1}")
print(f"{'nested' if value else 'other'}")
```

3.12 之前，f-string 里的引号嵌套和反斜杠限制更多；3.12 放宽了这些限制。

### `itertools.batched`

```python
from itertools import batched

list(batched([1, 2, 3, 4, 5], 2))
# [(1, 2), (3, 4), (5,)]
```

把可迭代对象按固定大小分批。

### `sys.monitoring`

3.12 引入更底层的监控/分析 API，供调试器、分析器和覆盖率工具使用。普通业务代码很少直接用它。

### 其他

- `typing.override`；
- `pathlib.Path.walk`（3.12）；
- `os.path.isjunction`；
- 更快的 `asyncio`；
- PEP 684（每解释器 GIL）实现基础。

## A.4 Python 3.13

### 实验性的 free-threaded CPython

3.13 提供一个可选构建，禁用 GIL（PEP 703），让多线程可以真正并行执行 Python 字节码。它仍是实验性的：

- 需要单独构建/安装；
- 第三方扩展可能不兼容；
- 单线程性能可能下降；
- 线程安全责任增加。

3.14 起 free-threading 进入“官方支持”的阶段，但仍不是默认构建。

### 实验性的 JIT

3.13 包含一个实验性的 JIT 编译器（PEP 744），默认不启用。它的目标是长期性能改进，不是让所有代码立刻变快。

### 新的交互式解释器

3.13 的 REPL 支持多行编辑、历史、颜色和更好的补全。日常体验提升明显。

### `typing.NoDefault`

用于区分“没有默认值”和“默认值是 None”：

```python
from typing import NoDefault

def f(x: int | NoDefault = NoDefault) -> None:
    ...
```

### `copy.replace`

```python
from copy import replace

new_point = replace(point, x=10)
```

对 dataclass、namedtuple 等支持 `__replace__` 的对象创建修改后的副本。

### 其他

- `dbm.sqlite3`；
- `asyncio` 的改进；
- `queue` 的 `ShutDown`；
- `random` 命令行工具；
- 更好的错误消息。

## A.5 Python 3.14

### 延迟求值的注解

PEP 649/749 让注解默认惰性求值：

```python
def f(x: LaterDefined) -> None:
    ...
```

注解不再在函数定义时立即求值，前向引用和循环依赖更容易处理。`annotationlib` 提供读取注解的工具。

这改变了 `__annotations__` 的语义；依赖运行时注解的框架需要适配。

### 模板字符串（t-string）

PEP 750 引入 `t"..."`：

```python
name = "Ada"
template = t"Hello, {name}!"
```

它返回一个 `Template` 对象，而不是普通字符串。模板字符串把“字面量部分”和“插值部分”分开保存，适合安全地构造 SQL、HTML、日志等。

不要把它当成 f-string 的替代品；它需要显式处理（例如转义、拼接）。

### 多解释器

PEP 734 在标准库中提供多解释器支持：

```python
from concurrent import interpreters
```

每个解释器有独立的全局状态，可以在同一进程内提供更强的隔离。它和线程、进程不是同一层面的并发工具。

### free-threading 正式支持

3.14 起，free-threaded 构建不再是实验性的，但仍不是默认。是否启用取决于部署环境和扩展兼容性。

### `except` 多异常不需要括号

```python
try:
    ...
except ValueError, TypeError:
    ...
```

PEP 758 允许省略括号。旧代码仍然可以写 `except (ValueError, TypeError):`。

### 其他

- `compression.zstd`；
- `annotationlib`；
- `concurrent.interpreters`；
- `pathlib` 的改进；
- 更好的错误消息和 REPL。

## A.6 `async` / `await` 与 `asyncio`

### 协程

```python
async def fetch(url: str) -> str:
    await asyncio.sleep(0.1)
    return f"data from {url}"
```

- `async def` 定义协程函数；
- 调用它不会立刻执行，而是返回协程对象；
- `await` 等待一个 awaitable，挂起当前协程，把控制权交回事件循环；
- 只能在 `async def` 里使用 `await`。

```python
import asyncio

async def main() -> None:
    result = await fetch("https://example.com")
    print(result)

asyncio.run(main())
```

`asyncio.run` 创建事件循环、运行协程、关闭循环。它适合程序入口；不要在已经运行的事件循环里调用它。

### 并发执行

```python
async def main() -> None:
    async with asyncio.TaskGroup() as group:
        first = group.create_task(fetch("a"))
        second = group.create_task(fetch("b"))

    print(first.result(), second.result())
```

`TaskGroup` 让多个协程并发运行，并统一处理异常。`asyncio.gather` 也能并发，但结构化程度较低。

### 异步生成器与异步上下文管理器

```python
async def lines(path: str):
    with open(path, encoding="utf-8") as file:
        for line in file:
            await asyncio.sleep(0)
            yield line

async for line in lines("data.txt"):
    print(line)
```

这个例子为了简短使用了同步文件读取；生产代码里应使用线程/异步文件库，避免阻塞事件循环。

```python
class Resource:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

async with Resource() as resource:
    ...
```

异步版本使用 `async for`、`async with`、`__aiter__`/`__anext__`、`__aenter__`/`__aexit__`。

### 取消

```python
task = asyncio.create_task(fetch("slow"))
task.cancel()
```

取消会在协程的下一个 `await` 处抛 `asyncio.CancelledError`。它通常应该继续传播，不要用裸 `except` 吞掉。

### 不要阻塞事件循环

```python
# 错误：阻塞整个事件循环
time.sleep(5)

# 正确：让出控制权
await asyncio.sleep(5)
```

CPU 密集型任务用 `asyncio.to_thread` / 进程池，而不是在协程里做长时间计算。

### 并发不等于并行

- `asyncio` 适合 I/O 密集型任务；
- 线程适合阻塞 I/O，但受 GIL 影响；
- 进程适合 CPU 密集型任务；
- free-threaded 构建改变了 GIL 的限制，但不改变并行编程的复杂性。

## A.7 从 3.12 往哪走

如果你已经掌握本教材的 3.12 内容，下一步可以按这个顺序扩展：

1. **标准库**：`pathlib`、`json`、`csv`、`sqlite3`、`logging`、`argparse`、`unittest`；
2. **类型检查**：mypy/pyright、stub 文件、`py.typed`；
3. **异步**：`asyncio`、`TaskGroup`、超时、取消、异步上下文管理器；
4. **工程**：`pyproject.toml`、pytest、ruff、black、CI；
5. **性能**：`timeit`、`cProfile`、`tracemalloc`、`sys.monitoring`；
6. **底层**：CPython 字节码、GIL、free-threading、C 扩展；
7. **领域**：Web、数据、科学计算、自动化、编译器。

Python 的语法不多，但对象模型和标准库很深。把第 0–11 章的名字绑定、可变性、闭包、类/MRO、导入、异常和类型注解握稳，后面的框架都只是这些规则的不同组合。

> 语言保证行为，实现决定速度；先分清两者，再谈优化。
