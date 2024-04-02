cmake_minimum_required(VERSION 3.26)
project(AA C)

set(CMAKE_C_STANDARD 11)

add_executable(intervals intervals/intervals.c)
add_executable(fractional_knapsack knapsack/fractional_knapsack.c)
add_executable(homework_knapsack knapsack/homework_knapsack.c)
add_executable(discrete_knapsack knapsack/discrete_knapsack.c)
