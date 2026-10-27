#!/usr/bin/env python3
"""
============================================================================
 Python 语言圣经 · 第 6 章
 字符串、字节与编码
============================================================================

 本文件观察：

    1. str 是 Unicode 码点序列
    2. 字符串字面量、原始字符串、三引号
    3. 常用方法与 f-string 格式化
    4. bytes 与 str 的边界
    5. UTF-8 编解码与常见错误

 运行：
     python3 strings.py

============================================================================
"""

import unicodedata


def show_unicode() -> None:
    print("== unicode ==")

    text = "Python 语言"
    print("text:", text)
    print("len:", len(text))
    print("first:", text[0])
    print("last:", text[-1])
    print("slice:", text[7:])
    print("ord('A'):", ord("A"), ", chr(65):", chr(65))

    # 一个 Unicode 码点不等于一个“用户看到的字符”。
    composed = "\u00e9"          # é
    decomposed = "e\u0301"       # e + 组合重音
    print("composed len:", len(composed), ", decomposed len:", len(decomposed))
    print("equal before normalize:", composed == decomposed)
    print("equal after NFC      :",
          unicodedata.normalize("NFC", composed) ==
          unicodedata.normalize("NFC", decomposed))


def show_literals() -> None:
    print("\n== literals ==")

    single = 'hello'
    double = "world"
    triple = """line one
line two"""
    raw = r"C:\code\python"
    name = "Ada"
    formatted = f"{name}, welcome to Python {3 + 1}"

    print("single:", single)
    print("double:", double)
    print("triple:", triple)
    print("raw:", raw)
    print("f-string:", formatted)

    print("escape:", "tab\tnewline\nbackslash\\quote\"")
    print("adjacent:", "Hello, " "World!")


def show_methods() -> None:
    print("\n== methods ==")

    text = "  Hello, Python!  "
    print("strip:", text.strip())
    print("lower:", text.lower())
    print("upper:", text.upper())
    print("casefold:", "Straße".casefold())
    print("replace:", text.replace("Python", "World"))
    print("find:", text.find("Python"))
    print("startswith:", text.strip().startswith("Hello"))
    print("split:", "a,b,c".split(","))
    print("rsplit:", "a,b,c".rsplit(",", 1))
    print("partition:", "key=value".partition("="))
    print("join:", "-".join(["a", "b", "c"]))
    print("zfill:", "42".zfill(5))
    print("center:", "hi".center(8, "*"))
    print("count:", "banana".count("an"))


def show_formatting() -> None:
    print("\n== formatting ==")

    value = 3.1415926
    count = 42
    name = "Ada"

    print(f"{value:.2f}")
    print(f"{value:10.3f}")
    print(f"{count:08d}")
    print(f"{count:#x}")
    print(f"{name:>10}")
    print(f"{name:*^10}")
    print(f"{count=}")
    print("{}, {} and {}".format("a", "b", "c"))
    print("{0}-{1}-{0}".format("x", "y"))
    print("{name} is {age}".format(name="Ada", age=36))


def show_bytes() -> None:
    print("\n== bytes ==")

    text = "你好, Python"
    encoded = text.encode("utf-8")

    print("text:", text)
    print("len(text):", len(text))
    print("encoded:", encoded)
    print("len(encoded):", len(encoded))
    print("bytes per CJK char:", len("你".encode("utf-8")))

    decoded = encoded.decode("utf-8")
    print("decoded:", decoded)
    print("equal:", decoded == text)

    raw = b"hello"
    print("bytes literal:", raw)
    print("raw[0]:", raw[0], ", chr:", chr(raw[0]))
    print("bytearray:", bytearray(b"abc"))

    try:
        b"\xff".decode("utf-8")
    except UnicodeDecodeError as error:
        print("invalid utf-8 ->", type(error).__name__, error.reason)

    print("with replacement:", b"\xff".decode("utf-8", errors="replace"))


def show_repr() -> None:
    print("\n== str vs repr ==")

    text = "line\nbreak"
    print("str  :", text)
    print("repr :", repr(text))
    print("list repr:", repr(["a", "b"]))

    # repr 的目标是让读者看到对象的“可重建表示”；
    # str 的目标是让人读。print 默认使用 str，容器使用 repr。


def show_text_processing() -> None:
    print("\n== text processing ==")

    lines = ["  alpha  ", "", "beta", "  gamma"]
    cleaned = [line.strip() for line in lines if line.strip()]
    print("cleaned:", cleaned)

    words = "the quick brown fox".split()
    print("capitalized:", " ".join(word.capitalize() for word in words))

    table = str.maketrans({"a": "4", "e": "3", "i": "1"})
    print("translate:", "attack the enemy".translate(table))


def main() -> None:
    show_unicode()
    show_literals()
    show_methods()
    show_formatting()
    show_bytes()
    show_repr()
    show_text_processing()


if __name__ == "__main__":
    main()
