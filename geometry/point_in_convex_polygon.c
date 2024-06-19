#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <inttypes.h>

typedef int32_t i32;
typedef int64_t i64;
#define I32 "%" PRId32

static i64 abs64(i64 x) {
    return x > 0 ? x : -x;
}

static void minimize(i32 *current_min, i32 new_value) {
    if(new_value < *current_min) *current_min = new_value;
}

static void maximize(i32 *current_max, i32 new_value) {
    if(new_value > *current_max) *current_max = new_value;
}

typedef enum result { INSIDE, OUTSIDE, BOUNDARY } result;

typedef struct point { i32 x; i32 y; } point;

static bool point_equal(point a, point b) {
    return a.x == b.x && a.y == b.y;
}

static i64 signed_area(point a, point b, point p) {
    /*
        | a_x a_y 1 |
        | b_x b_y 1 |
        | p_x p_y 1 |

        =

        | (b_x - a_x) (b_y - a_y) |
        | (p_x - a_x) (p_y - a_y) |

        returns 2 * signed area of triangle a, b, p (positive if points are counterclockwise)
    */
    return (i64)(b.x - a.x) * (i64)(p.y - a.y) - (i64)(b.y - a.y) * (i64)(p.x - a.x);
}

static bool in_interval(i32 a, i32 b, i32 x) {
    if(a > b) return in_interval(b, a, x);
    return (a <= x) && (x <= b);
}

static bool point_in_segment(point a, point b, point p) {
    return (signed_area(a, b, p) == 0) && in_interval(a.x, b.x, p.x) && in_interval(a.y, b.y, p.y);
}

static result point_in_triangle(point a, point b, point c, point p) {
    i64 abc_area = abs64(signed_area(a, b, c));
    i64 abp_area = abs64(signed_area(a, b, p));
    i64 bcp_area = abs64(signed_area(b, c, p));
    i64 cap_area = abs64(signed_area(c, a, p));
    i64 total_area = abp_area + bcp_area + cap_area;
    if(abc_area != total_area) return OUTSIDE;
    if(abp_area == 0 || bcp_area == 0 || cap_area == 0) return BOUNDARY;
    return INSIDE;
}

static result point_in_convex_polygon(point *polygon, i32 polygon_len, point p) {
    if(polygon_len <= 2) {
        fprintf(stderr, "point_in_convex_polygon called with polygon_len <= 2");
        exit(1);
    }
    if(polygon_len == 3) {
        return point_in_triangle(polygon[0], polygon[1], polygon[2], p);
    }
    i32 mid = polygon_len / 2;
    point p_0 = polygon[0];
    point p_mid = polygon[mid];
    i64 mid_line_ori = signed_area(p_0, p_mid, p);
    if(mid_line_ori == 0) {
        if(point_equal(p_0, p) || point_equal(p_mid, p)) return BOUNDARY;
        if(point_in_segment(p_0, p_mid, p)) return INSIDE;
        return OUTSIDE;
    }
    if(mid_line_ori > 0) {
        point tmp = polygon[mid - 1];
        polygon[mid - 1] = polygon[0];
        result r = point_in_convex_polygon(polygon + mid - 1, polygon_len - (mid - 1), p);
        polygon[mid - 1] = tmp;
        return r;
    }
    /* mid_line_ori < 0 */
    return point_in_convex_polygon(polygon, mid + 1, p);    
}

#define MAX_POINTS 100000

int main(void) {
    static point polygon[MAX_POINTS];
    i32 polygon_len;

    i32 min_x = INT32_MAX;
    i32 min_y = INT32_MAX;
    i32 max_x = INT32_MIN;
    i32 max_y = INT32_MIN;

    scanf(I32, &polygon_len);
    for(int x = 0;x < polygon_len;x++) {
        scanf(I32 I32, &polygon[x].x, &polygon[x].y);
        minimize(&min_x, polygon[x].x);
        maximize(&max_x, polygon[x].x);
        minimize(&min_y, polygon[x].y);
        maximize(&max_y, polygon[x].y);
        if((x >= 2) && (signed_area(polygon[x - 2], polygon[x - 1], polygon[x]) == 0)) {
            polygon[x - 1] = polygon[x];
            polygon_len--;
            x--;
        }
    }

    if(signed_area(polygon[0], polygon[1], polygon[2]) < 0) {
        for(int l = 0, r = polygon_len - 1;l < r;l++, r--) {
            point tmp = polygon[l];
            polygon[l] = polygon[r];
            polygon[r] = tmp;
        }
    }

    i32 m;
    scanf(I32, &m);
    const char *result_str[] = { [INSIDE] = "INSIDE", [OUTSIDE] = "OUTSIDE", [BOUNDARY] = "BOUNDARY" };
    for(int x = 0;x < m;x++) {
        point p;
        scanf(I32 I32, &p.x, &p.y);
        result r;
        if((!in_interval(min_x, max_x, p.x)) || (!in_interval(min_y, max_y, p.y))) {
            r = OUTSIDE;
        } else {
            r = point_in_convex_polygon(polygon, polygon_len, p);
        }
        puts(result_str[r]);
    }
}
