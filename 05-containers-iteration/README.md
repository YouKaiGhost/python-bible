# 第 5 章 · 容器、迭代与生成器

> **卷一 · 语言**　|　前置知识：第 1–4 章　|　建议用时：55 分钟

> 容器决定数据怎么放，迭代决定数据怎么流。Python 把两者都做成了协议，而不是一组固定语法。

函数把行为组织起来，容器把数据组织起来。这一章讲 `list`、`tuple`、`dict`、`set`、推导式、切片、解包、迭代协议、生成器和 `itertools`。

Python 的容器不是“数组、哈希表、集合”的简单别名，它们各自有复杂度、可变性和顺序保证。迭代协议则把 `for`、推导式、生成器、文件、数据库游标统一成一套接口。

## 5.1 本章语法地图

| 语法/概念 | 本章出现的位置 |
|-----------|----------------|
| `list` | `[1, 2, 3]`、`append`、`pop` |
| `tuple` | `(1, 2)`、解包 |
| `dict` | `{"a": 1}`、`items()`、`get()` |
| `set` / `frozenset` | `{1, 2}`、集合运算 |
| 切片 | `values[1:4]`、`values[::-1]` |
| 推导式 | `[x * x for x in values]` |
| 解包 | `head, *tail = values` |
| 迭代协议 | `iter()`、`next()`、`StopIteration` |
| 生成器 | `yield`、`yield from` |
| 生成器表达式 | `(x * x for x in values)` |
| `itertools` | `islice`、`count`、`chain` |
| `collections` | `Counter`、`defaultdict`、`deque` |

## 5.2 `list`：动态数组

```python
values = [10, 20, 30]
values.append(40)
values.extend([50, 60])
values.insert(1, 15)
```

`list` 是可变、有序、可重复的序列。底层通常是动态数组：

- 尾部 `append` 平均 O(1)；
- 中间插入/删除 O(n)；
- 按下标访问 O(1)；
- `in` 是线性扫描 O(n)。

常用操作：

```python
values[0]       # 第一个
values[-1]      # 最后一个
values[1:4]     # 切片，返回新列表
values[::2]     # 步长
values[::-1]    # 反转副本
values.pop()    # 删除并返回最后一个
values.remove(x) # 删除第一个等于 x 的元素
```

`sort` 原地排序，返回 `None`：

```python
values.sort()
values.sort(reverse=True)
values.sort(key=len)
```

`sorted` 返回新列表：

```python
ordered = sorted(values)
```

Python 的排序是稳定的：相等元素的相对顺序保持不变。

### 列表的别名

```python
original = [1, 2]
alias = original
alias.append(3)
print(original)   # [1, 2, 3]
```

切片和 `list()` 创建浅拷贝：

```python
copy1 = original[:]
copy2 = list(original)
copy3 = original.copy()
```

## 5.3 `tuple`：不可变序列

```python
point = (3, 4)
x, y = point
```

元组适合：

- 固定数量的异构值（坐标、数据库行、函数返回多个值）；
- 需要哈希的键；
- 不希望被修改的序列。

单元素元组必须带逗号：

```python
single = (42,)   # 元组
not_tuple = (42) # 整数
```

元组本身不可变，但可以包含可变对象：

```python
pair = (1, [2, 3])
pair[1].append(4)   # 合法
pair[0] = 99        # TypeError
```

元组可哈希的前提是所有元素都可哈希：

```python
hash((1, 2))       # 可以
hash((1, [2, 3]))  # TypeError
```

## 5.4 `dict`：哈希表

```python
scores = {"Ada": 98, "Grace": 95}
scores["Linus"] = 91
```

`dict` 是可变映射，键必须可哈希，值任意。3.7 起保证按插入顺序迭代。

常用操作：

```python
scores["Ada"]                 # KeyError if missing
scores.get("missing", 0)      # 默认值
scores.setdefault("Ada", 0)   # 存在则返回，不存在则插入
scores.items()                # 键值对视图
scores.keys()                 # 键视图
scores.values()               # 值视图
scores.update({"Alan": 90})   # 批量更新
scores | {"Alan": 90}         # 合并（3.9），返回新字典
```

`dict` 的键通常是不可变对象：字符串、数字、元组。列表、字典、集合不能做键。

### 字典的顺序

```python
mapping = {}
mapping["b"] = 1
mapping["a"] = 2
print(list(mapping))   # ['b', 'a']
```

插入顺序是语言保证的（3.7+），不是 CPython 实现细节。但“有序”不等于“排序”；需要排序时用 `sorted(mapping.items())`。

### `get` 与 `[]`

```python
value = mapping["missing"]        # KeyError
value = mapping.get("missing")    # None
value = mapping.get("missing", 0) # 0
```

不要用 `if key in mapping: value = mapping[key]` 然后再 `else`，除非你确实需要区分“键不存在”和“值为 None”。

## 5.5 `set` 与 `frozenset`

集合是无序、元素唯一、元素可哈希的容器：

```python
left = {1, 2, 3, 4}
right = {3, 4, 5, 6}

left | right   # 并集
left & right   # 交集
left - right   # 差集
left ^ right   # 对称差
```

`set` 可变，`frozenset` 不可变且可哈希：

```python
mutable = {1, 2}
immutable = frozenset({1, 2})
```

集合的典型用途：

- 去重：`set(values)`；
- 成员测试：`x in values` 平均 O(1)；
- 集合运算：交集、并集、差集；
- 作为字典键（`frozenset`）。

集合不保证顺序，不要依赖 `set` 的迭代顺序。

## 5.6 推导式

列表推导式：

```python
squares = [value * value for value in range(6)]
evens = [value for value in range(10) if value % 2 == 0]
```

字典推导式：

```python
lengths = {name: len(name) for name in names}
```

集合推导式：

```python
unique_lengths = {len(word) for word in words}
```

生成器表达式：

```python
lazy = (value * value for value in range(1_000_000))
```

推导式可以有多个 `for` 和 `if`：

```python
pairs = [(x, y) for x in range(3) for y in range(2)]
```

### 推导式的作用域

Python 3 的推导式有自己的作用域，循环变量不会泄漏：

```python
values = [1, 2, 3]
squares = [value * value for value in values]
# print(value)  # NameError
```

但 `for` 语句的循环变量会泄漏：

```python
for value in values:
    pass
print(value)   # 3
```

这是推导式与 `for` 语句的一个微妙差别。

### 什么时候不用推导式

- 逻辑太复杂，嵌套超过两层；
- 有副作用（修改外部状态、打印、写文件）；
- 需要 `try`/`except`；
- 可读性比“一行”更重要。

推导式适合“从已有序列构造新序列”，不适合当通用控制流。

## 5.7 切片与解包

切片：

```python
values[start:stop:step]
```

规则：

- `start` 包含，`stop` 不包含；
- 省略 `start` 从开头，省略 `stop` 到结尾；
- 负数索引从末尾算；
- `step` 可以为负；
- 切片返回新对象（浅拷贝）。

```python
values = [0, 1, 2, 3, 4, 5]
values[1:4]   # [1, 2, 3]
values[:3]    # [0, 1, 2]
values[3:]    # [3, 4, 5]
values[::2]   # [0, 2, 4]
values[::-1]  # [5, 4, 3, 2, 1, 0]
```

解包：

```python
first, second = [1, 2]
head, *middle, last = [1, 2, 3, 4]
```

解包要求数量匹配；`*` 收集剩余元素到列表。

## 5.8 迭代协议

`for` 能遍历对象，是因为对象实现了**迭代协议**：

```python
iterator = iter(values)
while True:
    try:
        value = next(iterator)
    except StopIteration:
        break
    print(value)
```

- **可迭代对象**（iterable）实现 `__iter__`，返回一个迭代器；
- **迭代器**（iterator）实现 `__next__`，返回下一个元素，没有元素时抛 `StopIteration`；
- 迭代器通常也实现 `__iter__`，返回自身。

`for` 语句大致等价于上面的 `while`。列表、元组、字典、集合、字符串、文件、生成器都是可迭代对象。

```python
values = [1, 2, 3]
iterator = iter(values)
next(iterator)   # 1
next(iterator)   # 2
next(iterator)   # 3
next(iterator)   # StopIteration
```

迭代器是**一次性**的：遍历完后不能自动重置。需要再次遍历时，重新调用 `iter()` 或重新创建可迭代对象。

## 5.9 生成器

生成器函数用 `yield` 产生值：

```python
def count_up(limit):
    current = 0
    while current < limit:
        yield current
        current += 1

for value in count_up(3):
    print(value)
```

调用生成器函数不会立刻执行函数体，而是返回一个生成器对象。每次 `next()` 执行到下一个 `yield`，暂停并保留局部状态。

```python
generator = count_up(3)
next(generator)   # 0
next(generator)   # 1
next(generator)   # 2
next(generator)   # StopIteration
```

生成器适合：

- 处理大文件/大数据流，不需要一次性放进内存；
- 表示无限序列；
- 把复杂迭代逻辑写成普通函数；
- 管道式数据处理。

### `yield from`

`yield from` 把另一个可迭代对象的元素逐个转发：

```python
def chain(*iterables):
    for iterable in iterables:
        yield from iterable
```

它比手写 `for value in iterable: yield value` 更简洁，也能正确转发 `send`/`throw`（生成器高级用法）。

### 生成器表达式

```python
squares = (value * value for value in range(10))
sum(squares)
```

生成器表达式是惰性的：只有迭代时才计算。它适合“只需要遍历一次”的场景。需要多次遍历或随机访问时，用列表。

### 生成器只能遍历一次

```python
generator = (value for value in [1, 2, 3])
list(generator)   # [1, 2, 3]
list(generator)   # []
```

第二次遍历时生成器已经耗尽。这是新手常见的 bug。

## 5.10 `itertools` 与 `collections`

### `itertools`

```python
from itertools import count, islice, chain, zip_longest

islice(count(10, 5), 5)   # 10, 15, 20, 25, 30
chain([1, 2], [3, 4])     # 1, 2, 3, 4
zip_longest([1, 2], [3])  # (1, 3), (2, None)
```

`itertools` 里的函数大多返回迭代器，适合惰性处理。常用还有 `product`、`permutations`、`combinations`、`groupby`、`accumulate`。

### `collections`

```python
from collections import Counter, defaultdict, deque

Counter("abracadabra")
defaultdict(list)
deque([1, 2, 3])
```

- `Counter`：计数；
- `defaultdict`：缺失键自动创建默认值；
- `deque`：双端队列，两端插入/删除 O(1)。

这些是标准库容器，不是语言语法；但它们是 Python 日常代码的重要组成部分。

## 5.11 容器选择

| 需求 | 选择 |
|------|------|
| 有序、可变、可重复 | `list` |
| 有序、不可变、可哈希 | `tuple` |
| 键值映射、插入顺序 | `dict` |
| 去重、成员测试、集合运算 | `set` |
| 不可变集合、可哈希 | `frozenset` |
| 计数 | `collections.Counter` |
| 缺失键有默认值 | `collections.defaultdict` |
| 两端高效增删 | `collections.deque` |
| 大文件/流式处理 | 生成器 / 迭代器 |

选择容器时，先问：

1. 需要顺序吗？
2. 需要修改吗？
3. 需要按值查找吗？
4. 需要哈希吗？
5. 数据量多大，能否一次性放进内存？

## 5.12 代码导览

本章有两个程序：

- [`containers.py`](containers.py)：`list`、`tuple`、`dict`、`set`、推导式、`enumerate`/`zip`、`collections`、浅拷贝。
- [`iteration.py`](iteration.py)：`iter`/`next`、生成器、`yield from`、惰性求值、无限序列、`iter(callable, sentinel)`。

运行：

```sh
python3 05-containers-iteration/containers.py
python3 05-containers-iteration/iteration.py
```

## 5.13 常见陷阱

| 写法 | 问题 | 建议 |
|------|------|------|
| 遍历列表时删除元素 | 跳过元素或行为异常 | 遍历副本，或先收集要删的元素 |
| `list.sort()` 赋值给变量 | 返回 `None` | 用 `sorted()` 或分开调用 |
| `(42)` 当单元素元组 | 它是整数 | 写 `(42,)` |
| 用列表做字典键 | 不可哈希 | 用元组/字符串 |
| 依赖集合顺序 | 不保证 | 需要顺序时排序 |
| 生成器遍历两次 | 第二次为空 | 重新创建或改用列表 |
| 推导式里做副作用 | 可读性差、顺序不直观 | 用普通循环 |
| 浅拷贝嵌套列表 | 内部对象共享 | 用 `deepcopy` |
| `dict["missing"]` | `KeyError` | 用 `get()` 或先判断 |
| `set` 里放列表 | 元素不可哈希 | 用元组 |
| 一次性把大文件读进列表 | 内存占用高 | 用迭代器/生成器 |

## 5.14 语法卡片

| 术语 | 一句话定义 | 本章例子 |
|------|------------|----------|
| `list` | 可变、有序序列 | `[1, 2, 3]` |
| `tuple` | 不可变序列 | `(1, 2)` |
| `dict` | 键值映射 | `{"a": 1}` |
| `set` | 无序、唯一元素集合 | `{1, 2}` |
| 切片 | 按范围取子序列 | `values[1:4]` |
| 推导式 | 从序列构造新容器 | `[x * x for x in xs]` |
| 可迭代对象 | 能返回迭代器的对象 | 列表、文件 |
| 迭代器 | 用 `next()` 逐个产出元素的对象 | `iter(values)` |
| 生成器 | 用 `yield` 产生值的函数 | `count_up(3)` |
| 生成器表达式 | 惰性推导式 | `(x for x in xs)` |
| `itertools` | 迭代器工具库 | `islice`、`chain` |

## 5.15 练习

1. **列表**：创建一个列表，练习 `append`、`insert`、`pop`、`remove`、切片、`sort`，打印每一步。
2. **元组**：用元组表示坐标，解包并计算距离；尝试修改元素，读 `TypeError`。
3. **字典**：统计一段文本中每个单词出现的次数，分别用普通 `dict` 和 `Counter`。
4. **集合**：给两个列表，求交集、并集、差集和对称差。
5. **推导式**：用列表/字典/集合推导式分别生成平方数、长度映射、唯一长度。
6. **迭代器**：手动调用 `iter()`/`next()` 遍历一个列表，捕获 `StopIteration`。
7. **生成器**：写一个生成斐波那契数列的生成器，用 `islice` 取前 10 个。
8. **惰性**：比较列表推导式和生成器表达式在创建时的求值差异（用打印函数观察）。
9. **管道**：用生成器把“读数字 → 过滤偶数 → 平方 → 求和”串起来。
10. **破坏实验**：在遍历列表时删除元素，观察漏掉的元素；再用副本修复。

## 5.16 下一章

**第 6 章 · 字符串、字节与编码**

容器把值组织起来，字符串把文本组织起来。下一章会讲 `str`、`bytes`、Unicode、UTF-8、f-string、格式化和文本/字节边界。

届时，`len("你好")` 为什么是 2，而 `len("你好".encode("utf-8"))` 是 6，会有完整的答案。
