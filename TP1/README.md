# TP1 - buscador de texto com OpenMP

O trabalho possui dois programas simples:

- `buscador_sequencial`: percorre os arquivos um por vez;
- `buscador`: distribui os arquivos entre threads usando OpenMP.

Os dois procuram nos arquivos `.txt` da pasta `textos`. A busca diferencia
maiusculas de minusculas e conta ocorrencias literais, sem sobreposicao.

## Compilar

Execute dentro da pasta `TP1`:

    make

## Executar

Versao sequencial:

    ./buscador_sequencial OpenMP

Versao paralela com quatro threads:

    OMP_NUM_THREADS=4 ./buscador OpenMP

O executavel paralelo aceita exatamente um argumento: a palavra procurada.
O numero de threads e configurado pela variavel padrao do OpenMP.

Para experimentar escalonadores e chunks sem alterar o programa:

    OMP_NUM_THREADS=4 OMP_SCHEDULE=static ./buscador OpenMP
    OMP_NUM_THREADS=4 OMP_SCHEDULE=dynamic,1 ./buscador OpenMP
    OMP_NUM_THREADS=4 OMP_SCHEDULE=guided,2 ./buscador OpenMP

Isso funciona porque a diretiva paralela usa `schedule(runtime)`.

## Testar

    make test

O teste executa as duas versoes e confirma que elas encontram o mesmo total.
Os oito textos pequenos incluidos servem apenas para verificar o funcionamento.
Para as medicoes do relatorio, podem ser adicionados outros arquivos pequenos
na pasta `textos`.
