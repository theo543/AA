from dataclasses import dataclass
from argparse import ArgumentParser
from json import loads
from math import ceil, log2
from random import Random
from itertools import accumulate
from typing import Any

@dataclass
class Configuration:
    population_size: int
    domain_start: float
    domain_end: float
    polynomial_terms: list[tuple[int, float]]
    decimal_precision: int
    crossover_chance: float
    mutation_chance: float
    generations: int
    random_seed: int

    def __post_init__(self):
        assert self.population_size > 0
        assert self.domain_end > self.domain_start
        self.polynomial_terms = [(term[0], term[1]) for term in self.polynomial_terms]
        assert self.decimal_precision >= 0
        assert 1 >= self.crossover_chance >= 0
        assert 1 >= self.mutation_chance >= 0
        assert self.generations > 0

def parse_args() -> Configuration:
    ap = ArgumentParser("genetics-polynomial-max")
    ap.add_argument("config_JSON_path", type=str, default="genetic_polynomial_max.json", nargs='?')
    config: str = ap.parse_args().config_JSON_path
    with open(config, "r") as f:
        return Configuration(**loads(f.read()))

class Polynomial:
    _terms: list[tuple[int, float]]
    def __init__(self, terms):
        self._terms = terms
    def eval(self, x):
        return sum(pow(x, term[0]) * term[1] for term in self._terms)

class Discretize:
    _steps: list[float]
    def __init__(self, begin: float, end: float, precision: float):
        bits = ceil(log2(end - begin) * (10 ** precision))
        step = (end - begin) / (2 ** bits)
        self._bits = bits
        self._steps = [step * (i + 1) for i in range(2 ** bits)]
    def encode(self, nr: float) -> str:
        index = search(nr, self.intervals)
        return f"{index:0{self._bits}b}"
    def decode(self, bits: str) -> float:
        index = int(bits, 2)
        return self.intervals[index]

@dataclass
class Chromosome:
    value: float
    encoded: str

def mutate(c: Chromosome, rng: Random, d: Discretize) -> Chromosome:
    bits = c.encoded
    bit = rng.randint(0, len(bits) - 1)
    mutated = str(bits)
    match bits[bit]:
        case '1':
            mutated[bit] = '0'
        case '0':
            mutated[bit] = '1'
        case _:
            raise ValueError(f"'bits' contains a value that's not 0 or 1 at index {bit}: {bits[bit]}")
    return d.decode(mutated)

def crossover(a: Chromosome, b: Chromosome, rng: Random, d: Discretize) -> tuple[Chromosome, Chromosome]:
    bits_a = a
    bits_b = b
    assert len(bits_a) == len(bits_b)
    cut = rng.randint(0, len(bits_a))
    new_a = bits_a[:cut] + bits_b[cut:]
    new_b = bits_b[:cut] + bits_a[cut:]
    return d.decode(new_a), d.decode(new_b)

def select_intervals(p: Polynomial, population: list[Chromosome]) -> list[int]:
    fitness = [p.eval(x.value) for x in population]
    least_fitness = min(fitness)
    if least_fitness < 0:
        fitness = [f + (-least_fitness) for f in fitness]
    steps = list(accumulate(fitness))
    total_fitness = steps[-1]
    prob = [step / total_fitness for step in steps]
    return prob

def select_with_intervals(population: list[Chromosome], rng: Random) -> list[Chromosome]:
    return [search(rng.random(), population) for _ in range(len(population))]

def search(item: Any, lst: list):
    if item > lst[-1]:
        raise ValueError("'item' is greater than all list elements.")
    l = 0
    r = len(lst) - 1
    while l < r:
        m = (l + r) // 2
        if item <= lst[m]:
            r = m
        elif item > lst[m]:
            l = m + 1
    return l

def main():
    cfg = parse_args()
    print(cfg)
    poly = Polynomial(cfg.polynomial_terms)
    d = Discretize(cfg.domain_start, cfg.domain_end, cfg.decimal_precision)
    rng = Random(cfg.random_seed)
    #TODO

if __name__ == "__main__":
    main()
