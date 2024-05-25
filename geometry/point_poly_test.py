from pathlib import Path
from random import choice, seed, random, randint, shuffle
from subprocess import run
from fractions import Fraction
from argparse import ArgumentParser
from typing import cast
from math import atan2, log10, cos, sin, pi
from polygenerator import random_polygon
from shapely.geometry import Polygon, Point, LineString
import matplotlib.pyplot as plt
from tqdm import tqdm

def is_convex(poly: list[tuple[int, int]]) -> bool:
    def cross_product(a: Point, b: Point, c: Point) -> float:
        return (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x)
    points_triples = [(poly[i], poly[i + 1], poly[i + 2]) for i in range(len(poly) - 2)]
    points_triples.append((poly[-2], poly[-1], poly[0]))
    points_triples.append((poly[-1], poly[0], poly[1]))
    is_positive = [cross_product(Point(a), Point(b), Point(c)) > 0 for a, b, c in points_triples]
    # a polygon convex should have all cross products of adjacent edges either all positive or all negative
    return all(is_positive) or not any(is_positive)

def random_convex_polygon_maybe_too_big(n: int, max_absolute_coord: int) -> list[tuple[int, int]]:
    # valtr algorithm
    # the one from polygenerator uses floats, and rounding to int makes it not convex
    # for some reason this doesn't stay within the bounds
    # I think I should be generating it in [0, 1] and scaling it to the bounds, but rounding breaks convexity
    def random_unique_numbers(n: int, high: int) -> list[int]:
        numbers = []
        repeat_limit = 1000
        while True:
            numbers = list(set(numbers))
            if len(numbers) < n:
                numbers += [randint(0, high) for _ in range(n - len(numbers))]
                repeat_limit -= 1
                if repeat_limit == 0:
                    print(f"Warning: failed to generate {n} unique numbers in range 0-{high} as part of Valtr's algorithm, " +
                            "continuing with duplicates, the result may be non-convex and rejected later")
                    return numbers
                continue
            return numbers
    def random_split(n: int, high: int) -> tuple[list[int], list[int]]:
        l = sorted(random_unique_numbers(n, high))
        l_mid = l[1:-1]
        shuffle(l_mid)
        split = len(l_mid) // 2
        l1_mid = l_mid[:split]
        l2_mid = l_mid[split:]
        l1 = [l[0]] + l1_mid + [l[-1]]
        l2 = [l[0]] + l2_mid + [l[-1]]
        return l1, l2
    def vec_comp(l1: list[int], l2: list[int]) -> list[int]:
        l1 = [l1[i + 1] - l1[i] for i in range(len(l1) - 1)]
        l2 = [l2[i] - l2[i + 1] for i in range(len(l2) - 1)]
        return l1 + l2
    x_vec = vec_comp(*random_split(n, max_absolute_coord))
    y_vec = vec_comp(*random_split(n, max_absolute_coord))
    shuffle(y_vec)
    vectors = list(zip(x_vec, y_vec))
    vectors = sorted(vectors, key=lambda v: atan2(v[1], v[0]))
    poly: list[tuple[int, int]] = [(0, 0)]
    for v in vectors[:-1]:
        poly.append((poly[-1][0] + v[0], poly[-1][1] + v[1]))
    if not is_convex(poly):
        print("Rejection of non-convex polygon, this happens when bounding box is too small relative to the number of points (known issue)")
        return random_convex_polygon_maybe_too_big(n, max_absolute_coord)
    return poly

def poly_max(poly: list[tuple[int, int]]) -> int:
    max_abs = 0
    for x, y in poly:
        max_abs = max(max_abs, abs(x), abs(y))
    return max_abs

def random_convex_polygon(n: int, max_absolute_coord: int) -> list[tuple[int, int]]:
    # fix the algorithm giving polygons that are too big
    # don't know why it does that
    current_max = max_absolute_coord
    while True:
        poly = random_convex_polygon_maybe_too_big(n, current_max)
        max_abs = poly_max(poly)
        if max_abs <= max_absolute_coord:
            return poly
        ratio = max_abs / max_absolute_coord
        factor = 0.7
        if ratio > 10:
            factor = 10 ** -max(1, log10(ratio) - 2)
        elif ratio > 5:
            factor = 0.3
        elif ratio > 2:
            factor = 0.6
        current_max = int(current_max * factor)
        print(f"Generated polygon with max abs coord {max_abs}, multiplying max abs coord by {factor} and retrying " +
              f"({ratio} times too big, known issue of convex polygon generator)")

def random_polygon_integer_points(poly_type: str, n: int, max_absolute_coord: int) -> Polygon:
    while True:
        if poly_type == "convex":
            poly_scaled_integer = random_convex_polygon(n, max_absolute_coord)
        elif poly_type == "deterministic_convex":
            poly_scaled_integer = deterministic_convex_polygon(n, max_absolute_coord)
        elif poly_type == "concave":
            poly = random_polygon(n)
            poly_scaled_integer = [(int(x*max_absolute_coord), int(y*max_absolute_coord)) for x, y in poly]
            assert poly_max(poly_scaled_integer) <= max_absolute_coord
        else:
            raise ValueError("invalid polygon type")
        if len(poly_scaled_integer) != len(set(poly_scaled_integer)):
            print("rejection of polygon with duplicate points")
            continue
        poly_shapely = Polygon(poly_scaled_integer)
        if not (poly_shapely.is_valid and poly_shapely.area > 0):
            print("rejection of invalid polygon")
            continue
        return poly_shapely

def deterministic_convex_polygon(n: int, max_absolute_coord: int) -> list[tuple[int, int]]:
    poly = []
    for i in range(n):
        angle = 2 * i * pi / n
        x = int(max_absolute_coord * cos(angle))
        y = int(max_absolute_coord * sin(angle))
        poly.append((x, y))
    assert is_convex(poly)
    assert poly_max(poly) <= max_absolute_coord
    return poly

def shapely_point_to_int_tuple(point: Point) -> tuple[int, int]:
    point_int = (int(point.x), int(point.y))
    assert point.x == point_int[0] and point.y == point_int[1]
    return point_int

def random_point_in_polygon(poly: Polygon) -> tuple[tuple[int, int], str]:
    bounds = cast(tuple[float, float, float, float], poly.bounds)
    def not_in_poly(point: Point) -> bool:
        return not poly.contains(point) and not poly.touches(point)
    def random_in_range(min_x: int | float, min_y: int | float, max_x: int | float, max_y: int | float) -> Point:
        return Point(choice(range(int(min_x), int(max_x))), choice(range(int(min_y), int(max_y))))
    def random_in_aabb() -> Point:
        min_x, min_y, max_x, max_y = bounds
        return random_in_range(min_x, min_y, max_x, max_y)
    def random_near() -> Point:
        while True:
            point = random_in_aabb()
            if not_in_poly(point):
                return point
    def random_very_near() -> Point:
        while True:
            vertex_i = choice(range(len(poly.exterior.coords) - 1))
            a = poly.exterior.coords[vertex_i]
            b = poly.exterior.coords[vertex_i + 1]
            line = LineString([a, b])
            p = line.interpolate(random())
            nudge = range(-1, 2)
            p = Point(int(p.x) + choice(nudge), int(p.y) + choice(nudge))
            if not_in_poly(p):
                return p
    def random_inside() -> Point:
        while True:
            point = random_in_aabb()
            if poly.contains(point):
                return point
    def random_far() -> Point:
        while True:
            min_x, min_y, max_x, max_y = bounds
            x_len = max_x - min_x
            y_len = max_y - min_y
            div = 20 # don't go too far because it makes the plot ugly
            point = random_in_range(min_x - x_len // div, min_y - y_len // div, max_x + x_len // div, max_y + y_len // div)
            if not_in_poly(point):
                return point

    choices = [(random_near, "OUTSIDE"), (random_far, "OUTSIDE"), (random_very_near, "OUTSIDE")] + [(random_inside, "INSIDE")] * 3
    (func, is_inside) = choice(choices)
    return (shapely_point_to_int_tuple(func()), is_inside)

def all_points_on_edge(poly: Polygon) -> list[tuple[tuple[int, int], str]]:
    points = []
    for x in tqdm(range(len(poly.exterior.coords) - 1), desc="Generating all integer-coordinate points for each edge"):
        a = poly.exterior.coords[x]
        b = poly.exterior.coords[x + 1]
        if b[0] == a[0]:
            # special case for vertical edges
            for y in range(min(int(a[1]), int(b[1])), max(int(a[1]), int(b[1])) + 1):
                points.append(((int(a[0]), y), "BOUNDARY"))
            continue
        slope = Fraction(int(b[1]) - int(a[1]), int(b[0]) - int(a[0]))
        for step in range(999999999):
            x = a[0] + step * slope.denominator
            y = a[1] + step * slope.numerator
            point = Point(x, y)
            if not poly.touches(point):
                break # went past the end of the edge
            points.append((shapely_point_to_int_tuple(point), "BOUNDARY"))

    return points

def plot_output(out: Path, poly: Polygon, points: list[tuple[tuple[int, int], str]], output: str):
    plt.figure()
    plt.gca().set_aspect('equal')

    for ((x, y), _), result in tqdm(zip(points, output.split('\n')), desc="Plotting output points", total=len(points)):
        markersize = 2
        points_fmt = 'rx'
        if 'BOUNDARY' in result:
            points_fmt = 'bx'
        if 'INSIDE' in result:
            points_fmt = 'gx'
        plt.plot(x, y, points_fmt, markersize=markersize)

    print("Plotting polygon...")
    xs = [x for x, _ in poly.exterior.coords]
    ys = [y for _, y in poly.exterior.coords]
    plt.plot(xs, ys, 'b-', linewidth=1)

    print("Saving plot...")
    plt.savefig(out, bbox_inches='tight', pad_inches=0.1, dpi=1200)

def validate_test_data_expected_output(poly: Polygon, points: list[tuple[tuple[int, int], str]]):
    for (p, expected) in tqdm(points, desc="Validating test data expected output by checking it agrees with Shapely"):
        match expected:
            case "INSIDE":
                assert poly.contains(Point(p))
            case "OUTSIDE":
                assert not poly.contains(Point(p)) and not poly.touches(Point(p))
            case "BOUNDARY":
                assert poly.touches(Point(p))
            case _:
                raise ValueError("invalid expected string - must be INSIDE, OUTSIDE or BOUNDARY")

def format_data(poly: Polygon, points: list[tuple[tuple[int, int], str]], extra_points: int) -> tuple[str, str]:
    poly_point_nr = len(poly.exterior.coords) - 1
    coords = [shapely_point_to_int_tuple(Point(pt)) for pt in poly.exterior.coords[:-1]]
    coords_rotation = randint(0, len(coords) - 1)
    coords = coords[coords_rotation:] + coords[:coords_rotation]
    if randint(0, 1):
        coords = coords[::-1]
    # insert redundant points to test it doesn't break the solver
    modified_coords = [coords[0]]
    for i in tqdm(range(1, len(coords)), desc="Inserting collinear points in edges", total=len(coords) - 1) if extra_points > 0 else []:
        if extra_points == 0:
            break
        a = coords[i - 1]
        b = coords[i]
        midpoints: list[tuple[int, int]] = []
        if b[0] == a[0]:
            for y in range(min(a[1], b[1]) + 1, max(a[1], b[1])):
                midpoints.append((a[0], y))
        elif b[1] == a[1]:
            for x in range(min(a[0], b[0]) + 1, max(a[0], b[0])):
                midpoints.append((x, a[1]))
        else:
            ratio = Fraction(b[1] - a[1], b[0] - a[0])
            x = a[0] + ratio.denominator
            y = a[1] + ratio.numerator
            while poly.touches(Point(x, y)):
                midpoints.append((x, y))
                x += ratio.denominator
                y += ratio.numerator
        for p in midpoints:
            modified_coords.append(p)
            extra_points -= 1
        modified_coords.append(b)
    if extra_points > 0:
        print(f"Inserted {len(modified_coords) - len(coords)} extra points in the polygon edges.")
        coords = modified_coords
        poly_point_nr = len(coords)
    poly_point_coords_str = '\n'.join([f'{x} {y}' for x, y in coords])
    challenge_points_nr = len(points)
    challenge_points_str = '\n'.join([f'{p[0]} {p[1]}' for (p, _) in points])
    solver_input = f'{poly_point_nr}\n{poly_point_coords_str}\n{challenge_points_nr}\n{challenge_points_str}'
    expected_output = '\n'.join([is_inside for (_, is_inside) in points])
    return solver_input, expected_output

def run_test(n: int, scale: int, poly_type: str, solver_path: Path, subtests: int, plot: bool, boundary: bool, extra_points: int) -> bool:
    expected_output_path = Path("expected_output.txt")
    input_path = Path("input.txt")
    actual_output_path = Path("actual_output.txt")
    img_path = Path("polygon.svg")
    expected_img_path = Path("expected_polygon.svg")

    poly = random_polygon_integer_points(poly_type, n, scale)
    print(f"Generated polygon with {len(poly.exterior.coords) - 1} points.")
    points = [random_point_in_polygon(poly) for _ in tqdm(range(subtests), desc="Generating random points")]
    if boundary:
        points += all_points_on_edge(poly)
        points += [((int(x), int(y)), "BOUNDARY") for x, y in poly.exterior.coords]
    validate_test_data_expected_output(poly, points)
    solver_input, expected_output = format_data(poly, points, extra_points)
    expected_output_path.write_text(expected_output, encoding='ascii')
    input_path.write_text(solver_input, encoding='ascii')
    print("Running solver...")

    proc = run([solver_path], input=solver_input, capture_output=True, text=True, check=False)
    print("Solver finished.")
    output = proc.stdout.strip()
    actual_output_path.write_text(output, encoding='ascii')
    if proc.returncode != 0:
        print(f"Solver exit code is {proc.returncode}.")
        print("Output won't be plotted since it's likely incomplete or garbage. Output files will still be saved.")
        print("Printing stderr:")
        print(proc.stderr)
        return False
    if output != expected_output:
        print("Output doesn't match expected output.")
        print("Incorrect output will be plotted, output files will be saved.")
        plot_output(img_path, poly, points, output)
        plot_output(expected_img_path, poly, points, expected_output)
        return False
    if plot:
        plot_output(img_path, poly, points, output)
        print("Plotted output.")
    print("Test passed.")
    expected_output_path.unlink()
    input_path.unlink()
    actual_output_path.unlink()
    return True

def main():
    ap = ArgumentParser("point_poly_test")
    ap.add_argument("solver_path", type=Path)
    ap.add_argument("-n", type=int, default=1000,
                    help="Number of vertices of the polygon")
    ap.add_argument("--bounds", type=int, default=1000000,
                    help="Max absolute value of the coordinates")
    ap.add_argument("--subtests", type=int, default=10000,
                    help="Number of random test points to generate (the points on the edges are generated deterministically)")
    convex = ap.add_mutually_exclusive_group()
    convex.add_argument("--convex", action="store_true", default=False,
                    help="Generate only convex polygons " +
                    "(can't generate polygons with 10^5 vertices with bounds 10^9 due to known issue, use deterministic convex instead for that)")
    convex.add_argument("--det-convex", action="store_true", default=False,
                    help="Generate only deterministic convex polygons")
    ap.add_argument("--tests", type=int, default=1,
                    help="Number of tests to run")
    ap.add_argument("--disable-boundary", action="store_false", default=True,
                    help="Disable testing all points on the boundary (might be necessary for polygons with very many edges)")
    ap.add_argument("--extra-points", type=int, default=0,
                    help="Number of extra points to insert in the polygon edges, up to one per edge " +
                    "(will add points to input, make sure it doesn't overflow the solver's limit)")
    args = ap.parse_args()
    tests = cast(int, args.tests)
    n = cast(int, args.n)
    bounds = cast(int, args.bounds)
    convex = cast(bool, args.convex)
    det_convex = cast(bool, args.det_convex)
    subtests = cast(int, args.subtests)
    solver_path = cast(Path, args.solver_path)
    boundary = cast(bool, args.disable_boundary)
    extra_points = cast(int, args.extra_points)
    plot = True
    poly_type = "deterministic_convex" if det_convex else "convex" if convex else "concave"
    if tests > 1:
        plot = False
        print("Plotting is disabled for multiple tests due to slow performance.")
    for i in range(tests):
        seed(None)
        if not run_test(n, bounds, poly_type, solver_path, subtests, plot, boundary, extra_points):
            if i != tests - 1:
                print(f"Remaining {tests - i - 1} tests cancelled due to failure.")
            break

if __name__ == "__main__":
    main()
