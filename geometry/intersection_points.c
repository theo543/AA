#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <inttypes.h>

#define MAX_SEGMENTS 100000
#define MAX_ABSOLUTE_COORD 1000000
#define TOTAL_COORDS (MAX_ABSOLUTE_COORD * 2 + 1)
#define LAST_COORD (TOTAL_COORDS - 1)

typedef int32_t i32;
typedef int64_t i64;
#define I32 "%" PRId32
#define I64 "%" PRId64

static i32 max(i32 a, i32 b) {
    return a > b ? a : b;
}

static i32 min(i32 a, i32 b) {
    return a < b ? a : b;
}

typedef struct event {
    i32 height;
    i32 horizontal_begin;
    i32 horizontal_end;
    enum event_type { START_VERTICAL = 0, HORIZONTAL = 1, END_VERTICAL = 2 } type;
} event;

static int compare_events(const void *event_a, const void *event_b) {
    const event *a = event_a;
    const event *b = event_b;
    if(a->height != b->height) return a->height - b->height;
    return a->type - b->type;
}

static i32 left(i32 node) {
    return node * 2;
}

static i32 right(i32 node) {
    return node * 2 + 1;
}

static i32 segment_tree_query(i32 *array, i32 node, i32 node_left, i32 node_right, i32 query_left, i32 query_right) {
    if(node_left == query_left && node_right == query_right) {
        return array[node];
    }
    i32 midpoint = (node_left + node_right) / 2;
    if(query_right <= midpoint) {
        return segment_tree_query(array, left(node), node_left, midpoint, query_left, query_right);
    } else if(query_left > midpoint) {
        return segment_tree_query(array, right(node), midpoint + 1, node_right, query_left, query_right);
    } else {
        i32 left_sum = segment_tree_query(array, left(node), node_left, midpoint, query_left, midpoint);
        i32 right_sum = segment_tree_query(array, right(node), midpoint + 1, node_right, midpoint + 1, query_right);
        return left_sum + right_sum;
    }
}

static void segment_tree_add(i32 *array, i32 node, i32 node_left, i32 node_right, i32 add_index, i32 add_value) {
    if(node_left == node_right) {
        array[node] += add_value;
        return;
    }
    i32 midpoint = (node_left + node_right) / 2;
    if(add_index <= midpoint) {
        segment_tree_add(array, left(node), node_left, midpoint, add_index, add_value);
    } else {
        segment_tree_add(array, right(node), midpoint + 1, node_right, add_index, add_value);
    }
    array[node] = array[left(node)] + array[right(node)];
}

int main(void) {
    static event events[MAX_SEGMENTS * 2];
    // first element is unused, array is 1-indexed because the root node of segment tree needs to be at index 1, since left(0) == 0
    static i32 segment_tree[TOTAL_COORDS * 4 + 1];
    i32 events_len = 0;
    i32 n;
    scanf(I32, &n);
    while(n--) {
        i32 x_a, y_a, x_b, y_b;
        scanf(I32 I32 I32 I32, &x_a, &y_a, &x_b, &y_b);
        x_a += MAX_ABSOLUTE_COORD;
        y_a += MAX_ABSOLUTE_COORD;
        x_b += MAX_ABSOLUTE_COORD;
        y_b += MAX_ABSOLUTE_COORD;
        // line endpoints are not counted for intersections
        if(x_a == x_b) {
            i32 y_begin = min(y_a, y_b);
            i32 y_end = max(y_a, y_b);
            y_begin++;
            y_end--;
            if(y_begin > y_end) continue;
            events[events_len++] = (event){y_begin, x_a, x_a, START_VERTICAL};
            events[events_len++] = (event){y_end, x_a, x_a, END_VERTICAL};
        } else if(y_a == y_b) {
            i32 x_begin = min(x_a, x_b);
            i32 x_end = max(x_a, x_b);
            x_begin++;
            x_end--;
            if(x_a > x_b) continue;
            events[events_len++] = (event){y_a, x_begin, x_end, HORIZONTAL};
        } else {
            fprintf(stderr, "Line must be horizontal or vertical\n");
            return 1;
        }
    }
    qsort(events, events_len, sizeof(event), compare_events);
    i64 intersections = 0;
    for(int x = 0;x < events_len;x++) {
        if(events[x].type == HORIZONTAL) {
            i32 inter = segment_tree_query(segment_tree, 1, 0, LAST_COORD, events[x].horizontal_begin, events[x].horizontal_end);
            intersections += inter;
        } else {
            i32 add_value = events[x].type == START_VERTICAL ? 1 : -1;
            segment_tree_add(segment_tree, 1, 0, LAST_COORD, events[x].horizontal_begin, add_value);
        }
    }
    printf(I64 "\n", intersections);
}
