from math import ceil, log2

def main():
    [a, b] = input().split()
    [a, b] = [float(a), float(b)]
    precision = int(input())
    queries = int(input())
    bits = ceil(log2((b - a) * (10 ** precision)))
    d = (b - a) / (2 ** bits)
    intervals = [(a + i * d, a + (i + 1) * d) for i in range(2 ** bits)]
    for _ in range(queries):
        command = input()
        if command == "TO":
            nr = float(input())
            index = search(nr, intervals)
            print(format(index, f"0{bits}b"))
        elif command == "FROM":
            nr = input()
            index = int(nr, 2)
            interval = intervals[index]
            print(interval[0])
        else:
            raise Exception("Invalid command")

def search(elem, intervals):
    l = 0
    r = len(intervals) - 1
    while l < r:
        m = (l + r) // 2
        if elem < intervals[m][0]:
            r = m
        elif elem >= intervals[m][1]:
            l = m + 1
        else:
            return m
    return l

if __name__ == "__main__":
    main()