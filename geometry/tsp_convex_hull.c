#include <math.h>
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdbool.h>
#include <inttypes.h>

typedef int32_t i32;
typedef int64_t i64;
#define I32 "%" PRId32

typedef struct point { i32 x; i32 y; } point;

#define MAX_POINTS 1000

static i64 pow2(i64 x) {
    return x * x;
}

static i64 squared_distance(const point a, const point b) {
    return pow2(a.x - b.x) + pow2(a.y - b.y);
}


static double distance(const point a, const point b) {
    return sqrt(pow(a.x - b.x, 2) + pow(a.y - b.y, 2));
}

static i64 orientation(point a, point b, point p) {
    return (i64)(b.x - a.x) * (i64)(p.y - a.y) - (i64)(b.y - a.y) * (i64)(p.x - a.x);
}

static point leftmost_lowest(const point *polygon, i32 len) {
    point lowest = polygon[0];
    for(i32 i = 1;i < len;i++) {
        if(polygon[i].x < lowest.x) {
            lowest = polygon[i];
        } else if(polygon[i].x == lowest.x && polygon[i].y < lowest.y) {
            lowest = polygon[i];
        }
    }
    return lowest;
}

point lowest;

static int comparator(const void *a_void, const void *b_void) {
    point a = *(point *)a_void;
    point b = *(point *)b_void;
    i64 o = orientation(lowest, a, b);
    if(o == 0) {
        return squared_distance(lowest, a) < squared_distance(lowest, b) ? -1 : 1;
    }
    return o > 0 ? -1 : 1;
}

static i32 convex_hull(point *polygon, i32 *hull, bool *added, i32 len) {
    lowest = leftmost_lowest(polygon, len);
    //printf("Lowest: " I32 " " I32 "\n", lowest.x, lowest.y);
    qsort(polygon, len, sizeof(point), comparator);
    //printf("Sorted:\n");
    //for(int x = 0;x < len;x++) {
    //    printf(I32 " " I32 "\n", polygon[x].x, polygon[x].y);
    //}
    i32 hull_len = 0;
    for(int x = 0;x < len;x++) {
        while(hull_len >= 2 && orientation(polygon[hull[hull_len - 2]], polygon[hull[hull_len - 1]], polygon[x]) < 0) {
            hull_len--;
        }
        hull[hull_len++] = x;
    }
    for(int x = 0;x < hull_len;x++) {
        added[hull[x]] = true;
    }
    return hull_len;
}

int main(void) {
    static point polygon[MAX_POINTS];
    static int tour[MAX_POINTS + 1];
    static bool added[MAX_POINTS];
    i32 polygon_len;

    scanf(I32, &polygon_len);
    for(int x = 0;x < polygon_len;x++) {
        scanf(I32 I32, &polygon[x].x, &polygon[x].y);
    }

    i32 tour_len = convex_hull(polygon, tour, added, polygon_len);
    //printf("Convex hull:\n");
    //for(int x = 0;x < tour_len;x++) {
    //    printf(I32 " " I32 "\n", polygon[tour[x]].x, polygon[tour[x]].y);
    //}
    i32 remaining = polygon_len - tour_len;
    tour[tour_len++] = tour[0];

    while(remaining > 0) {
        i32 best_insertion_before = -1;
        i32 best_insertion_index = -1;
        double best_insertion_cost = INFINITY;
        for(i32 r = 0;r < polygon_len;r++) {
            if(added[r]) continue;
            i32 best_before;
            double best_ij_dist;
            double best_cost = INFINITY;
            for(i32 i = 1;i < tour_len;i++) {
                double ir_dist = distance(polygon[tour[i - 1]], polygon[r]);
                double rj_dist = distance(polygon[r], polygon[tour[i]]);
                double ij_dist = distance(polygon[tour[i - 1]], polygon[tour[i]]);
                double cost = ir_dist + rj_dist - ij_dist;
                if(cost < best_cost) {
                    best_ij_dist = ij_dist;
                    best_cost = cost;
                    best_before = i;
                }
            }
            best_cost = (best_cost - best_ij_dist) / best_ij_dist;
            if(best_cost < best_insertion_cost) {
                best_insertion_before = best_before;
                best_insertion_index = r;
                best_insertion_cost = best_cost;
            }
        }
        for(i32 i = tour_len;i > best_insertion_before;i--) {
            tour[i] = tour[i - 1];
        }
        tour[best_insertion_before] = best_insertion_index;
        tour_len++;
        added[best_insertion_index] = true;
        remaining--;
    }
    //printf("TSP tour:\n");
    for(int x = 0;x < tour_len;x++) {
        printf(I32 " " I32 "\n", polygon[tour[x]].x, polygon[tour[x]].y);
    }
}
