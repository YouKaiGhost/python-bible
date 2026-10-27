# 第 6 章 · 字符串、字节与编码

> **卷一 · 语言**　|　前置知识：第 5 章　|　建议用时：50 分钟

> `str` 不是字节数组。它是 Unicode 码点序列；`bytes` 才是字节序列。把两者混在一起，是编码 bug 的常见起点。

容器把值组织起来，字符串把文本组织起来。这一章讲 `str`、`bytes`、Unicode、UTF-8、字符串字面量、f-string、格式化和文本/字节边界。

Python 3 把文本和字节分得很清楚：

- `str` 是文本，元素是 Unicode 码点；
- `bytes` 是字节，元素是 0..255 的整数；
- 两者之间用 `encode` / `decode` 转换。

理解这条边界，比背字符串方法更重要。

## 6.1 本章语法地图

| 语法/概念 | 本章出现的位置 |
|-----------|----------------|
| `str` 字面量 | `"hello"`、`'hello'` |
| 三引号 | `"""..."""` |
| 原始字符串 | `r"C:\code"` |
| f-string | `f"{name}: {value:.2f}"` |
| 转义序列 | `\n`、`\t`、`\\` |
| 索引/切片 | `text[0]`、`text[1:4]` |
| 字符串方法 | `strip`、`split`、`join`、`replace` |
| 格式化 | `format`、f-string 格式说明符 |
| `bytes` | `b"hello"`、`bytes([...])` |
| `bytearray` | 可变字节序列 |
| 编解码 | `encode("utf-8")`、`decode("utf-8")` |
| Unicode 规范化 | `unicodedata.normalize` |

## 6.2 `str` 是 Unicode 码点序列

```python
text = "Python 语言"
len(text)       # 9
text[0]         # 'P'
text[-1]        # '言'
text[7:]        # '语言'
```

`len` 返回码点数量，不是字节数，也不是“用户看到的字符数”。对大多数日常文本，一个码点看起来就是一个字符；但组合字符、变体选择符、表情符号序列会让“码点”和“字素簇”不同。

```python
composed = "\u00e9"       # é：一个码点
decomposed = "e\u0301"    # e + 组合重音：两个码点

len(composed)      # 1
len(decomposed)    # 2
composed == decomposed  # False（未规范化）
```

需要比较或搜索用户可见文本时，先做 Unicode 规范化：

```python
import unicodedata

normalized = unicodedata.normalize("NFC", decomposed)
normalized == composed   # True
```

完整的 Unicode 文本处理（字素簇、断行、排序）需要专门库；标准库只提供码点级操作和部分规范化。

### `ord` 与 `chr`

```python
ord("A")   # 65
chr(65)    # 'A'
```

`ord` 接收一个长度为 1 的字符串，返回码点；`chr` 把码点转成字符串。

## 6.3 字符串字面量

```python
single = 'hello'
double = "hello"
triple = """line one
line two"""
raw = r"C:\code\python"
```

- 单引号和双引号等价；
- 三引号可以跨行，保留换行；
- 原始字符串 `r"..."` 不处理反斜杠转义（但末尾不能是奇数个反斜杠）；
- 相邻字符串字面量会拼接：`"Hello, " "World!"`。

转义序列：

| 写法 | 含义 |
|------|------|
| `\n` | 换行 |
| `\t` | 制表符 |
| `\\` | 反斜杠 |
| `\'` | 单引号 |
| `\"` | 双引号 |
| `\0` | 空字符 |
| `\x41` | 十六进制字节/码点 |
| `\u4f60` | Unicode 码点（4 位十六进制） |
| `\U0001F600` | Unicode 码点（8 位十六进制） |

Python 3 源文件默认 UTF-8；如果需要其他编码，可以在文件开头写编码声明：

```python
# -*- coding: utf-8 -*-
```

现代代码几乎不需要这一行，默认就是 UTF-8。

## 6.4 索引与切片

```python
text = "Python"
text[0]      # 'P'
text[-1]     # 'n'
text[1:4]    # 'yth'
text[:3]     # 'Pyt'
text[3:]     # 'hon'
text[::2]    # 'Pto'
text[::-1]   # 'nohtyP'
```

`str` 是不可变序列，切片返回新字符串。索引越界抛 `IndexError`；切片越界会自动截断，不抛异常。

```python
text[100]    # IndexError
text[100:200] # ''
```

字符串没有“字符赋值”：

```python
text[0] = "p"   # TypeError
```

需要修改时创建新字符串：

```python
text = "p" + text[1:]
```

频繁拼接大量字符串时，用 `join` 而不是 `+`：

```python
"".join(parts)
```

## 6.5 常用方法

```python
text = "  Hello, Python!  "

text.strip()          # 'Hello, Python!'
text.lower()          # '  hello, python!  '
text.upper()          # '  HELLO, PYTHON!  '
text.replace("Python", "World")
text.find("Python")   # 9
text.startswith("  H")
text.split(",")       # ['  Hello', ' Python!  ']
"-".join(["a", "b"])  # 'a-b'
```

几个容易混淆的方法：

| 方法 | 作用 |
|------|------|
| `strip()` | 去掉两端空白（或指定字符集） |
| `removeprefix()` / `removesuffix()` | 去掉指定前缀/后缀（3.9） |
| `split()` | 按分隔符切分，默认按空白 |
| `partition()` | 按分隔符切成三段 |
| `casefold()` | 更激进的 Unicode 大小写折叠 |
| `startswith()` / `endswith()` | 前缀/后缀判断 |
| `find()` / `index()` | 查找，找不到时 `-1` / `ValueError` |

`strip("abc")` 去掉的是字符集合 `{a, b, c}` 中的字符，不是子串 `"abc"`。要精确去掉前缀/后缀，用 `removeprefix` / `removesuffix`。

### 大小写

```python
"Straße".lower()     # 'straße'
"Straße".casefold()  # 'strasse'
```

`casefold()` 更适合不区分大小写的比较，因为它会处理更多 Unicode 规则。大小写转换可能改变字符串长度，也可能依赖语言环境；跨语言比较要谨慎。

### `split` 与 `join`

```python
"a,b,c".split(",")      # ['a', 'b', 'c']
"a  b   c".split()      # ['a', 'b', 'c']
",".join(["a", "b"])    # 'a,b'
```

`join` 只接受字符串元素；有非字符串时要先转换：

```python
",".join(str(value) for value in values)
```

## 6.6 f-string 与格式化

```python
name = "Ada"
value = 3.1415926

f"{name}: {value:.2f}"   # 'Ada: 3.14'
```

格式说明符在冒号后：

| 写法 | 含义 |
|------|------|
| `:.2f` | 两位小数 |
| `:>10` | 右对齐，宽度 10 |
| `:*^10` | 居中，用 `*` 填充 |
| `:08d` | 整数宽度 8，前导 0 |
| `:#x` | 十六进制，带 `0x` |
| `:,.2f` | 千位分隔，两位小数 |
| `:e` | 科学计数法 |
| `:%` | 百分比 |

调试用 `=`：

```python
count = 42
f"{count=}"   # 'count=42'
```

`str.format` 是更早的通用格式化接口：

```python
"{name} is {age}".format(name="Ada", age=36)
"{0}-{1}-{0}".format("x", "y")
```

f-string 更短、更直观；需要模板复用或延迟格式化时用 `format`。旧的 `%` 格式化仍然存在，但新代码通常不用。

## 6.7 `bytes` 与 `bytearray`

`bytes` 是不可变字节序列，元素是整数：

```python
data = b"hello"
len(data)        # 5
data[0]          # 104
data[0:2]        # b'he'
```

`bytearray` 是可变的字节序列：

```python
buffer = bytearray(b"abc")
buffer[0] = 65
buffer.append(100)
```

字节字面量只能用 ASCII 字符和转义：

```python
b"hello"
b"\xe4\xbd\xa0"   # UTF-8 的“你”
```

`bytes` 和 `str` 不能直接拼接：

```python
"a" + b"b"   # TypeError
```

需要显式编码/解码。

## 6.8 编码与解码

```python
text = "你好, Python"
encoded = text.encode("utf-8")
decoded = encoded.decode("utf-8")
```

- `str.encode(encoding, errors="strict")` → `bytes`
- `bytes.decode(encoding, errors="strict")` → `str`

UTF-8 是变长编码：

| 字符 | 字节数 |
|------|--------|
| ASCII（`A`、`0`） | 1 |
| 拉丁扩展、希腊字母 | 2 |
| 常用汉字 | 3 |
| 部分表情符号 | 4 |

```python
len("你好")                    # 2 个码点
len("你好".encode("utf-8"))    # 6 个字节
```

### 编码错误

```python
b"\xff".decode("utf-8")   # UnicodeDecodeError
```

`errors` 参数：

| 值 | 行为 |
|----|------|
| `"strict"` | 抛异常（默认） |
| `"ignore"` | 丢弃非法字节 |
| `"replace"` | 用替换字符 `�` |
| `"backslashreplace"` | 用 `\xNN` 表示 |
| `"surrogateescape"` | 保留非法字节，供往返转换 |

不要随便用 `ignore`；它会静默丢数据。需要处理损坏输入时，记录日志或明确替换。

### 读写文件

文本模式：

```python
with open("data.txt", "w", encoding="utf-8") as file:
    file.write("你好\n")
```

二进制模式：

```python
with open("data.bin", "wb") as file:
    file.write(b"\x00\x01")
```

文本模式的默认编码取决于平台/环境；**总是显式写 `encoding="utf-8"`**，除非你明确需要其他编码。`open` 的 `newline` 参数控制换行转换，跨平台文本处理时要注意。

## 6.9 文本与字节的边界

经验规则：

- 程序内部处理文本用 `str`；
- 文件、网络、协议、加密、压缩用 `bytes`；
- 在边界处显式 `encode`/`decode`；
- 不要让 `bytes` 在业务逻辑里到处流动；
- 不要把 `str` 当作“UTF-8 字节数组”来切片。

错误示例：

```python
text = "你好"
text[:1]              # '你'：一个码点
text.encode()[:1]     # b'\xe4'：UTF-8 字节的一半
```

对 `bytes` 按字节切片可能切坏多字节字符；对 `str` 按码点切片不会切坏码点，但可能切坏字素簇。

## 6.10 代码导览

[`strings.py`](strings.py) 分成七部分：

- `show_unicode()`：`len`、索引、切片、`ord`/`chr`、NFC 规范化；
- `show_literals()`：单/双/三引号、原始字符串、f-string、转义；
- `show_methods()`：`strip`、`split`、`join`、`replace`、`casefold`；
- `show_formatting()`：f-string 格式说明符、`format`；
- `show_bytes()`：`bytes`、`bytearray`、编码/解码、错误处理；
- `show_repr()`：`str` 与 `repr`；
- `show_text_processing()`：清洗、大小写、`translate`。

运行：

```sh
python3 06-strings-text/strings.py
```

## 6.11 常见陷阱

| 写法 | 问题 | 建议 |
|------|------|------|
| 用 `len(str)` 当字节数 | 返回码点数 | 需要字节时先 `encode` |
| 对 `str` 按字节切片 | 可能切坏字符 | 对 `str` 按码点/字素切 |
| `"a" + b"b"` | 类型错误 | 显式编码/解码 |
| `open()` 不写 `encoding` | 依赖平台默认编码 | 显式 `encoding="utf-8"` |
| 用 `errors="ignore"` 静默丢数据 | 数据损坏不可见 | 记录/替换/严格处理 |
| 用 `lower()` 做 Unicode 大小写比较 | 规则不完整 | 用 `casefold()` |
| 用 `strip("abc")` 去前缀 | 去掉的是字符集合 | 用 `removeprefix` |
| 大量 `+=` 拼接字符串 | 可能 O(n²) | 收集后用 `join` |
| 认为一个码点等于一个字素 | 组合字符/表情 | 需要时用专门库 |
| 把 `bytes` 当文本打印 | 显示 `b'...'` | 先 `decode` |

## 6.12 语法卡片

| 术语 | 一句话定义 | 本章例子 |
|------|------------|----------|
| `str` | Unicode 码点序列 | `"你好"` |
| `bytes` | 不可变字节序列 | `b"hello"` |
| `bytearray` | 可变字节序列 | `bytearray(b"abc")` |
| 编码 | `str` → `bytes` | `text.encode("utf-8")` |
| 解码 | `bytes` → `str` | `data.decode("utf-8")` |
| 码点 | Unicode 的抽象字符编号 | `ord("A")` |
| 字素簇 | 用户感知的一个字符 | 可能由多个码点组成 |
| 规范化 | 统一 Unicode 表示 | `unicodedata.normalize` |
| f-string | 内嵌表达式的字符串字面量 | `f"{value:.2f}"` |
| 原始字符串 | 不处理反斜杠转义 | `r"C:\code"` |

## 6.13 练习

1. **长度**：分别打印 `len("你好")`、`len("你好".encode("utf-8"))`、`len("é")`、`len("e\u0301")`，解释差异。
2. **规范化**：用 `unicodedata.normalize` 比较组合字符和预组合字符，验证 NFC 后相等。
3. **格式化**：用 f-string 输出两位小数、右对齐、十六进制、百分比和千位分隔。
4. **方法**：用 `split`、`join`、`strip`、`removeprefix` 清洗一段文本。
5. **编码**：把一段中文编码成 UTF-8，打印字节和长度，再解码回来验证相等。
6. **错误处理**：用 `errors="replace"` 和 `errors="ignore"` 解码非法字节，比较结果。
7. **文件**：用 `encoding="utf-8"` 写入和读取一个文本文件；再用二进制模式写入并读取字节。
8. **`repr`**：打印包含换行、引号、反斜杠的字符串的 `str` 和 `repr`，比较可读性。
9. **破坏实验**：把 `"a" + b"b"` 放进代码，读 `TypeError`；再对 `bytes` 按 1 字节切片解码，观察 `UnicodeDecodeError`。

## 6.14 下一章

**第 7 章 · 类与对象模型**

字符串是标准库提供的不可变对象。下一章会讲如何定义自己的对象：类、实例、方法、属性、特殊方法、继承、MRO、dataclass 和 `__slots__`。

届时，`str` 为什么能 `len()`、能切片、能比较，会有完整的答案：它实现了序列协议和一堆特殊方法。
