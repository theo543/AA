from dataclasses import dataclass
import random
import subprocess
import sys
import time
import pathlib
import signal
import typing
from argparse import ArgumentParser

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

@dataclass
class TestGenerationParams:
    min_interval_begin: int
    max_interval_end: int
    max_interval_amount: int
    max_interval_length: int
    max_cover_len: bool
    def __post_init__(self):
        if self.min_interval_begin >= self.max_interval_end:
            raise ValueError("min_interval_begin must be less than max_interval_end")
        if self.max_interval_amount <= 0:
            raise ValueError("max_interval_amount must be positive")
        if self.max_interval_length <= 0:
            raise ValueError("max_interval_length must be positive")

def generate_test_case(params: TestGenerationParams) -> IntervalProblem:
    min_val = params.min_interval_begin
    max_val = params.max_interval_end
    max_amount = params.max_interval_amount
    max_len = params.max_interval_length
    cover_begin = min_val
    cover_end = max_val
    if not params.max_cover_len:
        cover_begin += random.randint(0, (max_val - min_val) // 10)
        cover_end -= random.randint(0, (max_val - min_val) // 10)
    interval_amount = random.randint(1, max_amount)
    intervals: list[tuple[int, int]] = []
    for _ in range(interval_amount):
        x = random.randint(min_val, max_val - 1)
        y = random.randint(x + 1, min(x + max_len, max_val))
        intervals.append((x, y))
    return IntervalProblem(cover_begin, cover_end, intervals)

def check_is_possible(p : IntervalProblem) -> bool:
    rightmost_covered = p.cover_begin - 1
    intervals = sorted(p.intervals)
    scan = 0
    for cover in range(p.cover_begin, p.cover_end + 1):
        if cover <= rightmost_covered:
            continue
        while True:
            if scan >= len(intervals) or intervals[scan][0] > cover:
                return False
            if cover <= intervals[scan][1]:
                rightmost_covered = intervals[scan][1]
                break
            scan += 1
    return True

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

def run_one_test(input_file_path: pathlib.Path, test: IntervalProblem, solver_path: pathlib.Path) -> TestResult:
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

def test_forever(solver_path: pathlib.Path, tests_dir: pathlib.Path, tests_counter: str, params: TestGenerationParams, test_limit: int) -> typing.NoReturn:
    signaled = False

    def set_signaled():
        nonlocal signaled
        if signaled:
            print("Received two keyboard interrupts, exiting immediately")
            sys.exit(1)
        signaled = True

    signal.signal(signal.SIGINT, lambda _1, _2 : set_signaled())

    tests = 0
    while not signaled:
        tests += 1
        if 0 < test_limit < tests:
            print(f"Reached test limit of {test_limit}, stopping")
            break
        test = generate_test_case(params)
        test_nr, input_file_path = make_file_for_next_test(tests_dir, tests_counter)
        result = run_one_test(input_file_path, test, solver_path)
        print(f"Test {test_nr}:")
        if signaled and result.failed:
            # Failure is probably due to subprocess inheriting the SIGINT signal
            print("Canceled")
            input_file_path.unlink()
            break
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
        print()
        input_file_path.unlink()

    print("Testing stopped")
    files = list(tests_dir.iterdir())
    if (len(files) == 1 and files[0].name == tests_counter) or len(files) == 0:
        print(f"No failing test files seem to be stored in {tests_dir}, removing it")
        if len(files) == 1:
            print(f"Removing test number counter file {files[0]}")
            files[0].unlink()
        tests_dir.rmdir()
    else:
        print(f"Not removing {tests_dir}, it seems to contain files, probably failing tests")
    sys.exit(0)

def main():
    ap = ArgumentParser()
    ap.add_argument("--solver", help="Path to the solver executable", type=str, default="intervals")
    ap.add_argument("--test_dir", help="Path to the directory where tests are stored", type=str, default="tests")
    ap.add_argument("--min_interval_begin", help="Minimum value for interval begin", type=int, default=-100000)
    ap.add_argument("--max_interval_end", help="Maximum value for interval end", type=int, default=100000)
    ap.add_argument("--max_interval_amount", help="Maximum amount of intervals", type=int, default=100000)
    ap.add_argument("--max_interval_length", help="Maximum length of an interval", type=int, default=200)
    ap.add_argument("--max_cover", help="Always test covering the entire interval", action="store_true", default=False)
    ap.add_argument("--test_limit", help="Maximum amount of tests to run (0 = unlimited)", type=int, default=0)
    args = ap.parse_args()
    print(args)
    params = TestGenerationParams(args.min_interval_begin, args.max_interval_end, args.max_interval_amount, args.max_interval_length, args.max_cover)
    tests_dir = pathlib.Path(args.test_dir).absolute()
    solver = pathlib.Path(args.solver).absolute()
    test_limit: int = args.test_limit
    test_forever(solver, tests_dir, "test_counter.txt", params, test_limit)

if __name__ == "__main__":
    main()
