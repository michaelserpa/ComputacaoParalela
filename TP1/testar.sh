#!/usr/bin/env bash
set -euo pipefail

saida_sequencial=$(./buscador_sequencial OpenMP)
saida_paralela=$(OMP_NUM_THREADS=4 OMP_SCHEDULE=dynamic,1 ./buscador OpenMP)

total_sequencial=$(printf '%s\n' "$saida_sequencial" | awk '/^Total:/ {print $2}')
total_paralelo=$(printf '%s\n' "$saida_paralela" | awk '/^Total:/ {print $2}')

if [[ $total_sequencial != "$total_paralelo" ]]; then
    echo "Erro: os resultados sequencial e paralelo sao diferentes." >&2
    exit 1
fi

printf 'Sequencial: %s ocorrencias\n' "$total_sequencial"
printf 'Paralelo:   %s ocorrencias\n' "$total_paralelo"
echo "Teste concluido com sucesso."
