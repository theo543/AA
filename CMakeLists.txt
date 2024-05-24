cmake_minimum_required(VERSION 3.26)
project(AA C)

set(CMAKE_C_STANDARD 11)

add_executable(intervals intervals/intervals.c)
add_executable(fractional_knapsack knapsack/fractional_knapsack.c)
add_executable(homework_knapsack knapsack/homework_knapsack.c)
add_executable(discrete_knapsack knapsack/discrete_knapsack.c)
add_executable(cover geometry/cover.c)
add_executable(orientation geometry/orientation.c)
add_executable(roby geometry/roby.c)
add_executable(point_in_polygon geometry/point_in_polygon.c)
add_executable(point_convex_poly geometry/point_convex_poly.c)
