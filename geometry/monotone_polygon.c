#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <inttypes.h>

typedef int32_t i32;
#define I32 "%" PRId32

typedef struct point { i32 x; i32 y; } point;

#define MAX_POINTS 1000000

bool is_y_monotone(const point *polygon, i32 polygon_len) {
    int highest_index = 0;
    int highest_y = polygon[0].y;
    for(int i = 1;i < polygon_len;i++) {
        if(polygon[i].y > highest_y) {
            highest_y = polygon[i].y;
            highest_index = i;
        }
    }
    bool ascending = false;
    int current_index = highest_index;
    while(true) {
        int prev_y = polygon[current_index].y;
        current_index = (current_index + 1) % polygon_len;
        int current_y = polygon[current_index].y;
        if(ascending && current_y < prev_y) return false;
        if(current_y > prev_y) ascending = true;
        if(current_index == highest_index) return true;
    }
}

bool is_x_monotone(const point *polygon, i32 polygon_len) {
    int highest_index = 0;
    int highest_x = polygon[0].x;
    for(int i = 1;i < polygon_len;i++) {
        if(polygon[i].x > highest_x) {
            highest_x = polygon[i].x;
            highest_index = i;
        }
    }
    bool ascending = false;
    int current_index = highest_index;
    while(true) {
        int prev_x = polygon[current_index].x;
        current_index = (current_index + 1) % polygon_len;
        int current_x = polygon[current_index].x;
        if(ascending && current_x < prev_x) return false;
        if(current_x > prev_x) ascending = true;
        if(current_index == highest_index) return true;
    }
}


int main(void) {
    static point polygon[MAX_POINTS];
    i32 polygon_len;

    scanf(I32, &polygon_len);
    for(int x = 0;x < polygon_len;x++) {
        scanf(I32 I32, &polygon[x].x, &polygon[x].y);
    }

    bool x_monotone = is_x_monotone(polygon, polygon_len);
    bool y_monotone = is_y_monotone(polygon, polygon_len);

    const char *result[] = { "NO", "YES" };
    puts(result[x_monotone]);
    puts(result[y_monotone]);
}
