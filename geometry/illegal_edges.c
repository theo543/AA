#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <inttypes.h>

typedef int64_t i64;
#define I64 "%" PRId64
#define MAX_POINTS 100000

typedef struct point { i64 x, y; } point;
typedef enum result { INSIDE = 0, OUTSIDE = 1, BOUNDARY = 2 } result;

static i64 pow2(i64 x) {
    return x * x;
}

static i64 det_3d(i64 v11, i64 v12, i64 v13, i64 v21, i64 v22, i64 v23, i64 v31, i64 v32, i64 v33) {
    return v11 * (v22 * v33 - v23 * v32) -
           v12 * (v21 * v33 - v23 * v31) +
           v13 * (v21 * v32 - v22 * v31);
}

static result point_position_circumscribed_circle(point a, point b, point c, point p) {
    /*
    | x_a y_a (x_a^2 + y_a^2) 1 |
    | x_b y_b (x_b^2 + y_b^2) 1 |
    | x_c y_c (x_c^2 + y_c^2) 1 |
    | x_p y_p (x_p^2 + y_p^2) 1 |
    =
    - | (x_b - x_a) (y_b - y_a) (x_b^2 + y_b^2 - x_a^2 - y_a^2) |
      | (x_c - x_a) (y_c - y_a) (x_c^2 + y_c^2 - x_a^2 - y_a^2) |
      | (x_p - x_a) (y_p - y_a) (x_p^2 + y_p^2 - x_a^2 - y_a^2) |
    */
    i64 det = - det_3d(b.x - a.x, b.y - a.y, pow2(b.x) + pow2(b.y) - pow2(a.x) - pow2(a.y),
                       c.x - a.x, c.y - a.y, pow2(c.x) + pow2(c.y) - pow2(a.x) - pow2(a.y),
                       p.x - a.x, p.y - a.y, pow2(p.x) + pow2(p.y) - pow2(a.x) - pow2(a.y));
    if(det == 0) return BOUNDARY;
    if(det > 0) return INSIDE;
    /* det < 0 */ return OUTSIDE;
}

int main(void) {
    point a, b, c, d;
    scanf(I64 I64 I64 I64 I64 I64 I64 I64, &a.x, &a.y, &b.x, &b.y, &c.x, &c.y, &d.x, &d.y);
    bool ac_illegal = point_position_circumscribed_circle(a, b, c, d) == INSIDE;
    bool bd_illegal = point_position_circumscribed_circle(a, b, d, c) == INSIDE;
    printf("AC: %s\n", ac_illegal ? "ILLEGAL" : "LEGAL");
    printf("BD: %s\n", bd_illegal ? "ILLEGAL" : "LEGAL");
}
