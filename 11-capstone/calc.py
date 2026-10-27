#!/usr/bin/env python3
"""
============================================================================
 Python 语言圣经 · 第 11 章
 综合练习：一个小型表达式求值器
============================================================================

 语法：

     expression := term (("+" | "-") term)*
     term       := factor (("*" | "/") factor)*
     factor     := number | "(" expression ")" | "-" factor | "+" factor
     number     := digit+ ("." digit*)? | "." digit+

 支持：
     + - * /、括号、一元正负号、十进制小数、空白

 不支持：
     变量、函数、指数记法、隐式乘法

 运行：
     python3 calc.py
     python3 calc.py "1 + 2 * 3"

============================================================================
"""

from dataclasses import dataclass
from enum import Enum, auto
import sys


class TokenKind(Enum):
    NUMBER = auto()
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    END = auto()


@dataclass(frozen=True)
class Token:
    kind: TokenKind
    value: float | None
    position: int


class ParseError(Exception):
    def __init__(self, message: str, position: int) -> None:
        super().__init__(message)
        self.message = message
        self.position = position


class Lexer:
    def __init__(self, text: str) -> None:
        self.text = text
        self.position = 0

    def next_token(self) -> Token:
        self._skip_space()

        if self.position >= len(self.text):
            return Token(TokenKind.END, None, self.position)

        start = self.position
        character = self.text[self.position]
        self.position += 1

        match character:
            case "+":
                return Token(TokenKind.PLUS, None, start)
            case "-":
                return Token(TokenKind.MINUS, None, start)
            case "*":
                return Token(TokenKind.STAR, None, start)
            case "/":
                return Token(TokenKind.SLASH, None, start)
            case "(":
                return Token(TokenKind.LEFT_PAREN, None, start)
            case ")":
                return Token(TokenKind.RIGHT_PAREN, None, start)
            case _:
                if character.isdigit() or (
                    character == "."
                    and self.position < len(self.text)
                    and self.text[self.position].isdigit()
                ):
                    self.position = start
                    return self._number()
                raise ParseError(f"unexpected character {character!r}", start)

    def _skip_space(self) -> None:
        while self.position < len(self.text) and self.text[self.position].isspace():
            self.position += 1

    def _number(self) -> Token:
        start = self.position
        has_digit = False

        while self.position < len(self.text) and self.text[self.position].isdigit():
            has_digit = True
            self.position += 1

        if self.position < len(self.text) and self.text[self.position] == ".":
            self.position += 1
            while self.position < len(self.text) and self.text[self.position].isdigit():
                has_digit = True
                self.position += 1

        if not has_digit:
            raise ParseError("invalid number", start)

        text = self.text[start:self.position]
        try:
            value = float(text)
        except ValueError as error:
            raise ParseError(f"invalid number {text!r}", start) from error

        return Token(TokenKind.NUMBER, value, start)


class Parser:
    def __init__(self, text: str) -> None:
        self.lexer = Lexer(text)
        self.current = self.lexer.next_token()

    def parse(self) -> float:
        value = self._expression()

        if self.current.kind is not TokenKind.END:
            raise ParseError("unexpected token", self.current.position)

        return value

    def _advance(self) -> None:
        self.current = self.lexer.next_token()

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

    def _factor(self) -> float:
        if self.current.kind is TokenKind.PLUS:
            self._advance()
            return self._factor()

        if self.current.kind is TokenKind.MINUS:
            self._advance()
            return -self._factor()

        return self._primary()

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


def evaluate(text: str) -> float:
    return Parser(text).parse()


def format_number(value: float) -> str:
    return f"{value:.12g}"


def report(text: str) -> None:
    try:
        value = evaluate(text)
    except ParseError as error:
        print(f"{text} = error: {error.message} at offset {error.position}")
        print(f"  {text}")
        print(f"  {' ' * error.position}^")
    else:
        print(f"{text} = {format_number(value)}")


def main(arguments: list[str]) -> int:
    samples = [
        "1 + 2 * 3",
        "(1 + 2) * 3",
        "10 / 4",
        "-3 + 5",
        "2 * (3 + 4) - 5",
        "0.1 + 0.2",
        "1 / 0",
        "2 +",
    ]

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
