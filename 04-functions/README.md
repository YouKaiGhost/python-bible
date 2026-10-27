# 第 4 章 · 函数、作用域与闭包

> **卷一 · 语言**　|　前置知识：第 2–3 章　|　建议用时：55 分钟

> 函数不只是“把代码包起来”。它还是一个对象，带着参数规则、作用域、默认值和可能的闭包环境。

控制流把语句组织成路径，函数把路径组织成可复用的单元。这一章讲 `def`、参数传递、默认值、`*args`/`**kwargs`、LEGB 作用域、闭包、递归、lambda 和装饰器。

Python 的函数有几个容易踩坑的地方：默认参数在定义时求值一次、可变默认参数会被共享、闭包捕获变量而不是值、函数内赋值会创建局部名字。理解这些规则，才能读懂装饰器和类方法。

## 4.1 本章语法地图

| 语法 | 本章出现的位置 |
|------|----------------|
| 函数定义 | `def greet(name, greeting="Hello"):` |
| 返回 | `return ...` |
| 文档字符串 | `"""..."""` |
| 位置参数 | `greet("Ada")` |
| 关键字参数 | `greet(name="Ada")` |
| 仅位置参数 | `def f(x, /, y):` |
| 仅关键字参数 | `def f(x, *, y):` |
| 可变位置参数 | `def f(*args):` |
| 可变关键字参数 | `def f(**kwargs):` |
| 调用解包 | `f(*args, **kwargs)` |
| 作用域 | LEGB |
| `global` / `nonlocal` | 修改外层名字 |
| 闭包 | 内部函数捕获外层变量 |
| lambda | `lambda x: x * 2` |
| 装饰器 | `@decorator` |
| 缓存 | `functools.lru_cache` |

## 4.2 定义与返回

```python
def greet(name: str, greeting: str = "Hello") -> str:
    """返回一句问候。"""
    return f"{greeting}, {name}!"
```

拆开看：

- `def`：函数定义关键字；
- `greet`：函数名，绑定到一个函数对象；
- `(name: str, greeting: str = "Hello")`：参数列表，带类型注解和默认值；
- `-> str`：返回类型注解，不强制检查；
- `:`：函数头结束；
- 缩进块：函数体；
- `"""..."""`：文档字符串，保存到 `greet.__doc__`；
- `return`：返回值。

没有 `return` 的函数返回 `None`：

```python
def log(message: str) -> None:
    print(message)

result = log("hello")   # 先打印，result 是 None
```

`return` 可以不带表达式，等价于 `return None`。函数可以有多条 `return`，执行到第一条就结束。

### 文档字符串

```python
def add(left: int, right: int) -> int:
    """返回两个整数之和。"""
    return left + right

print(add.__doc__)
```

文档字符串是给 `help()`、IDE 和文档工具看的。它不是注释，而是函数对象的一个属性。

## 4.3 参数的种类

Python 的参数比大多数语言多，因为要同时支持位置、关键字、可变参数和仅关键字参数。

### 位置参数与关键字参数

```python
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"

greet("Ada")                     # 位置参数
greet(name="Ada")                # 关键字参数
greet("Ada", greeting="Hi")      # 混合
```

规则：

- 位置参数按顺序匹配；
- 关键字参数按名字匹配；
- 位置参数必须出现在关键字参数之前；
- 同一个参数不能既用位置又用关键字重复传入。

### 默认值

```python
def power(base, exponent=2):
    return base ** exponent

power(3)      # 9
power(3, 4)   # 81
```

默认值在**函数定义时**求值一次，而不是每次调用时求值。这直接导致可变默认参数陷阱（下一节）。

默认值可以是任意表达式，但通常应该是不可变对象或 `None`。

### 仅位置参数 `/`

Python 3.8 起，`/` 之前的参数只能按位置传：

```python
def positional_only(x, /, y):
    return x + y

positional_only(1, 2)       # 3
positional_only(x=1, y=2)   # TypeError
```

仅位置参数适合“参数名不重要、不想暴露给调用者”的底层函数。标准库和一些 C 扩展常用。

### 仅关键字参数 `*`

`*` 之后的参数只能按关键字传：

```python
def make_point(x, y, *, scale=1):
    return x * scale, y * scale

make_point(2, 3, scale=10)  # 可以
make_point(2, 3, 10)        # TypeError
```

仅关键字参数让调用点更清楚，避免“第三个布尔参数是什么意思”的问题。

### `*args` 与 `**kwargs`

```python
def collect(*args, **kwargs):
    return args, kwargs

collect(1, 2, 3, name="Ada", role="engineer")
# ((1, 2, 3), {'name': 'Ada', 'role': 'engineer'})
```

- `*args` 收集多余的位置参数，得到**元组**；
- `**kwargs` 收集多余的关键字参数，得到**字典**。

名字 `args`/`kwargs` 是约定，不是关键字；`*values`、`**options` 也合法。

### 调用解包

```python
def f(a, b, c):
    return a + b + c

args = [1, 2, 3]
f(*args)          # 6

kwargs = {"a": 1, "b": 2, "c": 3}
f(**kwargs)       # 6
```

`*` 把序列展开成位置参数，`**` 把字典展开成关键字参数。

### 参数顺序

一个完整的参数列表顺序是：

```text
仅位置参数 / 位置或关键字参数 *args 仅关键字参数 **kwargs
```

例如：

```python
def f(a, b, /, c, d=4, *args, e, f=6, **kwargs):
    ...
```

不要为了“完整”而写这么复杂的签名。参数越多，调用点越难读。

## 4.4 可变默认参数陷阱

这是 Python 最经典的陷阱之一：

```python
def append_bad(value, bucket=[]):
    bucket.append(value)
    return bucket

print(append_bad(1))   # [1]
print(append_bad(2))   # [1, 2]
```

默认值 `[]` 只在函数定义时创建一次，所有调用共享同一个列表。第二次调用看到的是第一次修改后的结果。

正确写法：

```python
def append_good(value, bucket=None):
    if bucket is None:
        bucket = []
    bucket.append(value)
    return bucket
```

用 `None` 作为“没有提供”的哨兵，在函数内部创建新容器。类似的陷阱也适用于 `{}`、`set()` 和自定义可变对象。

如果默认值本身就是不可变对象（数字、字符串、元组），共享没有问题；问题只出在可变对象。

## 4.5 作用域：LEGB

Python 查找名字的顺序是 **LEGB**：

1. **L**ocal：当前函数内部；
2. **E**nclosing：外层函数（闭包）；
3. **G**lobal：模块级；
4. **B**uilt-in：内置命名空间。

```python
value = "global"

def outer():
    value = "outer"

    def inner():
        print(value)   # 找到 outer 的 value

    inner()

outer()
```

### 函数内赋值创建局部名字

```python
value = 10

def f():
    print(value)   # UnboundLocalError
    value = 20
```

只要函数体内有对 `value` 的赋值，Python 就把 `value` 当作局部名字；在赋值前读取会抛 `UnboundLocalError`。这不是“先读全局再赋值”。

### `global` 与 `nonlocal`

```python
counter = 0

def bump():
    global counter
    counter += 1
```

`global` 声明名字来自模块级作用域。

```python
def make_counter():
    count = 0

    def next_value():
        nonlocal count
        count += 1
        return count

    return next_value
```

`nonlocal` 声明名字来自外层函数作用域。它不能指向模块级名字；模块级用 `global`。

### 不要滥用 `global`

`global` 让函数依赖并修改模块状态，降低可测试性。优先通过参数和返回值传递状态；确实需要共享状态时，考虑类或显式的状态对象。

## 4.6 闭包

闭包是“函数 + 它捕获的外层变量”：

```python
def make_multiplier(factor):
    def multiply(value):
        return value * factor
    return multiply

double = make_multiplier(2)
triple = make_multiplier(3)
print(double(5), triple(5))   # 10 15
```

`multiply` 捕获了 `factor`。即使 `make_multiplier` 已经返回，`factor` 仍然被闭包保留。

### 捕获的是变量，不是值

```python
functions = []
for index in range(3):
    functions.append(lambda: index)

print([function() for function in functions])   # [2, 2, 2]
```

三个 lambda 捕获的是同一个变量 `index`，循环结束后 `index` 是 2。这就是**延迟绑定**。

修复方式：

```python
functions = [lambda index=index: index for index in range(3)]
print([function() for function in functions])   # [0, 1, 2]
```

默认参数在 lambda 创建时求值，把当前值固定下来。

也可以用 `functools.partial` 或工厂函数：

```python
from functools import partial

def identity(value):
    return value

functions = [partial(identity, index) for index in range(3)]
```

### 闭包与 `nonlocal`

闭包可以读取外层变量；要修改，需要 `nonlocal`：

```python
def make_counter(start=0):
    count = start

    def next_value():
        nonlocal count
        count += 1
        return count

    return next_value
```

没有 `nonlocal` 时，`count += 1` 会被当作局部赋值，抛 `UnboundLocalError`。

## 4.7 函数是第一类对象

函数可以赋值给变量、作为参数、作为返回值、放进容器：

```python
def square(value):
    return value * value

operation = square
print(operation(7))          # 49
print(sorted(words, key=len))
```

`key` 接收一个函数，`sorted` 对每个元素调用它，按返回值排序。

### lambda

lambda 是匿名函数表达式：

```python
square = lambda value: value * value
```

它只能包含**一个表达式**，不能包含语句，也不能写 `return`。适合很短的回调：

```python
sorted(words, key=lambda word: word[-1])
```

复杂逻辑用 `def`，不要为了“短”而牺牲可读性。

### `map` / `filter` 与推导式

```python
list(map(str.upper, words))
list(filter(lambda word: len(word) > 3, words))
```

现代 Python 通常更推荐列表推导式：

```python
[word.upper() for word in words]
[word for word in words if len(word) > 3]
```

推导式更直接，也更容易读。`map`/`filter` 在函数已经存在时仍然简洁。

## 4.8 递归与缓存

递归是函数调用自身：

```python
def factorial(n):
    return 1 if n <= 1 else n * factorial(n - 1)
```

递归要有基准情形，否则会无限递归，最终抛 `RecursionError`。Python 默认递归深度约 1000，可以用 `sys.setrecursionlimit` 调整，但不要依赖它处理非常深的递归；改用迭代或显式栈。

斐波那契的朴素递归会重复计算：

```python
def fibonacci(n):
    return n if n < 2 else fibonacci(n - 1) + fibonacci(n - 2)
```

用 `functools.lru_cache` 缓存结果：

```python
from functools import lru_cache

@lru_cache(maxsize=None)
def fibonacci(n):
    return n if n < 2 else fibonacci(n - 1) + fibonacci(n - 2)
```

`lru_cache` 用参数作为键，因此参数必须可哈希。它会保留缓存，可能占用内存；需要时设置 `maxsize`。

## 4.9 装饰器

装饰器是“接收函数、返回函数”的可调用对象：

```python
def logged(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        print(f"call {function.__name__}{args}")
        return function(*args, **kwargs)
    return wrapper

@logged
def add(left, right):
    return left + right
```

`@logged` 等价于：

```python
add = logged(add)
```

`wrapper` 在调用原函数前后插入逻辑。`functools.wraps` 把原函数的 `__name__`、`__doc__` 等复制到 wrapper，避免调试信息丢失。

### 带参数的装饰器

```python
def repeat(times):
    def decorate(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            result = None
            for _ in range(times):
                result = function(*args, **kwargs)
            return result
        return wrapper
    return decorate

@repeat(3)
def say(message):
    print(message)
```

`repeat(3)` 返回一个装饰器，装饰器再返回 wrapper。三层函数是带参数装饰器的常见结构。

### 装饰器的顺序

```python
@first
@second
def f():
    ...
```

等价于：

```python
f = first(second(f))
```

离函数最近的装饰器先应用。多个装饰器组合时，执行顺序容易混淆；保持装饰器职责单一。

### 类装饰器与 `__call__`

类也可以作为装饰器，只要它实现了 `__call__`；类也可以被装饰。第 7 章会讲类的特殊方法。

## 4.10 代码导览

[`functions.py`](functions.py) 分成六部分：

- `show_parameters()`：位置、关键字、默认值、仅位置、仅关键字、`*args`/`**kwargs`、调用解包；
- `show_mutable_default()`：可变默认参数陷阱；
- `show_scopes()`：LEGB、`global`、`nonlocal`、闭包计数器；
- `show_lambdas()`：lambda、排序 key、延迟绑定与默认参数修复；
- `show_recursion()`：阶乘、带缓存的斐波那契；
- `show_decorators()`：简单装饰器、带参数装饰器、`functools.wraps`。

运行：

```sh
python3 04-functions/functions.py
```

## 4.11 常见陷阱

| 写法 | 问题 | 建议 |
|------|------|------|
| `def f(x, bucket=[])` | 默认值共享 | 用 `None` 哨兵 |
| 函数内给全局名字赋值但没 `global` | 创建局部名字，可能 `UnboundLocalError` | 显式 `global`，或改用参数/返回值 |
| 闭包修改外层变量但没 `nonlocal` | 同上 | 显式 `nonlocal` |
| 循环里创建 lambda 捕获循环变量 | 延迟绑定，结果都是最后一个值 | 默认参数/`partial` |
| 用 `lambda` 写复杂逻辑 | 可读性差 | 用 `def` |
| 递归没有终止条件 | `RecursionError` | 先写基准情形 |
| 递归深度过大 | 栈溢出 | 改迭代或显式栈 |
| `lru_cache` 缓存可变参数 | 参数不可哈希 | 只缓存可哈希参数 |
| 装饰器忘记 `@wraps` | 函数名/文档丢失 | 用 `functools.wraps` |
| 默认参数是函数调用 | 定义时求值一次 | 需要每次调用时求值就放到函数体 |
| `*args` 当成列表 | 它是元组 | 需要列表时 `list(args)` |
| `**kwargs` 当成关键字参数声明 | 它是字典 | 用 `.get()` 或显式参数 |

## 4.12 语法卡片

| 术语 | 一句话定义 | 本章例子 |
|------|------------|----------|
| 函数对象 | 可以被传递、赋值、调用的对象 | `def f(): ...` |
| 位置参数 | 按位置匹配的参数 | `f(1, 2)` |
| 关键字参数 | 按名字匹配的参数 | `f(a=1)` |
| 默认参数 | 调用时可省略的参数 | `def f(x=0)` |
| 仅位置参数 | `/` 之前只能按位置传 | `def f(x, /)` |
| 仅关键字参数 | `*` 之后只能按关键字传 | `def f(*, x)` |
| `*args` | 收集多余位置参数为元组 | `def f(*args)` |
| `**kwargs` | 收集多余关键字参数为字典 | `def f(**kwargs)` |
| LEGB | 名字查找顺序 | Local、Enclosing、Global、Built-in |
| 闭包 | 捕获外层变量的函数 | `make_multiplier` |
| 装饰器 | 接收函数并返回函数的可调用对象 | `@logged` |
| 缓存 | 保存函数结果避免重复计算 | `@lru_cache` |

## 4.13 练习

1. **参数**：写一个函数，同时包含位置参数、仅位置参数、默认参数、仅关键字参数、`*args`、`**kwargs`，并打印收到的值。
2. **可变默认值**：分别用 `bucket=[]` 和 `bucket=None` 写两个追加函数，调用三次，比较结果。
3. **作用域**：写一个函数，内部先打印全局变量再赋值，读 `UnboundLocalError`；加 `global` 后修复。
4. **闭包**：写 `make_counter`，返回一个每次调用加 1 的函数；再写一个 `make_multiplier`。
5. **延迟绑定**：用循环创建三个 lambda，让它们分别返回 0、1、2；比较默认参数和 `partial` 两种修复。
6. **递归**：用递归和迭代分别计算阶乘；用 `lru_cache` 优化斐波那契。
7. **装饰器**：写一个 `logged` 装饰器，打印函数名和参数；再写一个 `repeat(n)` 装饰器。
8. **`functools.wraps`**：去掉 `@wraps`，观察被装饰函数的 `__name__` 变化。
9. **破坏实验**：把 `nonlocal count` 删掉，运行计数器，读 `UnboundLocalError`；再把 `global` 删掉，观察模块变量是否变化。

## 4.14 下一章

**第 5 章 · 容器、迭代与生成器**

函数把行为组织起来，容器把数据组织起来。下一章会讲 `list`、`tuple`、`dict`、`set`、推导式、迭代协议、生成器和 `itertools`。

届时，`for` 循环为什么能遍历列表、文件、生成器，会有完整的答案。
