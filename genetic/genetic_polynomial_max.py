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
    copy_best_to_new_generation: bool

    def __post_init__(self):
        assert self.population_size >= 2
        assert self.domain_end > self.domain_start
        self.polynomial_terms = [(term[0], term[1]) for term in self.polynomial_terms]
        assert self.decimal_precision >= 0
        assert 1 >= self.crossover_chance >= 0
        assert 1 >= self.mutation_chance >= 0
        assert self.generations >= 1

def parse_args() -> Configuration:
    ap = ArgumentParser("genetics-polynomial-max")
    ap.add_argument("config_JSON_path", type=str, default="genetic_polynomial_max.json", nargs='?')
    config: str = ap.parse_args().config_JSON_path
    with open(config, "r") as f:
        return Configuration(**loads(f.read()))

class Polynomial:
    _terms: list[tuple[int, float]]
    def __init__(self, terms: list[tuple[int, float]]):
        self._terms = terms
    def eval(self, x: float):
        return sum(pow(x, term[0]) * term[1] for term in self._terms)

@dataclass
class Chromosome:
    value: float
    encoded: str

class Discretize:
    _steps: list[float]
    _bits: int
    def __init__(self, begin: float, end: float, precision: float):
        bits = ceil(log2((end - begin) * (10 ** precision)))
        step = (end - begin) / (2 ** bits)
        self._bits = bits
        self._steps = [step * (i + 1) for i in range(2 ** bits)]
    def encode(self, nr: float) -> str:
        index = search(nr, self._steps)
        return f"{index:0{self._bits}b}"
    def decode_float(self, bits: str) -> float:
        index = int(bits, 2)
        return self._steps[index]
    def decode_chromo(self, bits: str) -> Chromosome:
        return Chromosome(self.decode_float(bits), bits)
    def bits(self) -> int:
        return self._bits

def mutate(c: Chromosome, bit_flip_chance: float, rng: Random, d: Discretize) -> Chromosome:
    bits = list(c.encoded)
    for i in range(len(bits)):
        if rng.random() < bit_flip_chance:
            bits[i] = '1' if (bits[i] == '0') else '0'
    return d.decode_chromo(''.join(bits))

def crossover(a: Chromosome, b: Chromosome, rng: Random, d: Discretize) -> tuple[Chromosome, Chromosome]:
    bits_a = a.encoded
    bits_b = b.encoded
    assert len(bits_a) == len(bits_b)
    cut = rng.randint(0, len(bits_a))
    new_a = bits_a[:cut] + bits_b[cut:]
    new_b = bits_b[:cut] + bits_a[cut:]
    return d.decode_chromo(new_a), d.decode_chromo(new_b)

@dataclass
class SelectionData:
    prob: list[float]
    cumulative_prob: list[float]

def select_gen_data(p: Polynomial, population: list[Chromosome]) -> SelectionData:
    fitness = [p.eval(x.value) for x in population]
    least_fitness = min(fitness)
    if least_fitness < 0:
        fitness = [f + (-least_fitness) for f in fitness]
    total_fitness = sum(fitness)
    prob = [f / total_fitness for f in fitness]
    cumulative_prob = list(accumulate(prob))
    return SelectionData(prob, cumulative_prob)

def select_chromosomes(amount_to_select: int, population: list[Chromosome], cumulative_prob: list[float], rng: Random, verbose: bool) -> list[Chromosome]:
    selected: list[Chromosome] = []
    for _ in range(amount_to_select):
        u = rng.random()
        chosen = search(u, cumulative_prob)
        selected.append(population[chosen])
    return selected

def search(item: Any, lst: list[Any]):
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

def generate_population(amount: int, rng: Random, d: Discretize) -> list[Chromosome]:
    bits = d.bits()
    upper = 2 ** bits
    def rand_bits():
        nr = rng.randint(0, upper - 1)
        return f"{nr:0{bits}b}"
    return [d.decode_chromo(rand_bits()) for _ in range(amount)]

def main():
    cfg = parse_args()
    print(cfg)
    poly = Polynomial(cfg.polynomial_terms)
    d = Discretize(cfg.domain_start, cfg.domain_end, cfg.decimal_precision)
    rng = Random(cfg.random_seed)
    population = generate_population(cfg.population_size, rng, d)
    verbose = True #TODO print loads of stuff on first iteration
    #TODO print initial population
    for i in range(cfg.generations):
        print(f"Generation {i + 1}")
        s_data = select_gen_data(poly, population)
        #TODO print prob and cumulative prob
        fitnesses = [poly.eval(c.value) for c in population]
        avg_fitness = sum(fitnesses) / len(fitnesses)
        best_fitness_index = max(range(len(fitnesses)), key=fitnesses.__getitem__)
        best_fitness = fitnesses[best_fitness_index]
        best = population[best_fitness_index]
        print(f"Average fitness: {avg_fitness}")
        print(f"Best fitness: {best_fitness}")
        amount_to_select = len(population)
        if cfg.copy_best_to_new_generation:
            amount_to_select -= 1
        selected = select_chromosomes(amount_to_select, population, s_data.cumulative_prob, rng, verbose)
        to_crossover: list[int] = []
        #TODO print crossover process
        for i in range(len(selected)):
            u = rng.random()
            if u <= cfg.crossover_chance:
                to_crossover.append(i)
        rng.shuffle(to_crossover)
        if len(to_crossover) % 2 == 1:
            to_crossover.pop()
        for i in range(0, len(to_crossover) - 1, 2):
            selected[i], selected[i + 1] = crossover(selected[i], selected[i + 1], rng, d)
        #before_mutation = selected
        selected = [mutate(c, cfg.mutation_chance, rng, d) for c in selected]
        if cfg.copy_best_to_new_generation:
            selected.append(best)
        population = selected
        verbose = False
    #TODO print results as we go, and print final result

if __name__ == "__main__":
    main()
