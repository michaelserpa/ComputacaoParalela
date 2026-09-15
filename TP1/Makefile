CC = gcc
CFLAGS = -O2 -std=c11 -Wall -Wextra -Wpedantic -fopenmp

.PHONY: all clean test

all: buscador_sequencial buscador

buscador_sequencial: buscador_sequencial.c
	$(CC) $(CFLAGS) $< -o $@

buscador: buscador_paralelo.c
	$(CC) $(CFLAGS) $< -o $@

test: all
	./testar.sh

clean:
	rm -f buscador buscador_sequencial
