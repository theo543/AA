from pathlib import Path
from random import choice, seed
from subprocess import run
from fractions import Fraction
from sys import argv, exit as sys_exit
from typing import cast
from polygenerator import random_polygon
from shapely.geometry import Polygon, Point
import matplotlib.pyplot as plt

def random_polygon_integer_points(n: int = 1000, scale: int = 1000000) -> Polygon:
    while True:
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

    choices = [(random_near, "OUTSIDE"), (random_far, "OUTSIDE")] + [(random_inside, "INSIDE")] * 2
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
        markersize = 4
        points_fmt = 'ro'
        if 'BOUNDARY' in result:
            points_fmt = 'bx'
            markersize = 2
        if 'INSIDE' in result:
            points_fmt = 'go'
        plt.plot(x, y, points_fmt, markersize=markersize)

    xs = [x for x, _ in poly.exterior.coords]
    ys = [y for _, y in poly.exterior.coords]
    plt.plot(xs, ys, 'b-', linewidth=1)

    plt.savefig(out, bbox_inches='tight', pad_inches=0.1)

def format_data(poly: Polygon, points: list[tuple[tuple[int, int], str]]) -> tuple[str, str]:
    poly_point_nr = len(poly.exterior.coords) - 1
    poly_point_coords_str = '\n'.join([f'{x} {y}' for x, y in [shapely_point_to_int_tuple(Point(pt)) for pt in poly.exterior.coords[:-1]]])
    challenge_points_nr = len(points)
    challenge_points_str = '\n'.join([f'{p[0]} {p[1]}' for (p, _) in points])
    solver_input = f'{poly_point_nr}\n{poly_point_coords_str}\n{challenge_points_nr}\n{challenge_points_str}'
    expected_output = '\n'.join([is_inside for (_, is_inside) in points])
    return solver_input, expected_output

def run_test(solver_path: Path, subtests: int = 10000):
    expected_output_path = Path("expected_output.txt")
    input_path = Path("input.txt")
    actual_output_path = Path("actual_output.txt")
    img_path = Path("polygon.png")

    poly = random_polygon_integer_points()
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
    if len(argv) != 2 and len(argv) != 3:
        print(f"Usage: {argv[0]} <solver_path>")
        sys_exit(1)
    solver_path = Path(argv[1])
    tests = 1
    if len(argv) == 3:
        tests = int(argv[2])
    for _ in range(tests):
        seed(None)
        run_test(solver_path)

if __name__ == "__main__":
    main()
