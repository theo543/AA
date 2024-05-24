#include <math.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdbool.h>
#include <inttypes.h>

typedef int64_t i64;
#define I64 "%" PRId64
#define MAX_POINTS 100000

typedef struct point { i64 x, y; } point;
typedef enum result { INSIDE, OUTSIDE, BOUNDARY } result;

static i64 det(point prev2, point prev1, point this) {
    return (prev1.x - prev2.x) * (this.y - prev2.y) - (this.x - prev2.x) * (prev1.y - prev2.y);
}

static bool in_interval(i64 a, i64 b, i64 p) {
    if(a > b) return in_interval(b, a, p);
    return a <= p && p <= b;
}

// check if the point is in the segment, already knowing it's colinear with it
static bool in_segment(point a, point b, point p) {
    if(a.x == b.x) return in_interval(a.y, b.y, p.y);
    return in_interval(a.x, b.x, p.x);
}

// in_segment converted to a result for convenience
static result in_segment_r(point a, point b, point p) {
    return in_segment(a, b, p) ? BOUNDARY : OUTSIDE;
}

static result trig_check(point a, point b, point c, point p) {
    i64 ab_p = det(a, b, p);
    i64 bc_p = det(b, c, p);
    i64 ca_p = det(c, a, p);
    // if any of these are 0, the point is either on the boundary, or outside and colinear with an edge
    if(ab_p == 0) return in_segment_r(a, b, p);
    if(bc_p == 0) return in_segment_r(b, c, p);
    if(ca_p == 0) return in_segment_r(c, a, p);
    // if it's inside, it will be left or right of all the edges depending on order
    return ((ab_p > 0 && bc_p > 0 && ca_p > 0) || (ab_p < 0 && bc_p < 0 && ca_p < 0)) ? INSIDE : OUTSIDE;
}

static void swap(point *a, point *b) {
    point tmp = *a;
    *a = *b;
    *b = tmp;
}

// check p inside convex poly
// poly array must have a free space at the end
static result check_point_in_convex(point p, point *poly, int poly_len) {
    if(poly_len == 3) {
        point a = poly[0], b = poly[1], c = poly[2];
        return trig_check(a, b, c, p);
    }
    int midpoint = poly_len / 2;
    i64 div_line_det = det(poly[0], poly[midpoint], p);
    if(div_line_det == 0) return in_segment_r(poly[0], poly[midpoint], p);
    if(div_line_det > 0) {
        // not a tail call, but this cuts it in half, so shouldn't overflow
        swap(&poly[poly_len], &poly[0]);
        result r = check_point_in_convex(p, poly + midpoint, poly_len - midpoint + 1);
        swap(&poly[poly_len], &poly[0]);
        return r;
    } else {
        return check_point_in_convex(p, poly, midpoint + 1);
    }
}

int main(void) {
    i64 n;
    scanf(I64, &n);
    static point poly[MAX_POINTS + 1];

    scanf(I64 I64, &poly[0].x, &poly[0].y);
    i64 max_x = poly[0].x, max_y = poly[0].y, min_x = poly[0].x, min_y = poly[0].y;
    for(i64 i = 1;i < n;i++) {
        scanf(I64 I64, &poly[i].x, &poly[i].y);
        if(poly[i].x > max_x) max_x = poly[i].x;
        if(poly[i].x < min_x) min_x = poly[i].x;
        if(poly[i].y > max_y) max_y = poly[i].y;
        if(poly[i].y < min_y) min_y = poly[i].y;
    }

    i64 m;
    scanf(I64, &m);
    while(m--) {
        point p;
        scanf(I64 I64, &p.x, &p.y);
        if(p.x < min_x || p.x > max_x || p.y < min_y || p.y > max_y) {
            printf("OUTSIDE\n");
            continue;
        }
        result r = check_point_in_convex(p, poly, n);
        if(r == INSIDE) printf("INSIDE\n");
        else if(r == OUTSIDE) printf("OUTSIDE\n");
        else printf("BOUNDARY\n");
    }
}
