#include <string.h>
#include <stdlib.h>
#include <stdio.h>

// Macro to crash if EXPR is false. EXPR is evaluated only once.
#define ASSERT(EXPR) do { if(!(EXPR)) { fprintf(stderr, "Assertion failed at line %d: %s\n", __LINE__, #EXPR); exit(1); } } while(0)

// Helper functions. The compiler will inline these on release mode.
static int max(int a, int b) { return a > b ? a : b; }
static int min(int a, int b) { return a < b ? a : b; }
static void swap_ptrs(int **a, int **b) { int *tmp = *a; *a = *b; *b = tmp; }

// Finds the optimal solution to the knapsack problem.
// Only the value is returned, the solution is not reconstructed.
// Time complexity is O(n * W), space complexity is O(W).
// This is pseudo-polynomial because W depends on the value of the input, not the length (if W has b bits, it can go up to 2^b).
static int knapsack_optimal(int max_weight, int len, const int *weights, const int *values) {
    // We will solve the problem with dynamic programming.
    // DP[i][w] is the optimal solution with at most i items and at most w weight.
    // DP[i][w] = 0 if i = 0
    // DP[i][w] = DP[i - 1][w] if weights[i] > w (because the item is too heavy)
    // DP[i][w] = max(DP[i - 1][w], DP[i - 1][w - weights[i]] + values[i]) otherwise (if we choose the item we will add it to the previous optimal solution)
    // We can prove this is correct by induction.
    // The base case is trivial, the first row will be initialized to 0.
    // If we correctly calculated DP for i - 1, we can calculate DP for i using the formula.
    // Therefore the conditions for induction are satisfied, so DP[len][max_weight] contains the optimal solution.

    // DP table is 2D, each row contains max_weight + 1 elements (from 0 to max_weight inclusive).
    int row_size = max_weight + 1;
    int row_bytes = sizeof(int) * row_size;
    // Because the formula only refers to the previous row, we only need to keep 2 rows in memory at a time.
    // If we wanted to reconstruct the solution, the space complexity would be O(n * W), but we don't need to do that.
    // This is the only allocation in this function, so space complexity is O(W).
    int *memory = (int*) malloc(row_bytes * 2);
    ASSERT(memory != NULL);
    int *prev = memory;
    int *current = memory + row_size;

    // Initialize the first row to 0 (base case).
    memset(prev, 0, row_bytes);

    // This is the main loop of the algorithm. The inner loops have W iterations in total, and the outer loop has n iterations, so this is O(n * W).
    for(int item = 1;item <= len;item++) {
        // For clarity, assign these values to variables. It makes no difference to the performance.
        int item_weight = weights[item - 1];
        int item_value = values[item - 1];
        // For DP[i][w] where w < item_weight, we cannot use this item, so we use the previous value.
        // For the case where item_weight >= max_weight, we want to loop over the entire row, skipping the item that doesn't fit.
        // This is not necessary for the homework, but I wanted to test this solution on GeeksForGeeks, and they include items that don't fit in the knapsack.
        for(int weight = 0; weight <= min(max(item_weight - 1, 0), max_weight); weight++) {
            current[weight] = prev[weight];
        }
        // For DP[i][w] where w >= item_weight, we can use this item, so we do whatever is better.
        for(int weight = item_weight;weight <= max_weight;weight++) {
            current[weight] = max(prev[weight], prev[weight - item_weight] + item_value);
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

int main(void) {
    // Driver code to handle I/O.
    // Constraints:
    // 1 <= n (len) <= 1000
    // 1 <= W (max_weight) <= 1000
    // 1 <= weights[i] <= 100
    // 1 <= values[i] <= 100
    int len, max_weight;
    ASSERT(scanf("%d %d", &len, &max_weight) == 2);
    int *input_memory = (int*) malloc(sizeof(int) * len * 2);
    ASSERT(input_memory != NULL);
    int *weights = input_memory;
    int *values = input_memory + len;
    for(int i = 0;i < len;i++) {
        ASSERT(scanf("%d", &values[i]) == 1);
    }
    for(int i = 0;i < len;i++) {
        ASSERT(scanf("%d", &weights[i]) == 1);
    }
    int result = knapsack_optimal(max_weight, len, weights, values);
    ASSERT(printf("%d\n", result) > 0);
    free(input_memory);
}
