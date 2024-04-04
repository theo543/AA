/*
 Approximation Algorithms Homework - Knapsack
  a)
   Implement and justify an optimal 0-1 knapsack algorithm in C, with pseudo-polynomial time complexity.
   Specify the time and space complexity.
  b)
   Implement a 2-approximation 0-1 knapsack algorithm with O(n) time complexity and O(1) space complexity.
   Weight is equal to value, all items can fit in the knapsack.
*/

#include <limits.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <time.h>

// Macro to crash if EXPR is false. EXPR is evaluated only once.
#define ASSERT(EXPR)\
do {\
    if(EXPR) break;\
    fprintf(stderr, "Assertion failed at line %d: %s\n", __LINE__, #EXPR);\
    exit(EXIT_FAILURE);\
} while(0)

// Helper functions. The compiler will inline these on release mode.
static int max(int a, int b) { return a > b ? a : b; }
static int min(int a, int b) { return a < b ? a : b; }
static void swap_ptrs(int **a, int **b) { int *tmp = *a; *a = *b; *b = tmp; }

/*
 Finds the optimal solution to the discrete knapsack problem, with weight = value.
 Only the value is returned, the solution is not reconstructed.
 Time complexity is O(n * W), space complexity is O(W).
 This is pseudo-polynomial because W depends on the value of the input, not the length.
 (If W has b bits, it can go up to 2^b).
*/
static int knapsack_optimal(int max_weight, int len, const int *weights) {
    /*
     We will solve the problem with dynamic programming.
     The table DP has (len + 1) rows and (max_weights + 1) columns.
     DP[i][w] is the optimal solution using only the first i items and at most w weight.
     For all i and w:

      - DP[i][w] = 0 if i = 0
        This is the base case. No items are in the knapsack.

      - DP[i][w] = DP[i - 1][w] | if weights[i] > w
        The i-th item is irrelevant to DP[i][w], so it's the same as DP[i - 1][w].

      - DP[i][w] = max(DP[i - 1][w], DP[i - 1][w - weights[i]] + weights[i])
        It's possible the i-th item is in the solution for DP[i][w].
        If it isn't, then the answer is the same as the previous case.
        If it is, we are left with a subproblem using the remaining weight.
        The previous row gives the answer for the subproblem, which is added to the item's value.

     We can prove this is correct by induction.
     The base case is trivial, the first row will be initialized to 0.
     If we correctly calculated DP for i - 1, we can calculate DP for i using the formula.
     Therefore the conditions for induction are satisfied.
     So, DP[len][max_weights] contains the best solution, considering all the items, and the entire sack.
    */

    int row_length = max_weight + 1;
    int row_bytes = sizeof(int) * row_length;
    /*  
     As an optimization, only store two rows at a time, since the recurrence formula only uses the previous row.
     If we wanted to reconstruct the solution, the space complexity would be O(n * W), but we don't need to do that.
     This is the only allocation in this function, so space complexity is O(W).
    */
    int *memory = (int*) malloc(row_bytes * 2);
    ASSERT(memory != NULL);
    int *prev = memory;
    int *current = memory + row_length;

    // Initialize the first row to 0 (base case).
    memset(prev, 0, row_bytes);

    // This is the main loop of the algorithm. The inner loops have W iterations in total, and the outer loop has n iterations, so this is O(n * W).
    for(int item = 1;item <= len;item++) {
        int item_weight = weights[item - 1];
        // For DP[i][w] where w < item_weight, we cannot use this item, so we use the previous value.
        for(int weight = 0; weight <= item_weight; weight++) {
            current[weight] = prev[weight];
        }
        // For DP[i][w] where w >= item_weight, we can use this item, or we could not, so we do whichever is better.
        for(int weight = item_weight;weight <= max_weight;weight++) {
            current[weight] = max(prev[weight], prev[weight - item_weight] + item_weight);
        }
        // Swap the pointers, in the next iteration the current row will be the previous row.
        swap_ptrs(&prev, &current);
    }

    // Before freeing the memory, save the result.
    // The last row will be in prev, since we swapped the pointers after the last iteration.
    int final_result = prev[max_weight];
    free(memory);
    return final_result;
}

// qsort comparator for descending order.
// We need this because sorting in C is HORRIBLE.
static int comparator(const void *a_, const void *b_) {
    int a = *(int*)a_, b = *(int*)b_;
    if(a == b) return 0;
    return a > b ? -1 : 1;
}

/*
 Finds a solution at least 1/2 as good as the optimal knapsack algorithm.
 The solution is not reconstructed, though that wouldn't change the space complexity in this case.
 Time complexity is O(n log n) due to sorting.
 If the input were already sorted, time complexity would be O(n).
 This mutates the weights input array, which is why space complexity is O(1).
*/
static int knapsack_approximation(int max_weight, int len, int *weights) {
    /*
     The approximation is much faster than the optimal solution, we just need a greedy algorithm.
     The items must be sorted in descending order to pick the best ones first.
     We do not assume that the input has already been sorted.
     This is the source of the O(n log n) time complexity.
     Could be made O(n) with radix sort, I think.
    */

    qsort(weights, len, sizeof(int), comparator);

    // We will be adding items in order until remaining_weight is too low to take the next item.
    // This is the only loop, with len iterations, so the algorithm is O(n).
    int solution = 0;
    int remaining_weight = max_weight;
    for(int item = 0;item < len;item++) {
        int item_weight = weights[item];
        if(remaining_weight >= item_weight) {
            // We can take the item.
            remaining_weight -= item_weight;
            solution += item_weight;
        } else {
            // We're out of space.
            // We don't need to keep going, this is enough for 1/2 approximation.
            break;
        }
    }
    return solution;
}

void run_test(int *memory, int max_len, int max_max_weight, int max_value) {
    // Note: When testing, compile with -ftrapv -fsanitize=address,undefined to insert runtime checks for UB.
    // TODO: don't use rand()
    int max_weight = rand() % max_max_weight + 1;
    int len = rand() % max_len + 1;
    for(int x = 0;x < len;x++) {
        memory[x] = rand() % min(max_value, max_weight) + 1;
    }
    int optimal = knapsack_optimal(max_weight, len, memory);
    int approximation = knapsack_approximation(max_weight, len, memory);
    ASSERT(approximation * 2 >= optimal);
}

int main(void) {
    srand(time(NULL));
    int memory[1000];
    for(int tests = 1;tests <= INT_MAX;tests++) {
        ASSERT(printf("Test %d.\n", tests) > 0);
        run_test(memory, 1000, 1000, 100);
    }
}
