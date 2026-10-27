#!/usr/bin/env python3
"""
============================================================================
 Python 语言圣经 · 第 3 章
 控制流
============================================================================

 本文件观察：

    1. if / elif / else 与真值
    2. while 与 for
    3. break / continue / 循环 else
    4. match 结构化模式匹配（3.10）
    5. while True + break

 运行：
     python3 control.py

============================================================================
"""


def show_if() -> None:
    print("== if ==")

    value = 42
    if value > 0:
        print("positive")
    elif value < 0:
        print("negative")
    else:
        print("zero")

    for item in [0, 1, "", "x", [], [0], None]:
        if item:
            print(f"{item!r:>5} is truthy")
        else:
            print(f"{item!r:>5} is falsy")


def show_while() -> None:
    print("\n== while ==")

    count = 3
    while count > 0:
        print("count =", count)
        count -= 1

    # Python 没有 do-while；用 while True + break 表达“至少执行一次”。
    attempts = 0
    while True:
        attempts += 1
        print("attempt", attempts)
        if attempts >= 2:
            break


def show_for() -> None:
    print("\n== for ==")

    for value in range(3):
        print("range(3):", value)

    for value in range(2, 8, 2):
        print("range(2, 8, 2):", value)

    for index, value in enumerate(["a", "b", "c"]):
        print(index, value)

    for character in "Py":
        print("character:", character)

    for key, value in {"x": 1, "y": 2}.items():
        print("item:", key, value)


def show_break_continue() -> None:
    print("\n== break / continue ==")

    for value in range(10):
        if value == 2:
            continue
        if value == 5:
            break
        print("value =", value)


def show_loop_else() -> None:
    print("\n== loop else ==")

    for value in [1, 3, 5, 7]:
        if value % 2 == 0:
            print("found even:", value)
            break
    else:
        print("no even number")

    for value in [1, 2, 3]:
        if value == 2:
            print("found 2")
            break
    else:
        print("no 2")


def show_match() -> None:
    print("\n== match ==")

    command = "add"
    match command:
        case "add" | "plus":
            print("command: add")
        case "quit":
            print("command: quit")
        case _:
            print("unknown command")

    values = [1, 2]
    match values:
        case []:
            print("empty list")
        case [x]:
            print("one item:", x)
        case [x, y] if x == y:
            print("two equal items:", x)
        case [x, y]:
            print("two items:", x, y)
        case _:
            print("other list")

    payload = {"type": "circle", "radius": 2.0}
    match payload:
        case {"type": "circle", "radius": radius}:
            print("circle radius:", radius)
        case {"type": "rectangle", "width": width, "height": height}:
            print("rectangle:", width, "x", height)
        case _:
            print("unknown payload")

    match 3.5:
        case int() | float() as number:
            print("number:", number)
        case _:
            print("not a number")


def show_pass() -> None:
    print("\n== pass ==")

    if True:
        pass  # 语法上需要一个块，但暂时什么都不做
    print("pass is a no-op")


def main() -> None:
    show_if()
    show_while()
    show_for()
    show_break_continue()
    show_loop_else()
    show_match()
    show_pass()


if __name__ == "__main__":
    main()
