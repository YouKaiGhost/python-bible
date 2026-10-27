# 第 11 章 · 综合练习：一个小型表达式求值器

> **卷一 · 语言**　|　前置知识：第 0–10 章　|　建议用时：65 分钟

> 这一章不引入新语法。它只把前面的东西拼起来，看看它们能否一起工作。

前面十章分别讲了对象、表达式、控制流、函数、容器、字符串、类、模块、异常和类型注解。现在写一个真正能运行的小程序：一个支持 `+ - * /`、括号、一元正负号和十进制小数的表达式求值器。

它的核心是一个**递归下降解析器**（recursive descent parser）。这个算法直接对应文法，结构清晰，是学习“用 Python 写解析器”的好起点。

我们不会用 `eval`。`eval` 会把字符串交给解释器执行，既能算表达式，也能执行任意代码；这里要的是“只理解算术”，不是“执行任意输入”。

## 11.1 程序目标

输入：

```text
1 + 2 * 3
(1 + 2) * 3
10 / 4
-(2 + 3) * 4
```

输出：

```text
1 + 2 * 3 = 7
(1 + 2) * 3 = 9
10 / 4 = 2.5
-(2 + 3) * 4 = -20
```

支持：

- `+`、`-`、`*`、`/`；
- 括号；
- 一元 `+` 和 `-`；
- 十进制小数（如 `3.14`、`.5`）；
- 空白字符。

不支持：

- 变量、赋值、函数调用；
- 指数记法（`1e3`）；
- 隐式乘法（`2(3)`）；
- `%`、幂运算、比较和逻辑运算；
- 注释。

## 11.2 文法

用 EBNF 写出来：

```text
expression = term { ("+" | "-") term } ;
term       = factor { ("*" | "/") factor } ;
factor     = number
           | "(" expression ")"
           | ("+" | "-") factor ;
number     = digit { digit } [ "." { digit } ]
           | "." digit { digit } ;
```

这个文法已经编码了优先级：

- `expression` 处理加减，优先级最低；
- `term` 处理乘除，优先级高于加减；
- `factor` 处理数字、括号和一元正负号，优先级最高。

左递归被改写成了循环（`{ ... }`），所以递归下降不会陷入无限递归。

## 11.3 程序结构

程序分成四层：

```text
字符
  │  Lexer
  ▼
Token 流
  │  Parser
  ▼
浮点结果 / ParseError
  │  report
  ▼
输出
```

- `TokenKind`：记号的种类；
- `Token`：记号的数据；
- `Lexer`：把字符串切成记号；
- `Parser`：按文法消费记号并求值；
- `ParseError`：带位置的解析错误；
- `report` / `main`：命令行与输出。

没有 AST（抽象语法树）：解析器一边解析一边计算。对这个小文法，这足够；要支持变量、函数、优化时，通常先建 AST，再求值。

## 11.4 记号

```python
class TokenKind(Enum):
    NUMBER = auto()
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    END = auto()
```

`Enum` 让记号种类有名字、可比较、不会和整数混淆。`auto()` 自动分配值。

```python
@dataclass(frozen=True)
class Token:
    kind: TokenKind
    value: float | None
    position: int
```

`Token` 是冻结的 dataclass：

- `kind`：记号类型；
- `value`：只有数字记号有值；
- `position`：在输入中的偏移，用于错误报告。

`frozen=True` 让记号不可变，避免解析过程中意外修改。

## 11.5 词法分析

`Lexer` 持有输入和当前位置：

```python
class Lexer:
    def __init__(self, text: str) -> None:
        self.text = text
        self.position = 0

    def next_token(self) -> Token:
        self._skip_space()
        ...
```

`next_token` 的流程：

1. 跳过空白；
2. 如果到达末尾，返回 `END`；
3. 读取一个字符；
4. 用 `match` 识别单字符运算符；
5. 如果是数字或 `.` 后跟数字，读取完整数字；
6. 其他字符抛 `ParseError`。

### `match` 识别字符

```python
match character:
    case "+":
        return Token(TokenKind.PLUS, None, start)
    case "-":
        return Token(TokenKind.MINUS, None, start)
    ...
```

`match` 在这里比一长串 `if/elif` 更清楚。注意每个分支直接 `return`，没有贯穿。

### 数字

```python
def _number(self) -> Token:
    start = self.position
    has_digit = False

    while ... and self.text[self.position].isdigit():
        has_digit = True
        self.position += 1

    if ... and self.text[self.position] == ".":
        self.position += 1
        while ... and self.text[self.position].isdigit():
            has_digit = True
            self.position += 1

    if not has_digit:
        raise ParseError("invalid number", start)

    text = self.text[start:self.position]
    value = float(text)
    return Token(TokenKind.NUMBER, value, start)
```

`float("1.")` 和 `float(".5")` 都是合法的 Python 字面量形式，正好覆盖我们的文法。

### 错误位置

`Token.position` 记录记号开始的位置。解析器报错时带上这个位置，`report` 才能在输入下方打印插入符。

## 11.6 解析器状态

```python
class Parser:
    def __init__(self, text: str) -> None:
        self.lexer = Lexer(text)
        self.current = self.lexer.next_token()

    def parse(self) -> float:
        value = self._expression()
        if self.current.kind is not TokenKind.END:
            raise ParseError("unexpected token", self.current.position)
        return value
```

`Parser` 持有 lexer 和当前记号。`_advance()` 从 lexer 取下一个记号：

```python
def _advance(self) -> None:
    self.current = self.lexer.next_token()
```

`parse()` 先解析一个完整表达式，然后要求输入已经结束。`2 +` 会在 `_primary()` 报“expected number or '('”；`2 3` 会在 `parse()` 报“unexpected token”。

## 11.7 逐层解析

### `_expression()`：加减

```python
def _expression(self) -> float:
    value = self._term()

    while self.current.kind in (TokenKind.PLUS, TokenKind.MINUS):
        operation = self.current.kind
        self._advance()
        right = self._term()

        if operation is TokenKind.PLUS:
            value += right
        else:
            value -= right

    return value
```

流程：

1. 先解析一个 `term`；
2. 只要当前记号是 `+` 或 `-`，消费它，再解析右边的 `term`；
3. 把结果加/减到 `value`；
4. 循环直到没有加减号。

左结合由循环自然实现：`1 - 2 - 3` 会先算 `1 - 2`，再减 `3`。

### `_term()`：乘除

```python
def _term(self) -> float:
    value = self._factor()

    while self.current.kind in (TokenKind.STAR, TokenKind.SLASH):
        operation = self.current.kind
        position = self.current.position
        self._advance()
        right = self._factor()

        if operation is TokenKind.STAR:
            value *= right
        else:
            if right == 0.0:
                raise ParseError("division by zero", position)
            value /= right

    return value
```

除零检查放在这里，因为只有 `/` 这一层知道除法的位置。错误位置记录的是 `/` 的偏移，而不是右操作数的偏移；指向运算符更直观。

### `_factor()`：一元正负号

```python
def _factor(self) -> float:
    if self.current.kind is TokenKind.PLUS:
        self._advance()
        return self._factor()

    if self.current.kind is TokenKind.MINUS:
        self._advance()
        return -self._factor()

    return self._primary()
```

一元 `+`/`-` 是右结合的，可以叠加：`--5` 是 `-(-5)`，结果是 `5`。递归调用 `_factor()` 自然支持。

### `_primary()`：数字与括号

```python
def _primary(self) -> float:
    if self.current.kind is TokenKind.NUMBER:
        assert self.current.value is not None
        value = self.current.value
        self._advance()
        return value

    if self.current.kind is TokenKind.LEFT_PAREN:
        self._advance()
        value = self._expression()

        if self.current.kind is not TokenKind.RIGHT_PAREN:
            raise ParseError("expected ')'", self.current.position)

        self._advance()
        return value

    raise ParseError("expected number or '('", self.current.position)
```

括号里的 `_expression()` 会递归回最高层，所以括号能改变优先级。

## 11.8 错误报告

```python
class ParseError(Exception):
    def __init__(self, message: str, position: int) -> None:
        super().__init__(message)
        self.message = message
        self.position = position
```

`ParseError` 携带消息和偏移。`report` 捕获它：

```python
try:
    value = evaluate(text)
except ParseError as error:
    print(f"{text} = error: {error.message} at offset {error.position}")
    print(f"  {text}")
    print(f"  {' ' * error.position}^")
else:
    print(f"{text} = {format_number(value)}")
```

输出：

```text
1 / 0 = error: division by zero at offset 2
  1 / 0
    ^
```

插入符的位置是 `error.position`。如果错误发生在输入末尾，偏移等于长度，插入符会出现在最后一个字符之后。

`format_number` 用 `:.12g`：

```python
def format_number(value: float) -> str:
    return f"{value:.12g}"
```

`0.1 + 0.2` 会显示成 `0.3`；提高精度会看到 `0.30000000000000004`。这是浮点表示，不是解析器的错误。

## 11.9 命令行入口

```python
def main(arguments: list[str]) -> int:
    samples = [...]
    if arguments:
        for text in arguments:
            report(text)
        return 0

    print("== expression evaluator ==")
    for text in samples:
        report(text)
    print('\nusage: calc.py "1 + 2 * 3"')
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
```

- 不带参数：运行内置样例；
- 带参数：每个参数当作一个表达式；
- `raise SystemExit(...)` 把返回码交给操作系统。

## 11.10 运行

```sh
python3 11-capstone/calc.py
python3 11-capstone/calc.py "1 + 2 * 3"
python3 11-capstone/calc.py "2 * (3 + 4) - 5" "1 / 0"
```

预期输出：

```text
== expression evaluator ==
1 + 2 * 3 = 7
(1 + 2) * 3 = 9
10 / 4 = 2.5
-3 + 5 = 2
2 * (3 + 4) - 5 = 9
0.1 + 0.2 = 0.3
1 / 0 = error: division by zero at offset 2
  1 / 0
    ^
2 + = error: expected number or '(' at offset 3
  2 +
     ^

usage: calc.py "1 + 2 * 3"
```

## 11.11 已知限制

这个求值器是教学程序，不是生产级计算器：

- 只支持十进制小数，不支持指数记法；
- 数字解析没有处理极大/极小值的溢出；
- 没有 AST，直接求值，无法做变量、函数或优化；
- 错误恢复只报第一个错误；
- 没有运算符优先级表，优先级写死在函数调用链里；
- 空白只支持 `str.isspace()` 识别的字符；
- 不支持 `%`、幂、比较、逻辑、赋值；
- 浮点结果没有做容差处理，`0.1 + 0.2` 不会“自动等于 0.3”。

这些限制是故意的：每增加一个特性，程序就多一层复杂度。先把最小闭环走通，再扩展。

## 11.12 这个程序用到了什么

| 语言/库特性 | 在程序里的位置 |
|-------------|----------------|
| `Enum` | `TokenKind` |
| `@dataclass(frozen=True)` | `Token` |
| 类与封装 | `Lexer`、`Parser` |
| `match` | 词法分析的单字符分派 |
| 异常 | `ParseError` |
| 异常处理 | `report` 捕获解析错误 |
| 类型注解 | 函数签名、字段、返回值 |
| `str.isdigit()` / `isspace()` | 词法分析 |
| `float()` | 数字转换 |
| `sys.argv` | 命令行参数 |
| `f-string` | 输出与错误报告 |
| `raise SystemExit` | 退出码 |

没有用到的：继承、`Protocol`、生成器、上下文管理器、第三方库。不是因为它们不重要，而是这个程序不需要。**能用简单工具解决的问题，不要为了展示语言特性而复杂化。**

## 11.13 练习与扩展

1. **加 `%`**：在 `_term()` 里增加 `%`，注意除零检查。
2. **加幂运算**：增加 `^`，它是右结合的，优先级高于乘除；想想为什么不能简单地在 `_term()` 里加一个循环。
3. **加变量**：支持 `x = 3` 和后续表达式引用 `x`；需要一个符号表（`dict[str, float]`）。
4. **加函数**：支持 `sqrt(2)`、`sin(0.5)`；需要在 `_primary()` 里识别标识符和 `(`。
5. **AST**：把“直接求值”改成“先建语法树，再求值”；比较两种设计的优缺点。
6. **错误恢复**：一次报告多个错误，而不是只报第一个。
7. **容差输出**：让 `0.1 + 0.2` 显示为 `0.3`，同时保留 `1e-15` 级别的小量；设计一个合理的格式化策略。
8. **测试**：用 `unittest` 或 `pytest` 为解析器写表驱动测试，覆盖优先级、结合性、括号、错误输入。
9. **REPL**：让程序读取多行输入，支持空行退出；注意捕获 `EOFError`。

## 11.14 结束语

这个程序不大，但它把前面十章的东西串成了一条线：

- 对象、名字和类型决定了 `Token`、`float`、`None` 怎么用；
- 表达式和控制流决定了 lexer/parser 的分支；
- 函数和递归决定了递归下降的结构；
- 容器和迭代决定了 token 流与样例列表；
- 字符串和编码决定了输入和输出；
- 类和特殊方法决定了 `Lexer`、`Parser`、`Token` 的生命期；
- 模块和导入决定了多文件组织的可能；
- 异常决定了错误如何传播和报告；
- 类型注解让接口意图更清楚。

如果这套教材只让你记住一句话，那应该是：**先问语言保证什么，再问实现碰巧怎么做。** Python 的自由很大，但自由的前提是知道边界在哪里。

附录 A 会把 Python 3.10–3.14 的变化和 `async`/`await`/`asyncio` 摊开。它们不是另一门语言，而是同一套对象模型和协议在新版本里的延伸。
