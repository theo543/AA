def mutate(chromosome: str, locations: list[int]) -> str:
    bits = list(chromosome)
    for x in locations:
#        assert chromosome[x] in ['0', '1']
        bits[x] = '1' if bits[x] == '0' else '0'
    return ''.join(bits)

def read_line() -> list[int]:
    return [int(token) for token in input().split()]

def main():
    [_length, _changes] = read_line()
    chromosome = input()
#    assert length == len(chromosome)
    locations = read_line()
#    assert changes == len(locations)
    print(mutate(chromosome, locations))

if __name__ == "__main__":
    main()
