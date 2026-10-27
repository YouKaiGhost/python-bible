#!/usr/bin/env python3
"""
============================================================================
 Python 语言圣经 · 第 4 章
 函数、作用域与闭包
============================================================================

 本文件观察：

    1. 参数传递的四种形态
    2. 默认值、可变默认参数陷阱
    3. LEGB 作用域、global、nonlocal
    4. 闭包、lambda、延迟绑定
    5. 递归、缓存、装饰器

 运行：
     python3 functions.py

============================================================================
"""

from functools import lru_cache, wraps
from typing import Callable

GLOBAL_COUNTER = 0


def greet(name: str, greeting: str = "Hello") -> str:
    return f"{greeting}, {name}!"


def make_point(x: int, y: int, *, scale: int = 1) -> tuple[int, int]:
    return x * scale, y * scale


def positional_only(x: int, /, y: int) -> int:
    return x + y


def collect(*args: int, **kwargs: str) -> tuple[tuple[int, ...], dict[str, str]]:
    return args, kwargs


def append_bad(value: int, bucket: list[int] = []) -> list[int]:
    bucket.append(value)
    return bucket


def append_good(value: int, bucket: list[int] | None = None) -> list[int]:
    if bucket is None:
        bucket = []
    bucket.append(value)
    return bucket


def make_counter(start: int = 0) -> Callable[[], int]:
    count = start

    def next_value() -> int:
        nonlocal count
        count += 1
        return count

    return next_value


def bump_global() -> int:
    global GLOBAL_COUNTER
    GLOBAL_COUNTER += 1
    return GLOBAL_COUNTER


@lru_cache(maxsize=None)
def fibonacci(n: int) -> int:
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


def logged(function: Callable[..., object]) -> Callable[..., object]:
    @wraps(function)
    def wrapper(*args: object, **kwargs: object) -> object:
        print(f"call {function.__name__}{args}")
        return function(*args, **kwargs)

    return wrapper


def repeat(times: int) -> Callable[[Callable[..., object]], Callable[..., object]]:
    def decorate(function: Callable[..., object]) -> Callable[..., object]:
        @wraps(function)
        def wrapper(*args: object, **kwargs: object) -> object:
            result: object = None
            for _ in range(times):
                result = function(*args, **kwargs)
            return result

        return wrapper

    return decorate


@logged
def add(left: int, right: int) -> int:
    return left + right


@repeat(3)
def say(message: str) -> str:
    print(message)
    return message


def show_parameters() -> None:
    print("== parameters ==")

    print(greet("Ada"))
    print(greet("Ada", greeting="Hi"))
    print(greet(name="Ada", greeting="Hello"))

    print("keyword-only:", make_point(2, 3, scale=10))
    try:
        print(make_point(2, 3, 10))
    except TypeError as error:
        print("make_point(2, 3, 10) ->", type(error).__name__, error)

    print("positional-only:", positional_only(1, 2))
    try:
        print(positional_only(x=1, y=2))
    except TypeError as error:
        print("positional_only(x=1, y=2) ->", type(error).__name__, error)

    print("varargs:", collect(1, 2, 3, name="Ada", role="engineer"))

    values = [1, 2]
    options = {"name": "Ada"}
    print("unpack call:", collect(*values, **options))


def show_mutable_default() -> None:
    print("\n== mutable default ==")

    print("bad first :", append_bad(1))
    print("bad second:", append_bad(2))

    print("good first :", append_good(1))
    print("good second:", append_good(2))


def show_scopes() -> None:
    print("\n== scopes ==")

    value = "global"

    def outer() -> None:
        value = "outer"

        def inner() -> None:
            nonlocal value
            value = "inner"
            print("inner sees:", value)

        inner()
        print("outer sees:", value)

    outer()
    print("module sees:", value)

    counter = make_counter(10)
    print("counter:", counter(), counter(), counter())
    print("global counter:", bump_global(), bump_global())


def show_lambdas() -> None:
    print("\n== lambdas / first-class functions ==")

    square = lambda value: value * value
    print("lambda square(7):", square(7))

    words = ["python", "c", "c++", "rust"]
    print("sorted by length:", sorted(words, key=len))
    print("sorted by last char:", sorted(words, key=lambda word: word[-1]))

    functions = [lambda: index for index in range(3)]
    print("late binding:", [function() for function in functions])

    fixed = [lambda index=index: index for index in range(3)]
    print("default capture:", [function() for function in fixed])


def show_recursion() -> None:
    print("\n== recursion ==")

    def factorial(n: int) -> int:
        return 1 if n <= 1 else n * factorial(n - 1)

    print("factorial(6) =", factorial(6))
    print("fibonacci(20) =", fibonacci(20))
    print("cache info:", fibonacci.cache_info())


def show_decorators() -> None:
    print("\n== decorators ==")

    print("add(2, 3) =", add(2, 3))
    print("add.__name__ =", add.__name__)
    print("say:")
    say("hello")


def main() -> None:
    show_parameters()
    show_mutable_default()
    show_scopes()
    show_lambdas()
    show_recursion()
    show_decorators()


if __name__ == "__main__":
    main()
