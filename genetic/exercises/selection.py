from dataclasses import dataclass
from itertools import accumulate

@dataclass
class Coefficients:
    a: float
    b: float
    c: float

def polynomial(c: Coefficients, x: float) -> float:
    return c.a * x**2 + c.b * x + c.c

def selection(c: Coefficients, chromosomes: list[float]) -> list[float]:
    fitness = [polynomial(c, x) for x in chromosomes]
    assert all(x >= 0 for x in fitness)
    interval_ends = [0] + list(accumulate(fitness))
    total_fitness = interval_ends[-1]
    for i in range(len(interval_ends)):
        interval_ends[i] /= total_fitness
    return interval_ends

def read_line() -> list[float]:
    return [float(token) for token in input().split()]

def main():
    c = Coefficients(*read_line())
    size = int(input())
    chromosomes = read_line()
    assert len(chromosomes) == size
    for x in selection(c, chromosomes):
        print(f"{x:.10f}")

if __name__ == "__main__":
    main()
