from pathlib import Path
from random import choice, seed, random, randint, shuffle
from subprocess import run
from fractions import Fraction
from sys import argv as sys_argv, exit as sys_exit
from typing import cast
from math import atan2
from polygenerator import random_polygon
from shapely.geometry import Polygon, Point, LineString
import matplotlib.pyplot as plt

def is_convex(poly: list[tuple[int, int]]) -> bool:
    def cross_product(a: Point, b: Point, c: Point) -> float:
        return (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x)
    points_triples = [(poly[i], poly[i + 1], poly[i + 2]) for i in range(len(poly) - 2)]
    points_triples.append((poly[-2], poly[-1], poly[0]))
    points_triples.append((poly[-1], poly[0], poly[1]))
    is_positive = [cross_product(Point(a), Point(b), Point(c)) > 0 for a, b, c in points_triples]
    # a polygon convex should have all cross products of adjacent edges either all positive or all negative
    return all(is_positive) or not any(is_positive)

def random_convex_polygon(n: int, bounding_box: tuple[int, int, int, int]) -> list[tuple[int, int]]:
    # valtr algorithm
    # the one from polygenerator uses floats, and rounding to int makes it not convex
    def random_unique_numbers(n: int, high: int) -> list[int]:
        numbers = []
        while True:
            numbers = list(set(numbers))
            if len(numbers) < n:
                numbers += [randint(0, high) for _ in range(n - len(numbers))]
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
    width = bounding_box[2] - bounding_box[0]
    height = bounding_box[3] - bounding_box[1]
    x_vec = vec_comp(*random_split(n, width))
    y_vec = vec_comp(*random_split(n, height))
    shuffle(y_vec)
    vectors = list(zip(x_vec, y_vec))
    vectors = sorted(vectors, key=lambda v: atan2(v[1], v[0]))
    poly: list[tuple[int, int]] = [(0, 0)]
    for v in vectors[:-1]:
        poly.append((poly[-1][0] + v[0], poly[-1][1] + v[1]))
    poly = [(x + bounding_box[0], y + bounding_box[1]) for x, y in poly]
    assert is_convex(poly)
    return poly

def random_polygon_integer_points(convex: bool, n: int = 1000, scale: int = 1000000) -> Polygon:
    while True:
        if convex:
            poly_scaled_integer = random_convex_polygon(n, (-scale, -scale, scale, scale))
        else:
            poly = random_polygon(n)
            poly_scaled_integer = [(int(x*scale), int(y*scale)) for x, y in poly]
        if len(poly_scaled_integer) != len(set(poly_scaled_integer)):
            print("rejection of polygon with duplicate points")
            continue
        poly_shapely = Polygon(poly_scaled_integer)
        if not (poly_shapely.is_valid and poly_shapely.area > 0):
            print("rejection of invalid polygon")
            continue
        return poly_shapely

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
    for x in range(len(poly.exterior.coords) - 1):
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

    for ((x, y), _), result in zip(points, output.split('\n')):
        markersize = 2
        points_fmt = 'rx'
        if 'BOUNDARY' in result:
            points_fmt = 'bx'
        if 'INSIDE' in result:
            points_fmt = 'gx'
        plt.plot(x, y, points_fmt, markersize=markersize)

    xs = [x for x, _ in poly.exterior.coords]
    ys = [y for _, y in poly.exterior.coords]
    plt.plot(xs, ys, 'b-', linewidth=1)

    plt.savefig(out, bbox_inches='tight', pad_inches=0.1, dpi=1200)

def format_data(poly: Polygon, points: list[tuple[tuple[int, int], str]]) -> tuple[str, str]:
    poly_point_nr = len(poly.exterior.coords) - 1
    poly_point_coords_str = '\n'.join([f'{x} {y}' for x, y in [shapely_point_to_int_tuple(Point(pt)) for pt in poly.exterior.coords[:-1]]])
    challenge_points_nr = len(points)
    challenge_points_str = '\n'.join([f'{p[0]} {p[1]}' for (p, _) in points])
    solver_input = f'{poly_point_nr}\n{poly_point_coords_str}\n{challenge_points_nr}\n{challenge_points_str}'
    expected_output = '\n'.join([is_inside for (_, is_inside) in points])
    return solver_input, expected_output

def run_test(convex: bool, solver_path: Path, subtests: int = 10000):
    expected_output_path = Path("expected_output.txt")
    input_path = Path("input.txt")
    actual_output_path = Path("actual_output.txt")
    img_path = Path("polygon.svg")

    poly = random_polygon_integer_points(convex)
    print(f"Generated polygon with {len(poly.exterior.coords) - 1} points.")
    points = [random_point_in_polygon(poly) for _ in range(subtests)] + all_points_on_edge(poly)
    print(f"Generated {subtests} points plus {len(points) - subtests} points on the edges with integer coordinates.")
    solver_input, expected_output = format_data(poly, points)
    expected_output_path.write_text(expected_output, encoding='ascii')
    input_path.write_text(solver_input, encoding='ascii')
    print("Running solver...")

    proc = run([solver_path], input=solver_input, capture_output=True, text=True, check=False)
    assert proc.returncode == 0
    output = proc.stdout.strip()
    print("Solver finished.")
    plot_output(img_path, poly, points, output)
    print("Plotted output.")
    actual_output_path.write_text(output, encoding='ascii')

    assert expected_output == output

    print("Test passed.")

    expected_output_path.unlink()
    input_path.unlink()
    actual_output_path.unlink()

def main():
    convex = '--convex' in sys_argv
    argv = [arg for arg in sys_argv if arg != '--convex']
    if len(argv) != 2 and len(argv) != 3:
        print(f"Usage: {argv[0]} <solver_path>")
        sys_exit(1)
    solver_path = Path(argv[1])
    tests = 1
    if len(argv) == 3:
        tests = int(argv[2])
    for _ in range(tests):
        seed(None)
        run_test(convex, solver_path)

if __name__ == "__main__":
    main()
