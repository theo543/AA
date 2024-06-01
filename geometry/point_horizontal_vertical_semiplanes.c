#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <inttypes.h>

typedef int32_t i32;
#define I32 "%" PRId32

#define MAX_SEMIPLANES 10000
#define MIN_COORD -1000000
#define MAX_COORD  1000000

static int double_cmp(const void *a, const void *b) {
    double diff = *((double*)a) - *((double*)b);
    if(diff < 0) return -1;
    if(diff > 0) return 1;
    return 0;
}

static double search_greater(double *array, i32 len, double x) {
    i32 l = 0;
    i32 r = len - 1;
    while(l != r) {
        i32 m = (l + r) / 2;
        if(array[m] <= x) {
            l = m + 1;
        } else {
            r = m;
        }
    }
    return array[l];
}

static double search_lesser(double *array, i32 len, double x) {
    i32 l = 0;
    i32 r = len - 1;
    while(l != r) {
        i32 m = (l + r + 1) / 2;
        if(array[m] < x) {
            l = m;
        } else {
            r = m - 1;
        }
    }
    return array[l];
}

int main(void) {
    static double  left_bounds[MAX_SEMIPLANES + 2] = {MIN_COORD - 1, MAX_COORD + 1};
    static double right_bounds[MAX_SEMIPLANES + 2] = {MIN_COORD - 1, MAX_COORD + 1};
    static double  down_bounds[MAX_SEMIPLANES + 2] = {MIN_COORD - 1, MAX_COORD + 1};
    static double    up_bounds[MAX_SEMIPLANES + 2] = {MIN_COORD - 1, MAX_COORD + 1};
    i32 left_count = 2;
    i32 right_count = 2;
    i32 down_count = 2;
    i32 up_count = 2;

    i32 n;
    scanf(I32, &n);
    while(n--) {
        // ax + by <= -c
        i32 a, b, c;
        scanf(I32 I32 I32, &a, &b, &c);

        if(a != 0 && b != 0) {
            fprintf(stderr, "Invalid input\n");
            return 1;
        }

        if(a > 0) {
            // x <= -c/a
            right_bounds[right_count++] = -c / (double)a;
        } else if (a < 0) {
            // -c/a <= x
            left_bounds[left_count++] = -c / (double)a;
        } else if(b > 0) {
            // y <= -c/b
            up_bounds[up_count++] = -c / (double)b;
        } else {
            // -c/b <= y
            down_bounds[down_count++] = -c / (double)b;
        }
    }

    qsort(left_bounds,  left_count,  sizeof(double), double_cmp);
    qsort(right_bounds, right_count, sizeof(double), double_cmp);
    qsort(down_bounds,  down_count,  sizeof(double), double_cmp);
    qsort(up_bounds,    up_count,    sizeof(double), double_cmp);

    i32 m;
    scanf(I32, &m);
    while(m--) {
        double x, y;
        scanf("%lf %lf", &x, &y);

        double left  = search_lesser (left_bounds,  left_count, x);
        double right = search_greater(right_bounds, right_count, x);
        double down  = search_lesser (down_bounds,  down_count, y);
        double up    = search_greater(up_bounds,    up_count, y);

        if(left == (MIN_COORD - 1) || right == (MAX_COORD + 1) || down == (MIN_COORD - 1) || up == (MAX_COORD + 1)) {
            printf("NO\n");
        } else {
            printf("YES\n%.6lf\n", (right - left) * (up - down));
        }
    }
}
