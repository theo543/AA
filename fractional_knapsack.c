#include <string.h>
#include <stdlib.h>
#include <stdio.h>

// Macro to crash if EXPR is false. EXPR is evaluated only once.
#define ASSERT(EXPR) do { if(!(EXPR)) { fprintf(stderr, "Assertion failed at line %d: %s\n", __LINE__, #EXPR); exit(1); } } while(0)

struct item {
    int weight;
    int value;
    double ratio;
};

static int comparator(const void *a_, const void *b_) {
    const struct item *a = (struct item*)a_, *b = (struct item*)b_;
    if(a->ratio > b->ratio) return -1;
    if(a->ratio < b->ratio) return 1;
    return 0;
}

struct variant {
    enum { INT, DOUBLE } tag;
    union {
        int int_val;
        double double_val;
    };
};

static struct variant fractional_knapsack(int max_weight, struct item *items, int len) {
    qsort(items, len, sizeof(struct item), comparator);

    int total_value = 0;
    int remaining_weight = max_weight;
    for(int item_index = 0;item_index < len;item_index++) {
        const struct item *item = items + item_index;
        if(item->weight <= remaining_weight) {
            remaining_weight -= item->weight;
            total_value += item->value;
        } else if(remaining_weight > 0) {
            double sliced_amount = ((double)remaining_weight / (double)item->weight) * (double)item->value;
            return (struct variant){.tag = DOUBLE, .double_val = sliced_amount + (double)total_value};
        } else {
            break;
        }
    }
    return (struct variant){.tag = INT, .int_val = total_value};
}

int main(void) {
    int len, max_weight;
    ASSERT(scanf("%d %d", &len, &max_weight) == 2);
    struct item *items = (struct item*) malloc(sizeof(struct item) * len);
    ASSERT(items != NULL);
    for(int i = 0;i < len;i++) {
        ASSERT(scanf("%d", &items[i].value) == 1);
    }
    for(int i = 0;i < len;i++) {
        ASSERT(scanf("%d", &items[i].weight) == 1);
        items[i].ratio = (double)items[i].value / (double)items[i].weight;
    }
    struct variant result = fractional_knapsack(max_weight, items, len);
    ASSERT(result.tag == INT || result.tag == DOUBLE);
    if(result.tag == DOUBLE) {
        ASSERT(printf("%.6lf\n", result.double_val) > 0);
    } else {
        ASSERT(printf("%d\n", result.int_val) > 0);
    }
    free(items);
}
