import random
import subprocess
import sys
import time

MIN_INTERVAL_BEGIN = -100000
MAX_INTERVAL_END = 100000
MAX_INTERVAL_AMOUNT = 100000

def generate_test_case() -> tuple[int, int, list[tuple[int, int]]]:
    cover_begin = random.randint(MIN_INTERVAL_BEGIN, MIN_INTERVAL_BEGIN + 100)
    cover_end = random.randint(MAX_INTERVAL_END - 100, MAX_INTERVAL_END)
    interval_amount = random.randint(1, MAX_INTERVAL_AMOUNT)
    intervals: list[tuple[int, int]] = []
    for _ in range(interval_amount):
        x = random.randint(MIN_INTERVAL_BEGIN, MAX_INTERVAL_END - 1)
        y = x + round(abs(random.normalvariate(100, 100))) + 1
        y = min(y, MAX_INTERVAL_END)
        intervals.append((x, y))
    return cover_begin, cover_end, intervals

def check_is_possible(cover_begin: int, cover_end: int, intervals: list[tuple[int, int]]) -> bool:
    bools = [False for _ in range(MIN_INTERVAL_BEGIN, MAX_INTERVAL_END + 1)]
    for (left, right) in intervals:
        for i in range(left - MIN_INTERVAL_BEGIN, right - MIN_INTERVAL_BEGIN + 1):
            bools[i] = True
    return all(bools[cover_begin - MIN_INTERVAL_BEGIN:cover_end - MIN_INTERVAL_BEGIN + 1])

def test_program(solver_path: str):
    while True:
        cover_begin, cover_end, intervals = generate_test_case()

        input_string = f"{cover_begin} {cover_end}\n{len(intervals)}\n"
        for interval in intervals:
            input_string += f"{interval[0]} {interval[1]}\n"

        with open("input.txt", "w+", encoding="ascii") as f:
            f.write(input_string)
            f.seek(0)
            start_time = time.perf_counter_ns()
            process = subprocess.run(solver_path, stdin=f, capture_output=True, check=False, text=True)
            elapsed_time = time.perf_counter_ns() - start_time
        print(f"Elapsed time: {elapsed_time / 1e9:.3f} seconds")
        if process.returncode != 0:
            print("Test failed")
            print(f"cover_begin={cover_begin}, cover_end={cover_end}, intervals={intervals}")
            print("process returned non-zero exit code")
            print(f"output={process.stdout}")
            print(f"error={process.stderr}")
            break
        output_lines = process.stdout.strip().split('\n')

        if len(output_lines) == 1:
            if check_is_possible(cover_begin, cover_end, intervals):
                print("Test failed")
                print(f"cover_begin={cover_begin}, cover_end={cover_end}, intervals={intervals}")
                print("claimed impossible")
                break

            print("Test passed - correctly claimed impossible")
            continue

        if len(output_lines) != 2:
            print("Test failed")
            print(f"cover_begin={cover_begin}, cover_end={cover_end}, intervals={intervals}")
            print("output has wrong number of lines")
            print(f"output_lines={output_lines}")
            break

        output_len = int(output_lines[0])
        output_indexes = [int(x) for x in output_lines[1].split()]
        assert output_len == len(output_indexes)
        chosen_intervals = [intervals[x - 1] for x in output_indexes]
        if check_is_possible(cover_begin, cover_end, chosen_intervals):
            print(f"Test passed - correctly chose {output_len} intervals")
        else:
            print("Test failed")
            print(f"cover_begin={cover_begin}, cover_end={cover_end}, intervals={intervals}")
            print(f"output_len={output_len}, output_indexes={output_indexes}, chosen_intervals={chosen_intervals}")
            print("chosen intervals do not cover the interval")
            break

if __name__ == "__main__":
    assert len(sys.argv) == 2
    test_program(sys.argv[1])
