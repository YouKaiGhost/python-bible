#!/usr/bin/env python3
"""
============================================================================
 Python 语言圣经 · 第 2 章
 表达式、运算符与求值
============================================================================

 本文件观察：

    1. 算术、比较、逻辑、位运算
    2. 真值与短路
    3. == 与 is
    4. 赋值、增强赋值与海象运算符
    5. 解包与求值顺序

 运行：
     python3 expressions.py

============================================================================
"""

import math


def trace(label: str, value: int) -> int:
    print(f"[{label}]", end=" ")
    return value


def show_arithmetic() -> None:
    print("== arithmetic ==")

    a = 7
    b = 3

    print("a + b  =", a + b)
    print("a - b  =", a - b)
    print("a * b  =", a * b)
    print("a / b  =", a / b)
    print("a // b =", a // b)
    print("a % b  =", a % b)
    print("a ** b =", a ** b)
    print("divmod(7, 3) =", divmod(7, 3))

    print("-7 // 3 =", -7 // 3)
    print("-7 % 3  =", -7 % 3)

    print("2 ** 100 =", 2**100)
    print("0.1 + 0.2 =", 0.1 + 0.2)
    print("isclose(0.1 + 0.2, 0.3) =", math.isclose(0.1 + 0.2, 0.3))


def show_truthiness() -> None:
    print("\n== truthiness ==")

    values = [0, 1, -1, 0.0, 0.1, "", "0", [], [0], {}, set(), None, False]
    for value in values:
        print(f"{value!r:>8} -> {bool(value)}")

    print("not 0      =", not 0)
    print("not [1]    =", not [1])
    print("0 or 42    =", 0 or 42)
    print("42 or 0    =", 42 or 0)
    print("0 and 42   =", 0 and 42)
    print("42 and 0   =", 42 and 0)


def show_short_circuit() -> None:
    print("\n== short circuit ==")

    def side_effect(label: str, value: bool) -> bool:
        print(f"[{label}]", end=" ")
        return value

    result1 = False and side_effect("right of and", True)
    result2 = True or side_effect("right of or", False)

    print()
    print("False and ... =", result1)
    print("True or ...   =", result2)


def show_comparisons() -> None:
    print("\n== comparisons ==")

    print("1 < 2 < 3       =", 1 < 2 < 3)
    print("1 < 2 > 3       =", 1 < 2 > 3)
    print("1 == 1.0        =", 1 == 1.0)
    one = 1
    one_float = 1.0
    print("one is one_float=", one is one_float)

    first = [1, 2]
    second = [1, 2]
    third = first

    print("first == second :", first == second)
    print("first is second :", first is second)
    print("first is third  :", first is third)

    # 链式比较的中间表达式只求值一次。
    print("chain: 1 < middle() < 10 =", 1 < trace("middle", 5) < 10)
    print()

    print("'a' in 'cat'     =", "a" in "cat")
    print("'z' not in 'cat' =", "z" not in "cat")
    print("3 in [1, 2, 3]   =", 3 in [1, 2, 3])


def show_bitwise() -> None:
    print("\n== bitwise ==")

    x = 0x0F
    y = 0x3C

    print("x       =", hex(x))
    print("y       =", hex(y))
    print("x & y   =", hex(x & y))
    print("x | y   =", hex(x | y))
    print("x ^ y   =", hex(x ^ y))
    print("~x      =", hex(~x))
    print("x << 2  =", hex(x << 2))
    print("y >> 2  =", hex(y >> 2))


def show_assignment() -> None:
    print("\n== assignment ==")

    values = [1, 2]
    alias = values
    values += [3]
    print("after +=: values =", values, ", alias =", alias)

    values = [1, 2]
    alias = values
    values = values + [3]
    print("after + : values =", values, ", alias =", alias)

    # 海象运算符（3.8）：在表达式内部绑定一个名字。
    data = [1, 2, 3, 4, 5]
    if (size := len(data)) > 3:
        print("walrus: size =", size)

    index = 0
    while (current := data[index]) < 4:
        print("walrus while:", current)
        index += 1


def show_conditional() -> None:
    print("\n== conditional expression ==")

    a = 12
    b = 30
    print("max =", a if a > b else b)

    value = None
    print("fallback =", value if value is not None else "default")


def show_unpacking() -> None:
    print("\n== unpacking ==")

    first, second = [1, 2]
    print("first, second =", first, second)

    head, *tail = [1, 2, 3, 4]
    print("head =", head, ", tail =", tail)

    *init, last = [1, 2, 3, 4]
    print("init =", init, ", last =", last)

    a, b = 1, 2
    a, b = b, a  # 右边先求值，再同时赋值
    print("after swap: a =", a, ", b =", b)

    mapping = {"x": 10, "y": 20}
    print("dict unpack:", {**mapping, "z": 30})


def show_evaluation_order() -> None:
    print("\n== evaluation order ==")

    result = trace("left", 1) + trace("right", 2)
    print()
    print("result =", result)

    # Python 的表达式通常从左到右求值。
    # 赋值语句先求右侧，再把结果绑定到左侧名字。
    value = trace("rhs", 7)
    print()
    print("value =", value)


def main() -> None:
    show_arithmetic()
    show_truthiness()
    show_short_circuit()
    show_comparisons()
    show_bitwise()
    show_assignment()
    show_conditional()
    show_unpacking()
    show_evaluation_order()


if __name__ == "__main__":
    main()
