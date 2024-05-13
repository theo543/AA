#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdbool.h>
#include <inttypes.h>

typedef int64_t i64;
#define I64 "%" PRId64
#define MAX_POINTS 100000

typedef struct point { i64 x, y; } point;

static i64 det(point prev2, point prev1, point this) {
    return (prev1.x - prev2.x) * (this.y - prev2.y) - (this.x - prev2.x) * (prev1.y - prev2.y);
}

int main(void) {
    i64 n;
    scanf(I64, &n);
    static point tmp[MAX_POINTS];
    for(i64 i = 0;i < n;i++) {
        scanf(I64 I64, &tmp[i].x, &tmp[i].y);
    }
    i64 leftmost_bottom = 0;
    for(i64 i = 1;i < n;i++) {
        if(tmp[i].y < tmp[leftmost_bottom].y || (tmp[i].y == tmp[leftmost_bottom].y && tmp[i].x < tmp[leftmost_bottom].x)) {
            leftmost_bottom = i;
        }
    }
    static point points[MAX_POINTS];
    memcpy(points, tmp + leftmost_bottom, (n - leftmost_bottom) * sizeof(point));
    memcpy(points + n - leftmost_bottom, tmp, leftmost_bottom * sizeof(point));
    i64 stack_ptr = 1;
    for(i64 next_read_ptr = 2;next_read_ptr < n;next_read_ptr++) {
        while(stack_ptr != 0 && det(points[stack_ptr - 1], points[stack_ptr - 0], points[next_read_ptr]) <= 0) {
            stack_ptr--;
        }
        stack_ptr++;
        points[stack_ptr] = points[next_read_ptr];
    }
    while(stack_ptr != 0 && det(points[stack_ptr - 1], points[stack_ptr - 0], points[0]) <= 0) {
        stack_ptr--;
    }
    printf(I64 "\n", stack_ptr + 1);
    for(i64 i = 0;i <= stack_ptr;i++) {
        printf(I64 " " I64 "\n", points[i].x, points[i].y);
    }
}
