# Python 语言圣经

> 用 Python 讲 Python。只讨论语法、对象模型与语言特性。

这是一套“自解释”的 Python 语言教材：每一章都是一个可以运行、修改、破坏的程序。源码是课文，Markdown 是路标，解释器是裁判。

它是 [C 语言圣经](https://github.com/YouKaiGhost/c-bible) 和 [C++ 语言圣经](https://github.com/YouKaiGhost/cpp-bible) 的 Python 姊妹篇。C/C++ 两本回答“标准保证了什么”；这一本继续追问：当语言有了动态类型、垃圾回收、闭包、描述符和协议之后，这些问题变成了什么样。

**当前进度：第 0–11 章已完成，覆盖 Python 3.12 的核心语言，并附一个综合练习和一份 Python 3.10–3.14 / 异步速览。**

## 为什么叫“圣经”？

这里的“圣经”不是宗教文本，也不是说它是唯一正确的 Python 教材。这里的“经”取的是“正经”的意思：一套关于 Python 语言本身的、尽量回到语言参考与第一性原理的读本。

本教材只回答这类问题：

- 一个名字绑定到了什么对象？
- 对象的身份、类型和值分别是什么？`is` 和 `==` 差在哪里？
- 可变对象和不可变对象在赋值、传参、哈希时有什么不同？
- 闭包捕获的是变量还是值？装饰器到底装饰了什么？
- 类的属性查找顺序是什么？`self` 从哪里来？
- 模块、包、导入系统如何工作？
- 异常、上下文管理器、生成器、类型注解在语言层面保证了什么？

它不教你写 Web 框架，不教你用 ORM，也不把“常见写法”冒充“语言规则”。遇到 CPython 实现细节与语言规范不一致的地方，会明确区分。

## 这套教材适合谁

- 已经会至少一门编程语言，想系统补齐 Python 语法的人；
- 写过 Python，却对可变性、闭包、描述符、MRO、导入系统、生成器似懂非懂的人；
- 想从“能跑”走向“知道语言保证了什么”的人。

它不适合完全没写过代码的人，也不是标准库 API 手册。标准库只在必要的地方出现，例如 `dataclasses`、`contextlib`、`collections`、`itertools`。

## 阅读方法

每章按同一个节奏展开：

1. **读**：先看这一章引入的语法。
2. **跑**：直接运行完整程序。
3. **拆**：逐节解剖，知道每个名字为什么在那里。
4. **坏**：故意改错一个缩进、去掉一个 `nonlocal`、覆盖一个特殊方法，读解释器的反应。
5. **练**：做练习，把知识变成手上的动作。

Python 没有编译期，很多错误只在运行时出现。这使“跑”和“坏”比 C/C++ 更重要：解释器不会替你检查所有东西，测试和静态检查是后来补上的安全带。

## 开始

要求：Python 3.12 或更高版本。本书以 **CPython 3.12** 为基线；涉及 3.10/3.11/3.13/3.14 的地方会单独标注。源文件使用 UTF-8 编码。

```sh
make          # 用 compileall 检查全部源码
make check    # 清理缓存，重新编译并运行全部示例（-W error）
make run      # 依次运行全部示例
```

如果 `python3` 不是 3.12，显式指定解释器：

```sh
make check PYTHON=python3.12
```

也可以进入章节目录直接运行：

```sh
cd 00-hello-world
python3 hello.py
```

看到下面这行，就说明解释器和教材都正常：

```text
Hello, World!
```

## 目录

| 章 | 主题 | 状态 |
|---:|------|:----:|
| [00](00-hello-world/README.md) | Hello, World!：解释器、函数、模块入口 | ✅ |
| [01](01-objects-names-types/README.md) | 对象、名字与类型 | ✅ |
| [02](02-expressions/README.md) | 表达式、运算符与求值 | ✅ |
| [03](03-control-flow/README.md) | 控制流与模式匹配 | ✅ |
| [04](04-functions/README.md) | 函数、作用域与闭包 | ✅ |
| [05](05-containers-iteration/README.md) | 容器、迭代与生成器 | ✅ |
| [06](06-strings-text/README.md) | 字符串、字节与编码 | ✅ |
| [07](07-classes/README.md) | 类与对象模型 | ✅ |
| [08](08-modules-packages/README.md) | 模块、包与导入 | ✅ |
| [09](09-exceptions/README.md) | 异常与上下文管理器 | ✅ |
| [10](10-typing/README.md) | 类型注解与协议 | ✅ |
| [11](11-capstone/README.md) | 综合练习：小型表达式求值器 | ✅ |
| [附录 A](APPENDIX.md) | Python 3.10–3.14 与异步速览 | ✅ |

## 约定

- 以 **Python 3.12** 为基线；3.10、3.11、3.13、3.14 的差异会单独标注。
- 只用标准库；不依赖第三方框架。
- 代码风格：4 空格缩进，模块/函数/类名遵循 PEP 8，类型注解从第 10 章开始系统使用。
- 所有示例都可以直接运行；第 8 章是多文件包。
- “实现细节”“语言保证”“未定义行为”是三个不同的层次，教材会尽量区分。Python 没有 C 那种 UB，但仍有实现细节、版本差异和未指定行为。
- 代码块里的 `python3` 指代你选择的 3.12+ 解释器。

## 仓库结构

```text
python-bible/
├── README.md
├── Makefile
├── .gitignore
├── LICENSE
├── 00-hello-world/
├── 01-objects-names-types/
├── 02-expressions/
├── 03-control-flow/
├── 04-functions/
├── 05-containers-iteration/
├── 06-strings-text/
├── 07-classes/
├── 08-modules-packages/
├── 09-exceptions/
├── 10-typing/
├── 11-capstone/
└── APPENDIX.md
```

每个章节目录都包含一份 `README.md` 课文和可运行的 `.py` 源码；第 8 章还包含一个 `shapes/` 包，用来演示多文件导入。

## 验证

本仓库在 **CPython 3.12.16** 下用以下配置验证过：

```sh
make check PYTHON=python3.12
```

它会：

- 删除所有 `__pycache__`；
- 用 `-W error` 执行 `compileall`；
- 用 `-W error` 依次运行全部 13 个程序。

`-W error` 把警告变成错误，避免示例在未来的 Python 版本里悄悄产生 `DeprecationWarning` 或 `SyntaxWarning`。

## 范围

这套教材覆盖 Python 3.12 的核心语言：

- 对象、名字、类型、身份、可变性、哈希；
- 表达式、真值、短路、赋值、解包、求值顺序；
- 控制流、循环 `else`、`match` 结构化模式匹配；
- 函数、参数、作用域、闭包、递归、装饰器；
- 容器、推导式、迭代协议、生成器；
- 字符串、Unicode、bytes、编码；
- 类、特殊方法、属性、继承、MRO、dataclass；
- 模块、包、导入系统；
- 异常、异常链、异常组、上下文管理器；
- 类型注解、泛型、Protocol、TypedDict；
- 一个递归下降表达式求值器。

附录补充 Python 3.10–3.14 的语言/实现变化，以及 `async`/`await` 与 `asyncio` 的速览。

它不展开完整标准库、Web 框架、数据库、打包发布、性能调优、CPython C API 和 GIL 的全部细节。教材的目标是让你读懂语言本身，而不是背完所有库。

## 许可

本仓库采用 [MIT License](LICENSE)。课文与代码均可按 MIT 条款使用、修改和分发。
