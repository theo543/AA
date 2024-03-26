#include <limits.h>
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
#define MAX_INPUT_LINE_LEN 32

static inline void read_two_ints(int *a, int *b) {
    ASSERT(a != NULL);
    char line[MAX_INPUT_LINE_LEN + 1];
    ASSERT(fgets(line, MAX_INPUT_LINE_LEN + 1, stdin) == line);
    char *endptr;
    *a = strtol(line, &endptr, 10);
    ASSERT(*a != LONG_MIN && *a != LONG_MAX);
    ASSERT(endptr != NULL && endptr > line);
    if(b != NULL) {
        ASSERT(*endptr == ' ');
        char *mid = endptr;
        *b = strtol(mid, &endptr, 10);
        ASSERT(*b != LONG_MIN && *b != LONG_MAX);
        ASSERT(endptr != NULL && endptr > mid);
    }
    ASSERT(*endptr == '\r' || *endptr == '\n' || *endptr == '\0');
}

static void read_intervals(int *intervals_end, int *intervals_index) {
    int intervals;
    read_two_ints(&intervals, NULL);
    ASSERT(0 < intervals && intervals <= MAX_INTERVALS);
    for(int x = 0, interval_begin, interval_end;x < intervals;x++) {
        read_two_ints(&interval_begin, &interval_end);
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
    // We track the rightmost positions scanned and reachable.
    // Everything to the left (inclusive) of reachable has been covered by intervals picked so far.
    // Scan is the next position to scan for an interval that might be picked to extend beyond reachable.
    // These aren't the same, since it's OK for intervals to overlap.
    // Ex. after picking [0, 10], that doesn't mean we couldn't then pick [1, 100000], even though they overlap.
    // After picking an interval, we don't jump to the end of it, we still scan everything in between.
    // This is a pseudo-polynomial algorithm, but with the fixed input constraints, it's fine.
    // If intervals has to be lines up, e.g. [0, 10], [11, 100], [101, 100000], then scan and reachable would be the same.
    int scan = 0;
    // Initialized at cover_start - 1 because we don't need to cover positions before cover_start, so we can treat them as already covered.
    // This might equal -1 if cover_start is 0, but that's fine, scan will still be 0, so we won't actually access invalid memory.
    int reachable = cover_start - 1;
    int chosen = 0;
    while(reachable < cover_end) {
        int best = reachable;
        int best_index = 0;
        // The intervals don't have to overlap, i.e. we can have [1, 10], [11, 20], [21, 30], etc, not necessarily [1, 10], [10, 20], [20, 30], etc.
        // So we scan up to reachable + 1, not just up to reachable.
        while(scan <= (reachable + 1)) {
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
    read_two_ints(&to_cover_begin, &to_cover_end);
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
