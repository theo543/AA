#include <string.h>
#include <stdlib.h>
#include <stdio.h>

// Macro to crash if EXPR is false. EXPR is evaluated only once.
#define ASSERT(EXPR) do { if(!(EXPR)) { fprintf(stderr, "Assertion failed at line %d: %s\n", __LINE__, #EXPR); exit(1); } } while(0)

// An item has a weight and a value. Ratio is cached to avoid recalculating it O(n log n) times.
struct item {
    int weight;
    int value;
};

// Comparator for qsort. Sorts in descending order of value/weight ratio.
static int comparator(const void *a_, const void *b_) {
    // Undo qsort type erasure. Ugly, but we don't have templates.
    const struct item *a = (struct item*)a_, *b = (struct item*)b_;
    // Values and weights are small, so the multiplication won't overflow.
    if(a->value * b->weight > b->value * a->weight) return -1;
    if(a->value * b->weight < b->value * a->weight) return 1;
    return 0;
}

// I don't want to show decimal places if we didn't slice any items, so I used a small tagged union.
// In C++ this would be std::variant<int, float>.
struct variant {
    enum { INT, FLOAT } tag;
    union {
        int int_val;
        float float_val;
    };
};

// Finds the optimal solution to the fractional knapsack problem.
// Only the value is returned, the solution is not reconstructed.
// Time complexity is O(n log n), space complexity is O(1).
// Though, in this case, returning the full solution wouldn't change the time complexity.
// Important: items will be mutated by this algorithm!
// If modifying the input is not allowed, space complexity would be O(n) instead.
static struct variant fractional_knapsack(int max_weight, struct item *items, int len) {
    // Fractional knapsack is easier to solve, we just need a greedy algorithm.
    // Since we can slice items, taking an item with high ratio will never screw us over later.
    // If no item is sliced, the solution will be an integer, otherwise it may have decimal places so we use a float.

    // The items must be sorted in descending order of value/weight ratio.
    // We do not assume that the input has already been sorted.
    // C sorting is ugly :(
    qsort(items, len, sizeof(struct item), comparator);

    // We will be adding items to accumulate value until remaining_weight is too low to take the next item.
    int accumulated_value = 0;
    int remaining_weight = max_weight;
    for(int item_index = 0;item_index < len;item_index++) {
        // Give this a more readable name.
        const struct item *item = items + item_index;
        if(item->weight <= remaining_weight) {
            // We can take the whole item.
            remaining_weight -= item->weight;
            accumulated_value += item->value;
        } else if(remaining_weight > 0) {
            // We can slice the item.
            // Calculate the value of the sliced amount.
            float sliced_amount = ((float)remaining_weight / (float)item->weight) * (float)item->value;
            // Return the accumulated value plus the sliced item value, as a float.
            return (struct variant){.tag = FLOAT, .float_val = sliced_amount + (float)accumulated_value};
        } else {
            // We can't slice the item.
            break;
        }
    }
    // We either took all items or ran out of weight and couldn't slice the item.
    // No slicing occurred, so there is no need for decimal places.
    // Return the accumulated value as an int, so that it will be printed without decimal places.
    return (struct variant){.tag = INT, .int_val = accumulated_value};
}

int main(void) {
    // Driver code to handle I/O.
    int len, max_weight;
    ASSERT(scanf("%d %d", &len, &max_weight) == 2);
    struct item *items = (struct item*) malloc(sizeof(struct item) * len);
    ASSERT(items != NULL);
    for(int i = 0;i < len;i++) {
        ASSERT(scanf("%d", &items[i].value) == 1);
    }
    for(int i = 0;i < len;i++) {
        ASSERT(scanf("%d", &items[i].weight) == 1);
    }
    struct variant result = fractional_knapsack(max_weight, items, len);
    ASSERT(result.tag == INT || result.tag == FLOAT);
    if(result.tag == FLOAT) {
        ASSERT(printf("%.6lf\n", result.float_val) > 0);
    } else {
        ASSERT(printf("%d\n", result.int_val) > 0);
    }
    free(items);
}
