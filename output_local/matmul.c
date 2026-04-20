#include <stdlib.h>
#include <stdio.h>
#include <time.h>

#define N 1024


// N=1024，double，避免编译优化把循环删掉
double A[N][N], B[N][N], C[N][N];

void init() {
    for (int i = 0; i < N; i++) { 
        for (int j = 0; j < N; j++) {
            A[i][j] = (double)rand() / RAND_MAX;
            B[i][j] = (double)rand() / RAND_MAX;
            C[i][j] = 0.0;
        }
    }
}

void matmul() {
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            double sum = 0.0;
            for (int k = 0; k < N; k++) {
                sum += A[i][k] * B[k][j];
            }
            C[i][j] = sum;
        }
    }
}

int main() {
    init();
    clock_t start = clock();
    matmul();
    clock_t end = clock();
    double time_spent = (double)(end - start) / CLOCKS_PER_SEC;
    printf("%f\n", time_spent);
    return 0;
}
