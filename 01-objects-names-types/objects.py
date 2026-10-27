#!/usr/bin/env python3
"""
============================================================================
 Python 语言圣经 · 第 1 章
 对象、名字与类型
============================================================================

 本文件回答五个问题：

    1. Python 的“对象”是什么？
    2. 名字和对象是什么关系？
    3. == 和 is 差在哪里？
    4. 可变对象与不可变对象有什么区别？
    5. 浅拷贝和深拷贝差在哪里？

 运行：
     python3 objects.py

============================================================================
"""

from copy import deepcopy
import sys


def show_identity() -> None:
    print("== identity / equality ==")

    original = [1, 2, 3]
    alias = original
    independent = original.copy()

    print("original       :", original)
    print("alias is original      :", alias is original)
    print("independent is original:", independent is original)
    print("independent == original:", independent == original)

    alias.append(4)
    print("after alias.append(4):")
    print("  original   =", original)
    print("  independent=", independent)

    print("id(original)   =", id(original))
    print("id(alias)      =", id(alias))
    print("id(independent)=", id(independent))

    # id 是对象在本次运行中的身份标识，不保证跨进程、跨版本稳定。
    # 不要把 id 当作持久化的对象 ID。


def show_types() -> None:
    print("\n== types ==")

    values = [42, 3.14, True, "text", b"bytes", None, [1], (1,), {"a": 1}]
    for value in values:
        print(f"{value!r:>12} -> {type(value).__name__}")

    print("type(True) is bool      :", type(True) is bool)
    print("isinstance(True, int)   :", isinstance(True, int))
    print("issubclass(bool, int)   :", issubclass(bool, int))
    print("type(1) is type(True)   :", type(1) is type(True))


def show_mutability() -> None:
    print("\n== mutability ==")

    numbers = [1, 2, 3]
    numbers.append(4)
    numbers[0] = 10
    print("list after mutation:", numbers)

    text = "hello"
    upper = text.upper()
    print("str is immutable: text =", text, ", upper =", upper)

    pair = (1, [2, 3])
    pair[1].append(4)
    print("tuple itself is immutable, nested list can change:", pair)

    try:
        pair[0] = 99
    except TypeError as error:
        print("pair[0] = 99 ->", type(error).__name__, error)


def show_names() -> None:
    print("\n== names ==")

    value = [1, 2]
    other = value
    value = [3, 4]
    print("rebinding value does not change other:", value, other)

    del value
    print("after del value, 'value' in locals():", "value" in locals())

    x = 1
    y = x
    x = 2
    print("x =", x, ", y =", y)

    # 名字只是绑定；赋值不会复制对象，除非右侧表达式本身创建了新对象。
    print("None is None:", None is None)


def show_hashability() -> None:
    print("\n== hashability ==")

    print("hash(42)      =", hash(42))
    print("hash('abc')   =", hash("abc"))

    mapping = {"a": 1, "b": 2}
    mapping["c"] = 3
    print("dict:", mapping)
    print("set:", {1, 2, 2, 3})

    try:
        mapping[[1, 2]] = "bad"
    except TypeError as error:
        print("list as dict key ->", type(error).__name__, error)


def show_copy() -> None:
    print("\n== shallow / deep copy ==")

    original = [[1, 2], [3, 4]]
    shallow = original.copy()
    deep = deepcopy(original)

    original[0].append(99)
    print("original:", original)
    print("shallow :", shallow)
    print("deep    :", deep)

    print("shallow[0] is original[0]:", shallow[0] is original[0])
    print("deep[0] is original[0]   :", deep[0] is original[0])


def show_arguments() -> None:
    print("\n== objects at call boundaries ==")

    def mutate(values: list[int]) -> None:
        values.append(100)

    values = [1, 2, 3]
    mutate(values)
    print("after mutate(values):", values)

    # Python 的“传参”是对象引用的传递，不是值拷贝，也不是 C++ 的引用参数。
    # 函数可以修改传入的可变对象，但重新绑定形参不会影响调用者的名字。
    def rebind(values: list[int]) -> None:
        values = [7, 8, 9]

    rebind(values)
    print("after rebind(values):", values)


def main() -> None:
    print("Python:", sys.version.split()[0])
    show_identity()
    show_types()
    show_mutability()
    show_names()
    show_hashability()
    show_copy()
    show_arguments()


if __name__ == "__main__":
    main()
