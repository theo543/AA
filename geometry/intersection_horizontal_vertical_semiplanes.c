#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <inttypes.h>

typedef int32_t i32;
typedef int64_t i64;
#define I32 "%" PRId32

typedef struct rational {
    i32 num;
    i32 den;
} rational;

static bool lesser(rational a, rational b) {
    return (i64)a.num * (i64)b.den < (i64)b.num * (i64)a.den;
}

static rational min(rational a, rational b) {
    return lesser(a, b) ? a : b;
}

static rational max(rational a, rational b) {
    return lesser(a, b) ? b : a;
}

int main(void) {
    const i32 MAX_COORD = 10000000;
    i32 PLACEHOLDER = 2 * MAX_COORD;
    rational min_x = {-PLACEHOLDER, 1};
    rational max_x = {PLACEHOLDER, 1};
    rational min_y = {-PLACEHOLDER, 1};
    rational max_y = {PLACEHOLDER, 1};
    int n;
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
            max_x = min(max_x, (rational){-c, a});
        } else if (a < 0) {
            // x >= -c/a
            min_x = max(min_x, (rational){c, -a});
        } else if(b > 0) {
            // y <= -c/b
            max_y = min(max_y, (rational){-c, b});
        } else {
            // y >= -c/b
            min_y = max(min_y, (rational){c, -b});
        }
    }
    if(lesser(max_x, min_x) || lesser(max_y, min_y)) {
        printf("VOID\n");
    } else if(min_x.num == -PLACEHOLDER || max_x.num == PLACEHOLDER || min_y.num == -PLACEHOLDER || max_y.num == PLACEHOLDER) {
        printf("UNBOUNDED\n");
    } else {
        printf("BOUNDED\n");
    }
}
