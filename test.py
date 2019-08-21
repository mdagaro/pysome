from pysome.funcs import *
from pysome.maybe import *

len_tests = ["b", ["a", "b", "c"], "bbd", {1: 3}, 12, False]
len_tests = [maybe(x) for x in len_tests]


def fprint(func, tests):
    for l in tests:
        print(l.get(), l.comb(func))
    print()


fprint(maybelen, len_tests)

fprint(maybestr, len_tests)

fprint(maybebool, len_tests)


def test(string):
    @maybefunction
    def returnfunc(value):
        return value.count(string)

    return returnfunc


fprint(test("b"), len_tests)
fprint(maybedict, len_tests)
fprint(maybelist, len_tests)
