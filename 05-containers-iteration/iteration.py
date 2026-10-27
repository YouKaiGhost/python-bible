#!/usr/bin/env python3
"""
============================================================================
 Python 语言圣经 · 第 5 章（附）
 迭代器与生成器
============================================================================

 本文件观察：

    1. iter / next / StopIteration
    2. 生成器函数与 yield
    3. yield from
    4. 生成器表达式与惰性求值
    5. itertools.islice 与无限序列

 运行：
     python3 iteration.py

============================================================================
"""

from itertools import count, islice
from collections.abc import Iterator


def show_iterator_protocol() -> None:
    print("== iterator protocol ==")

    values = [10, 20, 30]
    iterator = iter(values)

    print("type(iterator):", type(iterator).__name__)
    print("next:", next(iterator))
    print("next:", next(iterator))
    print("next:", next(iterator))

    try:
        next(iterator)
    except StopIteration:
        print("StopIteration: exhausted")

    # for 循环只是 iter/next/StopIteration 的语法糖。
    total = 0
    for value in values:
        total += value
    print("for total:", total)


def count_up(limit: int) -> Iterator[int]:
    current = 0
    while current < limit:
        yield current
        current += 1


def show_generators() -> None:
    print("\n== generators ==")

    generator = count_up(4)
    print("type(generator):", type(generator).__name__)
    print("next(generator):", next(generator))
    print("next(generator):", next(generator))

    print("remaining:", list(generator))

    for value in count_up(3):
        print("for generator:", value)


def chain(*iterables: list[int]) -> Iterator[int]:
    for iterable in iterables:
        yield from iterable


def show_yield_from() -> None:
    print("\n== yield from ==")

    combined = chain([1, 2], [3, 4], [5])
    print("chain:", list(combined))


def show_laziness() -> None:
    print("\n== laziness ==")

    def trace(value: int) -> int:
        print("computing", value)
        return value * value

    lazy = (trace(value) for value in range(4))
    print("generator created")
    print("take two:", list(islice(lazy, 2)))
    print("take rest:", list(lazy))

    # 生成器只能遍历一次。
    exhausted = (value for value in [1, 2, 3])
    print("first pass:", list(exhausted))
    print("second pass:", list(exhausted))


def show_infinite() -> None:
    print("\n== infinite generators ==")

    values = islice(count(10, 5), 5)
    print("islice(count(10, 5), 5):", list(values))


def show_callable_iterator() -> None:
    print("\n== iter(callable, sentinel) ==")

    remaining = 3

    def read() -> int:
        nonlocal remaining
        remaining -= 1
        return remaining

    for value in iter(read, 0):
        print("read:", value)


def main() -> None:
    show_iterator_protocol()
    show_generators()
    show_yield_from()
    show_laziness()
    show_infinite()
    show_callable_iterator()


if __name__ == "__main__":
    main()
