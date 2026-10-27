# 第 3 章 · 控制流与模式匹配

> **卷一 · 语言**　|　前置知识：第 2 章　|　建议用时：40 分钟

> 程序不是一条直线。控制流决定哪条线被走到，走多少次，什么时候离开。

表达式负责算出值，控制流负责决定“算哪一个”。这一章讲 `if`、`while`、`for`、`break`、`continue`、循环 `else`，以及 Python 3.10 引入的 `match` 结构化模式匹配。

Python 的控制流表面上和 C/C++ 很像，但有几个独特之处：缩进是语法，`for` 是“遍历可迭代对象”而不是三段式循环，循环可以带 `else`，`match` 不是 `switch` 的简单替代。

## 3.1 本章语法地图

| 语法 | 本章出现的位置 |
|------|----------------|
| `if` / `elif` / `else` | `if value > 0: ...` |
| `while` | `while count > 0: ...` |
| `for` | `for value in range(3): ...` |
| `break` / `continue` | 跳出/跳过循环 |
| 循环 `else` | `for ...: ... else: ...` |
| `match` / `case` | 结构化模式匹配 |
| 模式 | 字面量、捕获、`_`、序列、映射、类、守卫 |
| `pass` | 空语句 |
| 真值测试 | `if item:` |

## 3.2 缩进就是语法

Python 用缩进表示代码块：

```python
if value > 0:
    print("positive")
    print("still inside")
print("outside")
```

规则：

- 复合语句头以冒号 `:` 结束；
- 同一块的语句缩进必须一致；
- 本书统一用 4 个空格；
- 不要混用 Tab 和空格，否则可能抛 `TabError`；
- 空行不影响语义，但影响可读性。

缩进不是“风格建议”，而是语法的一部分。C/C++ 的 `{}` 在 Python 里变成了“缩进层级”。

## 3.3 `if`：条件分支

```python
if value > 0:
    print("positive")
elif value < 0:
    print("negative")
else:
    print("zero")
```

条件使用真值测试：

```python
if items:          # 非空容器
    ...
if name:           # 非空字符串
    ...
if value is not None:
    ...
```

不要用 `if value == True:` 判断布尔值；直接写 `if value:` 或 `if not value:`。

### 条件表达式

`if` 语句是语句；条件表达式是表达式：

```python
label = "positive" if value > 0 else "non-positive"
```

复杂的多分支用 `if`/`elif`/`else`，不要嵌套条件表达式。

## 3.4 `while`：先判断，再循环

```python
count = 3
while count > 0:
    print(count)
    count -= 1
```

执行顺序：

1. 判断条件；
2. 条件为真，执行循环体；
3. 回到步骤 1；
4. 条件为假，退出。

如果第一次条件就为假，循环体一次也不执行。

Python 没有 `do-while`。需要“至少执行一次”时，用：

```python
while True:
    value = input("> ")
    if value == "quit":
        break
```

## 3.5 `for`：遍历可迭代对象

Python 的 `for` 不是 C 的三段式循环，而是**对可迭代对象逐个取元素**：

```python
for value in [10, 20, 30]:
    print(value)
```

等价于：

```python
iterator = iter([10, 20, 30])
while True:
    try:
        value = next(iterator)
    except StopIteration:
        break
    print(value)
```

所以 `for` 能遍历任何实现了迭代协议的对象：列表、元组、字符串、字典、集合、文件、生成器、`range`。

### `range`

```python
range(5)          # 0, 1, 2, 3, 4
range(2, 8)       # 2, 3, 4, 5, 6, 7
range(2, 8, 2)    # 2, 4, 6
range(5, 0, -1)   # 5, 4, 3, 2, 1
```

`range` 是惰性序列，不会一次性创建所有元素。它支持 `len()`、索引和成员测试，但通常直接用于循环。

### `enumerate` 与 `zip`

```python
for index, value in enumerate(["a", "b", "c"]):
    print(index, value)

for name, score in zip(names, scores):
    print(name, score)
```

`zip` 在最短的输入耗尽时停止。需要补齐时用 `itertools.zip_longest`。

### 字典遍历

```python
for key in mapping:
    ...

for key, value in mapping.items():
    ...

for value in mapping.values():
    ...
```

字典迭代的是键，且按插入顺序（3.7 起保证）。

### 循环变量会泄漏

`for` 的循环变量在循环结束后仍然存在：

```python
for value in range(3):
    pass
print(value)   # 2
```

这与其他一些语言不同。列表推导式有自己的作用域，循环变量不会泄漏（第 5 章会讲）。

## 3.6 `break` 与 `continue`

```python
for value in range(10):
    if value == 2:
        continue   # 跳过 2
    if value == 5:
        break      # 到 5 就停
    print(value)
```

- `break` 立即退出**最内层**循环；
- `continue` 跳过本轮剩余部分，进入下一轮；
- 两者都只影响最内层循环，不会跳出多层嵌套。

跳出多层循环的常见写法：

- 用标志变量；
- 把循环封装成函数，用 `return`；
- 用 `for ... else` 或 `match` 重新组织；
- 用异常（不推荐作为常规控制流）。

## 3.7 循环 `else`

`for` 和 `while` 可以带 `else`：

```python
for value in [1, 3, 5, 7]:
    if value % 2 == 0:
        print("found even:", value)
        break
else:
    print("no even number")
```

`else` 在循环**没有被 `break` 中断**时执行：

- 循环正常结束（包括空序列）→ 执行 `else`；
- 循环被 `break` → 跳过 `else`。

它不是“如果循环体一次都没执行”，而是“如果循环没有提前退出”。这个语义容易记错，初学阶段可以先用标志变量，熟悉后再用 `else`。

`while ... else` 同理：

```python
count = 0
while count < 3:
    count += 1
else:
    print("finished without break")
```

## 3.8 `match`：结构化模式匹配

Python 3.10 引入了 `match`：

```python
match command:
    case "add":
        print("add")
    case "quit":
        print("quit")
    case _:
        print("unknown")
```

它看起来像 `switch`，但语义不同：

- 没有贯穿（不需要 `break`）；
- `case` 是**模式**，不是常量标签；
- 模式可以解构序列、映射、对象；
- 可以带守卫 `if`；
- 匹配成功后执行对应块，然后结束整个 `match`。

### 字面量与 OR 模式

```python
match value:
    case 0:
        print("zero")
    case 1 | 2 | 3:
        print("small")
    case _:
        print("other")
```

`|` 表示“或”。OR 模式中所有分支必须绑定相同的名字集合（如果有捕获）。

### 捕获与通配符

```python
match value:
    case 0:
        print("zero")
    case number:
        print("captured:", number)
```

`number` 是一个**捕获模式**：它匹配任何值，并把值绑定到 `number`。捕获模式总是匹配，所以它后面的 `case` 都不可达；`case _` 是特殊的通配符，不绑定名字。

```python
case _:
    ...
```

`_` 必须放在最后，否则后面的分支不可达。

### 序列模式

```python
match values:
    case []:
        print("empty")
    case [x]:
        print("one:", x)
    case [x, y] if x == y:
        print("two equal:", x)
    case [x, y]:
        print("two:", x, y)
    case [first, *rest]:
        print("first:", first, "rest:", rest)
    case _:
        print("other")
```

序列模式匹配列表、元组等序列类型，长度必须匹配（`*rest` 可以吸收剩余元素）。

### 映射模式

```python
match payload:
    case {"type": "circle", "radius": radius}:
        print("circle:", radius)
    case {"type": "rectangle", "width": width, "height": height}:
        print("rectangle:", width, height)
    case _:
        print("unknown")
```

映射模式只要求指定的键存在，不要求映射只有这些键；它匹配字典等映射类型。

### 类模式

```python
match point:
    case Point(x=0, y=0):
        print("origin")
    case Point(x=0, y=y):
        print("on y-axis:", y)
    case Point(x=x, y=y):
        print("point:", x, y)
```

类模式先用 `isinstance` 检查类型，再按属性匹配。`Point` 需要是类，且属性可访问。第 7 章定义类后可以回来试。

### 守卫

```python
match value:
    case int() as number if number > 0:
        print("positive int:", number)
    case int() as number:
        print("non-positive int:", number)
    case _:
        print("not an int")
```

守卫是 `case` 末尾的 `if` 条件；只有模式匹配且守卫为真时才选中。

### `match` 不是 `switch`

- 没有贯穿；
- 不需要 `break`；
- 模式可以解构对象；
- `case` 顺序重要；
- `match` 只是一个语句，不会自动创建作用域；捕获的变量在 `match` 之后仍然可见。

## 3.9 `pass` 与空块

`pass` 是一个空语句，什么都不做：

```python
if ready:
    pass   # 先占位，稍后实现
```

Python 不允许空块，所以需要占位时用 `pass`。

## 3.10 代码导览

[`control.py`](control.py) 分成七部分：

- `show_if()`：`if` / `elif` / `else` 与真值；
- `show_while()`：`while` 与 `while True`；
- `show_for()`：`range`、`enumerate`、字符串、字典；
- `show_break_continue()`：`break` / `continue`；
- `show_loop_else()`：循环 `else`；
- `show_match()`：字面量、OR、序列、映射、守卫、类模式；
- `show_pass()`：空语句。

运行：

```sh
python3 03-control-flow/control.py
```

## 3.11 常见陷阱

| 写法 | 问题 | 建议 |
|------|------|------|
| 忘记复合语句后的冒号 | `SyntaxError` | 每个 `if`/`for`/`while`/`def`/`class` 头都要冒号 |
| 缩进不一致 | `IndentationError` / `TabError` | 统一 4 空格 |
| `if x = 1:` | 赋值不是比较 | 用 `==` |
| `for` 里修改正在遍历的列表 | 迭代行为异常 | 遍历副本或先收集修改 |
| `break` 以为能跳出多层 | 只跳出最内层 | 用函数/标志/重构 |
| 循环 `else` 当成“没执行” | 语义是“没被 break” | 记清楚或先用标志 |
| 在 `case _` 后写其他分支 | 不可达 | `_` 放最后 |
| OR 模式绑定不同名字 | 语法错误 | 保证绑定集合一致 |
| 捕获模式放在前面 | 后面的分支不可达 | 具体模式在前，捕获在后 |
| 依赖集合遍历顺序 | 不保证 | 需要顺序时排序 |
| `match` 当 `switch` 用 | 没有贯穿，模式语义不同 | 先读模式规则 |

## 3.12 语法卡片

| 术语 | 一句话定义 | 本章例子 |
|------|------------|----------|
| 复合语句 | 带头部、冒号和缩进块的语句 | `if`、`for`、`while` |
| 真值测试 | 条件表达式的真假判断 | `if items:` |
| 可迭代对象 | 能被 `for` 遍历的对象 | 列表、字符串、`range` |
| `range` | 惰性整数序列 | `range(3)` |
| `enumerate` | 同时给出索引和值 | `enumerate(values)` |
| `break` | 退出最内层循环 | `break` |
| `continue` | 跳过本轮剩余部分 | `continue` |
| 循环 `else` | 没有 `break` 时执行 | `for ... else:` |
| `match` | 结构化模式匹配 | `match value:` |
| 捕获模式 | 匹配任何值并绑定名字 | `case x:` |
| 通配符 | 匹配任何值但不绑定 | `case _:` |
| 守卫 | 模式后的额外条件 | `case x if x > 0:` |

## 3.13 练习

1. **符号判断**：读入一个整数，输出正数、负数或零。
2. **阶乘表**：用 `for` 打印 1 到 10 的阶乘。
3. **猜数字**：用 `while` 和 `input()` 写一个猜数字循环，输入 `quit` 退出。
4. **循环 `else`**：在列表中查找一个值，找到就 `break`，用 `else` 输出“没找到”。
5. **`match` 命令**：用 `match` 解析 `"add"`、`"sub"`、`"quit"` 三个命令，未知命令走 `case _`。
6. **序列模式**：用 `match` 匹配 `[]`、`[x]`、`[x, y]`、`[first, *rest]` 四种列表。
7. **映射模式**：匹配 `{"type": "circle", "radius": r}` 和 `{"type": "rectangle", ...}`。
8. **类模式**：先定义一个简单的 `Point` 类，用 `match` 匹配原点和坐标轴上的点（第 7 章会讲类）。
9. **破坏实验**：把 `case _` 放到 `match` 中间，观察是否还能匹配后面的分支；再删掉 `for` 的冒号，读 `SyntaxError`。

## 3.14 下一章

**第 4 章 · 函数、作用域与闭包**

控制流把语句组织成路径，函数把路径组织成可复用的单元。下一章会讲参数传递、默认值、`*args`/`**kwargs`、LEGB 作用域、闭包、递归、lambda 和装饰器。

届时，`for` 循环里的每个分支都可能变成一个函数，而函数本身也可以像值一样被传递。
