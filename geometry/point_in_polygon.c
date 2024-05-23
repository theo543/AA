#include <math.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdbool.h>
#include <inttypes.h>

typedef uint32_t u32;
typedef uint64_t u64;
typedef int64_t i64;
#define I64 "%" PRId64
#define MAX_POINTS 1002

typedef struct point { i64 x, y; } point;

static i64 det(point prev2, point prev1, point this) {
    return (prev1.x - prev2.x) * (this.y - prev2.y) - (this.x - prev2.x) * (prev1.y - prev2.y);
}

static bool in_interval(i64 a, i64 b, i64 p) {
    if(a > b) return in_interval(b, a, p);
    return a <= p && p <= b;
}

static bool in_segment(point a, point b, point p) {
    if(det(a, b, p) != 0) return false;
    if(a.x == b.x) return in_interval(a.y, b.y, p.y);
    return in_interval(a.x, b.x, p.x);
}

static u32 random(void) {
    const u64 MUL = 3202034522624059733, INC = 5340424991;
    static u64 state = 1;
    state = ((state * MUL) + INC);
    return state >> 32;
}

static u64 random64(void) {
    return (((u64)random()) << 32) | random();
}

static point random_distant_point(point center, i64 len) {
    double rand_frac = (double)random64() / (double)UINT64_MAX;
    double deg_angle = 360 * rand_frac;
    double rad_angle = deg_angle * 3.1415926535 / 180;
    // polar to cartesian
    double x = center.x + len * cos(rad_angle);
    double y = center.y + len * sin(rad_angle);
    return (point){(i64)x, (i64)y};
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
    poly[n] = poly[0];
    n++;

    point aabb_center = {(min_x + max_x) / 2, (min_y + max_y) / 2};
    i64 aabb_diag = sqrt((max_x - min_x) * (max_x - min_x) + (max_y - min_y) * (max_y - min_y)) + 10;

    i64 m;
    scanf(I64, &m);
    while(m--) {
        point p;
        scanf(I64 I64, &p.x, &p.y);
        if(p.x < min_x || p.x > max_x || p.y < min_y || p.y > max_y) {
            printf("OUTSIDE\n");
            continue;
        }
        point distant = {max_x + 1, max_y + 1};
        i64 count = 0;
        i64 restart_limit = n * 10;
        for(i64 i = 1;i < n;i++) {
            if(in_segment(poly[i - 1], poly[i], p)) {
                count = -1;
                break;
            }
            // the ray must not intersect the polygon vertices
            if(in_segment(p, distant, poly[i - 1]) || in_segment(p, distant, poly[i])) {
                restart_limit--;
                if(restart_limit <= 0) {
                    fprintf(stderr, "Too many restarts\n");
                    return 1;
                }
                distant = random_distant_point(aabb_center, aabb_diag);
                i = 0;
                count = 0;
                continue;
            }
            point A_1 = p;
            point A_2 = distant;
            point B_1 = poly[i - 1];
            point B_2 = poly[i];
            // in order for two segments to intersect, A_1 and A_2 must be on different sides of B_1B_2, AND the other way around
            i64 ori_1 = det(B_1, B_2, A_1);
            i64 ori_2 = det(B_1, B_2, A_2);
            i64 ori_3 = det(A_1, A_2, B_1);
            i64 ori_4 = det(A_1, A_2, B_2);
            count += ((ori_1 >= 0) != (ori_2 >= 0)) && ((ori_3 >= 0) != (ori_4 >= 0));
        }
        if(count == -1) {
            printf("BOUNDARY\n");
        } else if(count % 2) {
            printf("INSIDE\n");
        } else {
            printf("OUTSIDE\n");
        }
    }
}
