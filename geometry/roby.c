#include <stdio.h>
#include <stdint.h>
#include <inttypes.h>

typedef int32_t i32;
#define I32 "%" PRId32

int main(void) {
    i32 n;
    i32 left = 0, right = 0, touch = 0;
    scanf(I32, &n);
    i32 prev2_x, prev2_y, prev1_x, prev1_y, this_x, this_y;
    scanf(I32 I32 I32 I32, &prev2_x, &prev2_y, &prev1_x, &prev1_y);
    i32 p1_x = prev2_x, p1_y = prev2_y;
    for(i32 x = 2;x <= n;x++) {
        if(x < n) {
            scanf(I32 I32, &this_x, &this_y);
        } else {
            this_x = p1_x;
            this_y = p1_y;
        }
        i32 det = (prev1_x - prev2_x) * (this_y - prev2_y) - (this_x - prev2_x) * (prev1_y - prev2_y);
        if(det == 0) {
            touch++;
        } else if(det > 0) {
            left++;
        } else {
            right++;
        }
        prev2_x = prev1_x;
        prev2_y = prev1_y;
        prev1_x = this_x;
        prev1_y = this_y;
    }
    printf(I32 " " I32 " " I32 "\n", left, right, touch);
}
