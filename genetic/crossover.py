def cross(chromosome_a: str, chromosome_b: str, cut_point: int) -> tuple[str, str]:
    assert len(chromosome_a) == len(chromosome_b)
    new_c_a = chromosome_a[:cut_point] + chromosome_b[cut_point:]
    new_c_b = chromosome_b[:cut_point] + chromosome_a[cut_point:]
    return new_c_a, new_c_b

def main():
    length = int(input())
    chromosome_a = input()
    chromosome_b = input()
    assert length == len(chromosome_a) == len(chromosome_b)
    cut_point = int(input())
    (new_c_a, new_c_b) = cross(chromosome_a, chromosome_b, cut_point)
    print(new_c_a)
    print(new_c_b)

if __name__ == "__main__":
    main()
