#include <stdio.h>
#include <omp.h>

#define N 20

int main() {
	int i, soma = 0;
	omp_set_num_threads(4);	
	#pragma omp parallel for firstprivate(soma) lastprivate(soma)
	for(i=0; i<N; i++) {
		soma += i;
		if(i == ((omp_get_thread_num()+1)*(N/omp_get_num_threads())-1))
			printf("%d: %d\n", omp_get_thread_num(), soma);
	}
	printf("%d\n", soma);
	return 0;
}