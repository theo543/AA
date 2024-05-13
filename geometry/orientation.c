#include <stdio.h>
#include <stdint.h>
#include <inttypes.h>

typedef int64_t i64;
#define I64 "%" PRId64

int main(void) {
    i64 t;
    scanf(I64, &t);
    while(t--) {
        i64 px, py, qx, qy, rx, ry;
        scanf(I64 I64 I64 I64 I64 I64, &px, &py, &qx, &qy, &rx, &ry);
        i64 det = (qx - px) * (ry - py) - (rx - px) * (qy - py);
        if(det == 0) {
            printf("TOUCH\n");
        } else if(det > 0) {
            printf("LEFT\n");
        } else {
            printf("RIGHT\n");
        }
    }
}
