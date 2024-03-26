#include <string.h>
#include <stdlib.h>
#include <stdio.h>

#define ASSERT(EXPR)\
do {\
    if(EXPR) break;\
    fprintf(stderr, "Assertion failed at line %d: %s\n", __LINE__, #EXPR);\
    exit(EXIT_FAILURE);\
} while(0)

#define MAX_INTERVAL_END 200000
#define TRANSLATION_OFFSET 100000
#define MAX_INTERVALS 100000

static void read_intervals(int *intervals_end, int *intervals_index) {
    int intervals;
    ASSERT(scanf("%d", &intervals) == 1);
    ASSERT(0 < intervals && intervals <= MAX_INTERVALS);
    for(int x = 0, interval_begin, interval_end;x < intervals;x++) {
        ASSERT(scanf("%d %d", &interval_begin, &interval_end) == 2);
        ASSERT(interval_begin < interval_end);
        interval_begin += TRANSLATION_OFFSET;
        interval_end += TRANSLATION_OFFSET;
        ASSERT(interval_begin <= MAX_INTERVAL_END);
        ASSERT(interval_end <= MAX_INTERVAL_END);
        if(interval_end > intervals_end[interval_begin]) {
            intervals_end[interval_begin] = interval_end;
            intervals_index[interval_begin] = x + 1;
        }
    }
}

static int choose_intervals(const int *intervals_end, const int *intervals_index, int *chosen_intervals, int cover_start, int cover_end) {
    int scan = 0;
    int reachable = cover_start;
    int chosen = 0;
    while(reachable < cover_end) {
        int best = reachable;
        int best_index = 0;
        while(scan <= reachable) {
            if(intervals_end[scan] > best) {
                best = intervals_end[scan];
                best_index = intervals_index[scan];
            }
            scan++;
        }
        if(best == reachable) {
            return 0;
        }
        reachable = best;
        chosen_intervals[chosen] = best_index;
        chosen++;
    }
    return chosen;
}

int main(void) {
    static int intervals_end[MAX_INTERVAL_END + 1];
    static int intervals_index[MAX_INTERVAL_END + 1];
    static int chosen_intervals[MAX_INTERVALS];

    int to_cover_begin, to_cover_end;
    ASSERT(scanf("%d %d", &to_cover_begin, &to_cover_end) == 2);
    ASSERT(to_cover_begin < to_cover_end);
    to_cover_begin += TRANSLATION_OFFSET;
    to_cover_end += TRANSLATION_OFFSET;

    read_intervals(intervals_end, intervals_index);

    int chosen_len = choose_intervals(intervals_end, intervals_index, chosen_intervals, to_cover_begin, to_cover_end);

    printf("%d\n", chosen_len);
    if(chosen_len > 0) {
        printf("%d", chosen_intervals[0]);
        for(int x = 1;x < chosen_len;x++) {
            printf(" %d", chosen_intervals[x]);
        }
        printf("\n");
    }
}
