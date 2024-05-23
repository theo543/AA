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

static bool in_segment(point a, point b, point p) {
    if(det(a, b, p) != 0) return false;
    i64 dot = (p.x - a.x) * (b.x - a.x) + (p.y - a.y) * (b.y - a.y);
    if(dot < 0) return false;
    i64 ba_squared = (b.x - a.x) * (b.x - a.x) + (b.y - a.y) * (b.y - a.y);    
    if(dot > ba_squared) return false;
    return true;
}

static u32 random(void) {
    const u64 MUL = 3202034522624059733, INC = 5340424991;
    static u64 state = 1;
    state = ((state * MUL) + INC);
    return state >> 32;
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
        i64 restart_count = 0;
        for(i64 i = 1;i < n;i++) {
            if(in_segment(poly[i - 1], poly[i], p)) {
                count = -1;
                break;
            }
            point A_1 = p;
            point A_2 = distant;
            point B_1 = poly[i - 1];
            point B_2 = poly[i];
            // segment intersection check using orientation
            // if any orientation returns 0 we randomly move the distant point and try again
            // in order for two segments to intersect, A_1 and A_2 must be on different sides of B_1B_2, AND the other way around
            i64 ori_1 = det(B_1, B_2, A_1);
            i64 ori_2 = det(B_1, B_2, A_2);
            i64 ori_3 = det(A_1, A_2, B_1);
            i64 ori_4 = det(A_1, A_2, B_2);
            if(ori_1 == 0 || ori_2 == 0 || ori_3 == 0 || ori_4 == 0) {
                restart_count++;
                if(restart_count > n * 2) {
                    fprintf(stderr, "Too many restarts\n");
                    return 1;
                }
                distant.x += random() % 1024;
                distant.y += random() % 1024;
                i = 0;
                count = 0;
                continue;
            }
            count += ((ori_1 > 0) != (ori_2 > 0)) && ((ori_3 > 0) != (ori_4 > 0));
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
