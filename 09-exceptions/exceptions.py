#!/usr/bin/env python3
"""
============================================================================
 Python 语言圣经 · 第 9 章
 异常与上下文管理器
============================================================================

 本文件观察：

    1. try / except / else / finally
    2. 自定义异常、异常链 raise ... from ...
    3. ExceptionGroup 与 except*（3.11）
    4. with、__enter__/__exit__
    5. contextlib.contextmanager / suppress

 运行：
     python3 exceptions.py

============================================================================
"""

from collections.abc import Iterator
from contextlib import contextmanager, suppress


class ValidationError(ValueError):
    """表示输入校验失败。"""

    def __init__(self, field: str, message: str) -> None:
        super().__init__(f"{field}: {message}")
        self.field = field
        self.message = message


def parse_positive(text: str) -> int:
    try:
        value = int(text)
    except ValueError as error:
        raise ValidationError("number", f"{text!r} is not an integer") from error

    if value <= 0:
        raise ValidationError("number", "value must be positive")

    return value


def validate_all(values: list[str]) -> None:
    errors: list[ValidationError] = []

    for text in values:
        try:
            parse_positive(text)
        except ValidationError as error:
            errors.append(error)

    if errors:
        raise ExceptionGroup("validation failed", errors)


class Resource:
    def __init__(self, name: str) -> None:
        self.name = name

    def __enter__(self) -> "Resource":
        print(f"enter {self.name}")
        return self

    def __exit__(self, exc_type, exc, traceback) -> bool:
        if exc_type is None:
            print(f"exit {self.name}: no exception")
        else:
            print(f"exit {self.name}: {exc_type.__name__}: {exc}")
        return False


@contextmanager
def section(name: str) -> Iterator[None]:
    print(f"<{name}>")
    try:
        yield
    finally:
        print(f"</{name}>")


def show_try() -> None:
    print("== try / except ==")

    for text in ["5", "x", "-2"]:
        try:
            value = parse_positive(text)
        except ValidationError as error:
            print(f"{text!r}: {error}")
        else:
            print(f"{text!r}: ok, value = {value}")
        finally:
            print(f"{text!r}: finally")


def show_chaining() -> None:
    print("\n== exception chaining ==")

    try:
        parse_positive("abc")
    except ValidationError as error:
        print("caught:", error)
        print("cause:", type(error.__cause__).__name__, error.__cause__)
        print("context:", type(error.__context__).__name__)


def show_group() -> None:
    print("\n== exception group ==")

    try:
        validate_all(["1", "bad", "-3"])
    except* ValidationError as group:
        print("group message:", group.message)
        for error in group.exceptions:
            print("  -", error)


def show_context_manager() -> None:
    print("\n== context manager ==")

    with Resource("database") as resource:
        print("inside", resource.name)

    try:
        with Resource("transaction"):
            raise RuntimeError("boom")
    except RuntimeError as error:
        print("caught outside:", error)

    with section("chapter"):
        print("inside section")

    with suppress(ZeroDivisionError):
        print(1 / 0)
    print("after suppress: still running")


def show_assert() -> None:
    print("\n== assert ==")

    value = 10
    assert value > 0, "value must be positive"
    print("assert passed")

    # assert 是调试工具，不是输入校验：
    # python -O 会移除 assert 语句。


def main() -> None:
    show_try()
    show_chaining()
    show_group()
    show_context_manager()
    show_assert()


if __name__ == "__main__":
    main()
