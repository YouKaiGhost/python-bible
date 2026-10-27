#!/usr/bin/env python3
"""
============================================================================
 Python 语言圣经 · 第 5 章
 容器与推导式
============================================================================

 本文件观察：

    1. list / tuple / dict / set 的常用操作
    2. 切片、排序、解包
    3. 列表、字典、集合推导式
    4. 浅拷贝与容器嵌套
    5. collections 里的几个常用容器

 运行：
     python3 containers.py

============================================================================
"""

from collections import Counter, defaultdict, deque


def show_lists() -> None:
    print("== lists ==")

    values = [10, 20, 30]
    values.append(40)
    values.extend([50, 60])
    values.insert(1, 15)
    print("values:", values)

    print("values[0]   =", values[0])
    print("values[-1]  =", values[-1])
    print("values[1:4] =", values[1:4])
    print("values[::2] =", values[::2])
    print("reversed    =", values[::-1])

    removed = values.pop()
    print("pop() ->", removed, ", values:", values)
    values.remove(15)
    print("after remove(15):", values)

    numbers = [3, 1, 4, 1, 5]
    print("sorted:", sorted(numbers))
    print("original:", numbers)
    numbers.sort(reverse=True)
    print("in-place sort:", numbers)

    squares = [value * value for value in range(6)]
    print("squares:", squares)
    evens = [value for value in range(10) if value % 2 == 0]
    print("evens:", evens)


def show_tuples() -> None:
    print("\n== tuples ==")

    point = (3, 4)
    x, y = point
    print("point:", point, ", x =", x, ", y =", y)

    single = (42,)
    print("single:", single, ", type:", type(single).__name__)

    nested = (1, (2, 3))
    print("nested[1][0] =", nested[1][0])

    try:
        point[0] = 99
    except TypeError as error:
        print("tuple assignment ->", type(error).__name__, error)


def show_dicts() -> None:
    print("\n== dicts ==")

    scores = {"Ada": 98, "Grace": 95}
    scores["Linus"] = 91
    print("scores:", scores)

    print("Ada:", scores["Ada"])
    print("missing get:", scores.get("missing", 0))
    print("setdefault:", scores.setdefault("Margaret", 99))
    print("scores:", scores)

    print("keys  :", list(scores.keys()))
    print("values:", list(scores.values()))
    print("items :", list(scores.items()))

    extra = {"Alan": 90}
    print("merge:", scores | extra)

    lengths = {name: len(name) for name in scores}
    print("lengths:", lengths)

    # 3.7 起，dict 保证保留插入顺序。
    print("insertion order:", list(scores))


def show_sets() -> None:
    print("\n== sets ==")

    left = {1, 2, 3, 4}
    right = {3, 4, 5, 6}

    print("left | right =", left | right)
    print("left & right =", left & right)
    print("left - right =", left - right)
    print("left ^ right =", left ^ right)

    values = [1, 2, 2, 3, 3, 3]
    print("deduplicate:", set(values))
    print("membership:", 2 in left)


def show_comprehensions() -> None:
    print("\n== comprehensions ==")

    squares = {value: value * value for value in range(5)}
    print("dict comprehension:", squares)

    unique_lengths = {len(word) for word in ["a", "bb", "cc", "ddd"]}
    print("set comprehension:", unique_lengths)

    pairs = [(x, y) for x in range(3) for y in range(2)]
    print("nested comprehension:", pairs)

    matrix = [[1, 2], [3, 4], [5, 6]]
    transpose = [[row[column] for row in matrix] for column in range(2)]
    print("transpose:", transpose)


def show_helpers() -> None:
    print("\n== helpers ==")

    names = ["Ada", "Grace", "Linus"]
    for index, name in enumerate(names, start=1):
        print(index, name)

    scores = [98, 95, 91]
    for name, score in zip(names, scores):
        print(name, score)

    print("sum:", sum(scores))
    print("min/max:", min(scores), max(scores))
    print("any/all:", any(score > 97 for score in scores),
          all(score > 90 for score in scores))


def show_collections() -> None:
    print("\n== collections ==")

    counter = Counter("abracadabra")
    print("Counter:", counter)
    print("most_common(2):", counter.most_common(2))

    grouped: defaultdict[str, list[int]] = defaultdict(list)
    for value in [1, 2, 3, 4, 5, 6]:
        grouped["even" if value % 2 == 0 else "odd"].append(value)
    print("defaultdict:", dict(grouped))

    queue: deque[int] = deque([1, 2, 3])
    queue.append(4)
    queue.appendleft(0)
    print("deque:", queue, ", popleft:", queue.popleft())


def show_aliasing() -> None:
    print("\n== aliasing ==")

    original = [[1, 2], [3, 4]]
    shallow = original.copy()
    original[0].append(99)

    print("original:", original)
    print("shallow :", shallow)
    print("same nested list:", shallow[0] is original[0])


def main() -> None:
    show_lists()
    show_tuples()
    show_dicts()
    show_sets()
    show_comprehensions()
    show_helpers()
    show_collections()
    show_aliasing()


if __name__ == "__main__":
    main()
