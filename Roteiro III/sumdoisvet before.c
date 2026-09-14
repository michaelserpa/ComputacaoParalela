
#include <omp.h>
#include <stdio.h>
#include <omp.h>

double a[100000], b[100000];

int main (int argc, char *argv[]) 
{
    int   i, n;
    double sum;
    double starttime, stoptime;

    starttime = omp_get_wtime(); 

    omp_set_num_threads(2);

    n = 100000;

    for (i=0; i < n; i++)
        a[i] = b[i] = i/10 * 1.0;
    
    sum = 0.0;

    #pragma omp parallel for 

    for (i=0; i < n; i++)
        sum = sum + (a[i] * b[i]);

    printf("\nSum = %f\n",sum);

    stoptime = omp_get_wtime();
	
    printf("\nTempo de execucao: %3.2f segundos\n\n", stoptime-starttime);

    return(0);
}