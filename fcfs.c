#include <stdio.h>

int main() {
    int n, i;
    int burst[20], waiting[20], turnaround[20];
    float avg_wt = 0, avg_tat = 0;

    printf("Enter number of processes: ");
    scanf("%d", &n);

    // Input burst times
    printf("Enter Burst Time for each process:\n");
    for(i = 0; i < n; i++) {
        printf("P%d: ", i + 1);
        scanf("%d", &burst[i]);
    }

    // First process waiting time is 0
    waiting[0] = 0;

    // Calculate waiting time
    for(i = 1; i < n; i++) {
        waiting[i] = waiting[i - 1] + burst[i - 1];
    }

    // Calculate turnaround time
    for(i = 0; i < n; i++) {
        turnaround[i] = waiting[i] + burst[i];
    }

    // Display results
    printf("\nProcess\tBurst Time\tWaiting Time\tTurnaround Time\n");

    for(i = 0; i < n; i++) {
        printf("P%d\t%d\t\t%d\t\t%d\n",
               i + 1, burst[i], waiting[i], turnaround[i]);

        avg_wt += waiting[i];
        avg_tat += turnaround[i];
    }

    // Average calculations
    avg_wt /= n;
    avg_tat /= n;

    printf("\nAverage Waiting Time = %.2f", avg_wt);
    printf("\nAverage Turnaround Time = %.2f\n", avg_tat);

    return 0;
}
