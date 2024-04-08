"""
Genetic Algorithms homework assignment - maximizing a polynomial.

Usage:

The program is configured via a JSON file, not via arguments or stdin.
The configuration is read from genetic_polynomial_max.json in the current working directory by default.

> python genetics_polynomial_max.py > evolution.txt

It can also be run with a custom configuration file via an argument:

> python genetics_polynomial_max.py path/to/my_config.json > evolution.txt

This program was developed using Python 3.11.3 and has been tested on Windows and Linux.
"""

from dataclasses import dataclass
from argparse import ArgumentParser
from json import loads
from math import ceil, log2, log10
from random import Random
from itertools import accumulate
from textwrap import wrap
from secrets import randbits
from pprint import pprint
from typing import Sequence

@dataclass
class Configuration:
    """
    Configuration deserialized from a JSON file for the genetic algorithm:

    population_size: The number of chromosomes in each generation.
    domain_start: The start of the domain for the polynomial.
    domain_end: The end of the domain for the polynomial.
    polynomial_terms: The terms of the polynomial, as a list of exponent-coefficient tuples (array of arrays in JSON).
    decimal_precision: The decimal places for the fixed precision encoding.
    crossover_chance: Chance of a chromosome being included in crossover.
    mutation_chance: Chance of each bit in a chromosome being flipped.
    generations: The number of generations to run before extracting the final result.
    random_seed: The seed for the RNG, or 0 to get a random seed from the OS.
    verbose_first_generation: Whether to print verbose output for the first generation.
    copy_best_to_new_generation: Whether to add a unchanged copy of the best chromosome to each new generation.
    """
    population_size: int
    domain_start: float
    domain_end: float
    polynomial_terms: list[tuple[int, float]]
    decimal_precision: int
    crossover_chance: float
    mutation_chance: float
    generations: int
    random_seed: int
    verbose_first_generation: bool
    copy_best_to_new_generation: bool

    def __post_init__(self):
        """
        Check for various errors in the configuration.
        Convert from array of arrays to array of tuples for polynomial_terms, since JSON uses arrays.
        """
        assert self.population_size >= 2
        assert self.domain_end > self.domain_start
        self.polynomial_terms = [(term[0], term[1]) for term in self.polynomial_terms]
        assert self.decimal_precision >= 0
        assert 1 >= self.crossover_chance >= 0
        assert 1 >= self.mutation_chance >= 0
        assert self.generations >= 1

def parse_args() -> Configuration:
    """
    Parse the configuration, either from the default file or from a custom location.
    """
    ap = ArgumentParser("python genetics_polynomial_max.py")
    ap.add_argument("config_JSON_path", type=str, default="genetic_polynomial_max.json", nargs='?')
    config: str = ap.parse_args().config_JSON_path
    with open(config, "r", encoding='utf-8') as f:
        return Configuration(**loads(f.read()))

class Polynomial:
    """
    A polynomial function with integer exponents and float coefficients.
    Used as the fitness function for the genetic algorithm.
    """
    _terms: list[tuple[int, float]]
    def __init__(self, terms: list[tuple[int, float]]):
        self._terms = terms
    def eval(self, x: float):
        """
        Evaluate the polynomial at a floating point value x.
        """
        return sum(pow(x, term[0]) * term[1] for term in self._terms)

@dataclass
class Chromosome:
    """
    A fixed precision number encoded as a binary string.
    For convenience, both the value and the encoded string are stored at all times.
    """
    value: float
    encoded: str

class Discretize:
    """
    A class to encode and decode floating point numbers as fixed precision binary strings.
    Creates and stores a list of all possible values in the range [begin, end] with the given precision.
    The precision and interval cannot be too large, since the number of possible values grows exponentially.
    """
    _steps: list[float]
    _bits: int
    def __init__(self, begin: float, end: float, precision: float):
        bits = ceil(log2((end - begin) * (10 ** precision)))
        step = (end - begin) / (2 ** bits)
        self._bits = bits
        self._steps = [step * (i + 1) + begin for i in range(2 ** bits)]
    def encode(self, nr: float) -> str:
        """
        Encode a floating point number as a fixed precision binary string, using the closest value in the list.
        """
        index = search(nr, self._steps)
        return f"{index:0{self._bits}b}"
    def decode_float(self, bits: str) -> float:
        """
        Decode a fixed precision binary string to a floating point number.
        """
        index = int(bits, 2)
        return self._steps[index]
    def decode_chromo(self, bits: str) -> Chromosome:
        """
        Decode a fixed precision binary to a Chromosome dataclass, which keeps both the value and the encoded string.
        """
        return Chromosome(self.decode_float(bits), bits)
    def bits(self) -> int:
        """
        Get the number of bits used to encode the floating point numbers.
        """
        return self._bits

def mutate(c: Chromosome, bit_flip_chance: float, rng: Random, d: Discretize) -> Chromosome:
    """
    Mutate a chromosome by flipping each bit with a given chance.
    """
    def maybe_flip(bit: str) -> str:
        assert bit in ('0', '1')
        if rng.random() < bit_flip_chance:
            return '1' if bit == '0' else '0'
        return bit
    mutated = ''.join(map(maybe_flip, c.encoded))
    return d.decode_chromo(mutated)

def crossover(a: Chromosome, b: Chromosome, rng: Random, d: Discretize) -> tuple[Chromosome, Chromosome, int]:
    """
    Cross two chromosomes by swapping them after a random cut point.
    """
    bits_a = a.encoded
    bits_b = b.encoded
    assert len(bits_a) == len(bits_b)
    cut = rng.randint(0, len(bits_a))
    new_a = bits_a[:cut] + bits_b[cut:]
    new_b = bits_b[:cut] + bits_a[cut:]
    return d.decode_chromo(new_a), d.decode_chromo(new_b), cut

@dataclass
class SelectionData:
    """
    Small dataclass to return both the probabilities and the cumulative probabilities for selection.
    Only needed so that the original list of probabilities can be printed in the first generation verbose output.
    """
    prob: list[float]
    cumulative_prob: list[float]

def select_gen_data(p: Polynomial, population: list[Chromosome]) -> SelectionData:
    """
    Calculate the cumulative probabilities of each chromosome in the population being selected, based on their fitness.
    Used to select chromosomes using the roulette method.
    Also returns the probabilities for verbose output in the first generation.
    """
    fitness = [p.eval(x.value) for x in population]
    least_fitness = min(fitness)
    if least_fitness < 0:
        fitness = [f + (-least_fitness) for f in fitness]
    total_fitness = sum(fitness)
    prob = [f / total_fitness for f in fitness]
    cumulative_prob = list(accumulate(prob))
    # fix rounding errors
    assert 0.99 <= cumulative_prob[-1] <= 1.01
    cumulative_prob[-1] = 1.0
    return SelectionData(prob, cumulative_prob)

def select_chromosomes(amount_to_select: int, population: list[Chromosome], cumulative_prob: list[float], rng: Random, verbose: bool) -> list[Chromosome]:
    """
    Use the roulette method to select chromosomes based on previously calculated cumulative probabilities.
    Separate from select_gen_data to allow the main function to print the probabilities formatted nicely.
    If verbose is True, print the roulette selection process, showing the random number and the selected chromosome.
    """
    selected: list[Chromosome] = []
    for _ in range(amount_to_select):
        u = rng.random()
        chosen = search(u, cumulative_prob)
        selected.append(population[chosen])
        if verbose:
            print(f"u={u}: Select chromosome {chosen}")
    return selected

def search(item: float, lst: list[float]):
    """
    Use efficient binary search to find the greatest index such that item <= lst[index], in a sorted list.
    Used for roulette selection and for chromosome encoding.
    """
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
    """
    Generate a population of random chromosomes, stored as Chromosome dataclasses, evenly distributed in the discretized domain.
    """
    bits = d.bits()
    upper = 2 ** bits
    def rand_bits():
        nr = rng.randint(0, upper - 1)
        return f"{nr:0{bits}b}"
    return [d.decode_chromo(rand_bits()) for _ in range(amount)]

def format_chromosome(c: Chromosome, poly: Polynomial) -> str:
    """
    Format a Chromosome for printing. Cannot be a __str__ method because it needs the polynomial to calculate the fitness.
    """
    return f"(encoded={c.encoded}, value={c.value}, fitness={poly.eval(c.value)})"

def print_list_wrapped(title: str, items: Sequence[object], indent: str = '    '):
    """
    Print a list of items, as a title followed by a list of items, wrapped using textwrap.wrap, with an equal indent on all lines.
    """
    unwrapped = ', '.join(map(str, items))
    lines = wrap(unwrapped, initial_indent=indent, subsequent_indent=indent)
    print(f"{title}: [")
    print('\n'.join(lines))
    print("]")

def main():
    """
    The main function of the program, which runs the genetic algorithm.
    This function is very long, because of the need to print verbose output for the first generation.
    It's hard to split into functions, when there is printing interleaved with everything else.
    """
    cfg = parse_args()
    pprint(cfg)
    poly = Polynomial(cfg.polynomial_terms)
    d = Discretize(cfg.domain_start, cfg.domain_end, cfg.decimal_precision)
    rng = Random(cfg.random_seed if cfg.random_seed != 0 else randbits(64))
    population = generate_population(cfg.population_size, rng, d)
    verbose = cfg.verbose_first_generation
    print("Generation 0 (initial population):")
    idx_pad = ceil(log10(len(population)))
    def pad(index: int) -> str:
        return f"{index + 1: >{idx_pad}}"
    for i, c in enumerate(population):
        print(f"{pad(i)}: {format_chromosome(c, poly)}")
    print()
    for i in range(cfg.generations):
        fitnesses = [poly.eval(c.value) for c in population]
        best_fitness_index = max(range(len(fitnesses)), key=fitnesses.__getitem__)
        best = population[best_fitness_index]
        amount_to_select = len(population)
        print(f"Best chromosome: {format_chromosome(best, poly)}")
        if cfg.copy_best_to_new_generation:
            amount_to_select -= 1

        s_data = select_gen_data(poly, population)
        if verbose:
            print()
            print("Selection probabilities:")
            for i, p in enumerate(s_data.prob):
                print(f"Chromosome {pad(i)}: P={p}")
            print_list_wrapped("Cumulative probabilities", s_data.cumulative_prob)
        selected = select_chromosomes(amount_to_select, population, s_data.cumulative_prob, rng, verbose)
        if verbose:
            print()
            print("Selected chromosomes:")
            for i, c in enumerate(selected):
                print(f"{pad(i)}: {format_chromosome(selected[i], poly)}")

        to_crossover: list[int] = []
        if verbose:
            print()
            print(f"Crossover probability = {cfg.crossover_chance}")
        for index, chromo in enumerate(selected):
            u = rng.random()
            cross = u <= cfg.crossover_chance
            if cross:
                to_crossover.append(index)
            if verbose:
                print(f"{pad(index)}: {chromo.encoded} u={u}", end="")
                print(" | Will crossover" if cross else "")
        rng.shuffle(to_crossover)
        if len(to_crossover) % 2 == 1:
            c = to_crossover.pop()
            if verbose:
                print(f"Removed {c} from crossover list to have an even amount.")

        for i in range(0, len(to_crossover) - 1, 2):
            s = selected
            x, y = to_crossover[i], to_crossover[i + 1]
            orig_x, orig_y = s[x].encoded, s[y].encoded
            s[x], s[y], cut = crossover(s[x], s[y], rng, d)
            def print_with_cut(s: str, index: int, cut: int):
                with_cut = s[:cut] + '|' + s[cut:]
                print(f"  {pad(index)}: {with_cut}")
            if verbose:
                print(f"Crossing {x} and {y} at cut point {cut}:")
                print(" Before:")
                print_with_cut(orig_x, x, cut)
                print_with_cut(orig_y, y, cut)
                print(" After:")
                print_with_cut(s[x].encoded, x, cut)
                print_with_cut(s[y].encoded, y, cut)

        if verbose:
            print()
            print("After crossover:")
            for i, c in enumerate(selected):
                print(f"{pad(i)}: {format_chromosome(c, poly)}")

            print()
            print(f"Mutation probability = {cfg.mutation_chance}")
        before_mutation = [c.encoded for c in selected]
        selected = [mutate(c, cfg.mutation_chance, rng, d) for c in selected]
        diff = [i for i in range(len(selected)) if before_mutation[i] != selected[i].encoded]
        if verbose:
            print_list_wrapped("Changed chromosomes", diff)
            print("Chromosomes after mutation:")
            for i, c in enumerate(selected):
                print(f"{pad(i)}: {format_chromosome(c, poly)}")
            print()
        if cfg.copy_best_to_new_generation:
            selected.append(best)
            if verbose:
                print(f"Added saved copy of best chromosome: {format_chromosome(best, poly)}")
        population = selected
        if verbose:
            verbose = False
            print()
            print("Further generations will only print the best chromosome.")

    final_best = max(population, key=lambda c: poly.eval(c.value))
    print()
    print(f"Best chromosome after {cfg.generations} generations: {format_chromosome(final_best, poly)}")

if __name__ == "__main__":
    main()
