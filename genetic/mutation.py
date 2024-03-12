def mutate(chromosome: str, locations: list[int]) -> str:
    chromosome = list(chromosome)
    for x in locations:
#        assert chromosome[x] in ['0', '1']
        chromosome[x] = '1' if chromosome[x] == '0' else '0'
    return ''.join(chromosome)

def read_line() -> list[int]:
    return [int(token) for token in input().split()]

def main():
    [length, changes] = read_line()
    chromosome = input()
#    assert length == len(chromosome)
    locations = read_line()
#    assert changes == len(locations)
    print(mutate(chromosome, locations))

if __name__ == "__main__":
    main()
