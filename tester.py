from dataclasses import dataclass
import random
import subprocess
import sys
import time
import pathlib

MIN_INTERVAL_BEGIN = -100000
MAX_INTERVAL_END = 100000
MAX_INTERVAL_AMOUNT = 100000

@dataclass
class IntervalProblem:
    cover_begin: int
    cover_end: int
    intervals: list[tuple[int, int]]

def format_problem(pb: IntervalProblem) -> str:
    """
    Convert the IntervalProblem to the format specified in the problem statement.
    It must be exactly like this to be parsed correctly by the solver.
    """
    test_txt = f"{pb.cover_begin} {pb.cover_end}\n"
    test_txt += f"{len(pb.intervals)}\n"
    test_txt += '\n'.join(f"{x[0]} {x[1]}" for x in pb.intervals)
    test_txt += '\n'
    return test_txt

def generate_test_case() -> IntervalProblem:
    cover_begin = random.randint(MIN_INTERVAL_BEGIN, MIN_INTERVAL_BEGIN + 100)
    cover_end = random.randint(MAX_INTERVAL_END - 100, MAX_INTERVAL_END)
    interval_amount = random.randint(1, MAX_INTERVAL_AMOUNT)
    intervals: list[tuple[int, int]] = []
    for _ in range(interval_amount):
        x = random.randint(MIN_INTERVAL_BEGIN, MAX_INTERVAL_END - 1)
        y = x + round(abs(random.normalvariate(100, 100))) + 1
        y = min(y, MAX_INTERVAL_END)
        intervals.append((x, y))
    return IntervalProblem(cover_begin, cover_end, intervals)

def check_is_possible(p : IntervalProblem) -> bool:
    bools = [False for _ in range(MIN_INTERVAL_BEGIN, MAX_INTERVAL_END + 1)]
    for (left, right) in p.intervals:
        for i in range(left - MIN_INTERVAL_BEGIN, right - MIN_INTERVAL_BEGIN + 1):
            bools[i] = True
    return all(bools[p.cover_begin - MIN_INTERVAL_BEGIN:p.cover_end - MIN_INTERVAL_BEGIN + 1])

def make_file_for_next_test(tests_folder: pathlib.Path, counter_file_name: str) -> tuple[int, pathlib.Path]:
    counter_file = tests_folder / counter_file_name
    if not tests_folder.exists():
        tests_folder.mkdir()
    if not counter_file.exists():
        counter_file.write_text("0\n")
    counter_txt = counter_file.read_text(encoding='ascii')
    try:
        last_test = int(counter_txt)
    except ValueError as e:
        raise ValueError(f"File {counter_file} contains non-integer data: {counter_txt}") from e
    this_test = last_test + 1
    counter_file.write_text(f"{this_test}\n")
    new_test_file = tests_folder / f"test_{this_test}.txt"
    if new_test_file.exists():
        raise FileExistsError(f"Test file {new_test_file} already exists")
    new_test_file.touch()
    return this_test, new_test_file

@dataclass
class TestResult:
    elapsed_ns: int
    process: subprocess.CompletedProcess[str]
    message: str
    failed: bool

def run_one_test(input_file_path: pathlib.Path, test: IntervalProblem, solver_path: str) -> TestResult:
    input_file_path.write_text(format_problem(test), encoding='ascii')

    with open(input_file_path, 'r', encoding='ascii') as input_file_handle:
        start_time = time.perf_counter_ns()
        process = subprocess.run(solver_path, stdin=input_file_handle, capture_output=True, check=False, text=True)
        elapsed_time = time.perf_counter_ns() - start_time

    def mk_fail(msg: str) -> TestResult:
        return TestResult(elapsed_time, process, msg, True)

    def mk_success(msg: str) -> TestResult:
        return TestResult(elapsed_time, process, msg, False)

    if process.returncode != 0:
        return mk_fail("Non-zero exit code")

    output_lines = process.stdout.strip().split('\n')

    if len(output_lines) == 1:
        if check_is_possible(test):
            return mk_fail("Incorrectly said impossible")

        return mk_success("Correctly said impossible")

    if len(output_lines) != 2:
        return mk_fail("Line 1 doesn't match number of indexes on line 2")

    output_len = int(output_lines[0])
    output_indexes = [int(x) for x in output_lines[1].split()]
    assert output_len == len(output_indexes)

    chosen_intervals: list[tuple[int, int]] = []
    for index in output_indexes:
        try:
            # indexes are 1-based
            chosen_intervals.append(test.intervals[index - 1])
        except IndexError:
            return mk_fail(f"Index {index} out of bounds")

    chosen_solution = IntervalProblem(test.cover_begin, test.cover_end, chosen_intervals)

    if not check_is_possible(chosen_solution):
        return mk_fail(f"Incorrectly chose {output_len} intervals, does not cover the interval")

    return mk_success(f"Correctly chose {output_len} intervals")

def test_forever(solver_path: str, tests_dir: pathlib.Path):
    while True:
        test = generate_test_case()
        test_nr, input_file_path = make_file_for_next_test(tests_dir, "test_counter.txt")
        result = run_one_test(input_file_path, test, solver_path)
        print(f"Test {test_nr}:")
        print(f"Elapsed: {result.elapsed_ns / 1e9:.3f} seconds")

        if result.failed:
            print(f"Exit code: {result.process.returncode}")
            print(f"Failure: {result.message}")
            if len(result.process.stderr):
                print(f"Process stderr: {result.process.stderr.strip()}")
            else:
                print("No stderr output")
            print(f"Saved input to {input_file_path}")
            if len(result.process.stdout):
                output_file = input_file_path.with_name(input_file_path.stem + ".out.txt")
                output_file.write_text(result.process.stdout)
                print(f"Saved output to {output_file}")
            else:
                print("No stdout output")
            break

        print(f"Success: {result.message}")
        input_file_path.unlink()

def main():
    assert len(sys.argv) == 2
    tests_dir = pathlib.Path("tests")
    test_forever(sys.argv[1], tests_dir)

if __name__ == "__main__":
    main()
