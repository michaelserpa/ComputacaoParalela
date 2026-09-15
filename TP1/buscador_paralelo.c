#define _DEFAULT_SOURCE

#include <dirent.h>
#include <inttypes.h>
#include <omp.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define DIRETORIO_TEXTOS "textos"

static int arquivo_txt(const struct dirent *entrada) {
    size_t tamanho = strlen(entrada->d_name);
    return tamanho > 4 &&
           strcmp(entrada->d_name + tamanho - 4, ".txt") == 0;
}

static uint64_t buscar_no_arquivo(const char *caminho, const char *palavra) {
    FILE *arquivo = fopen(caminho, "r");
    if (arquivo == NULL) {
        fprintf(stderr, "Nao foi possivel abrir %s\n", caminho);
        return 0;
    }

    uint64_t ocorrencias = 0;
    size_t tamanho_palavra = strlen(palavra);
    char *linha = NULL;
    size_t capacidade = 0;

    while (getline(&linha, &capacidade, arquivo) != -1) {
        char *posicao = linha;
        while ((posicao = strstr(posicao, palavra)) != NULL) {
            ocorrencias++;
            posicao += tamanho_palavra;
        }
    }

    free(linha);
    fclose(arquivo);
    return ocorrencias;
}

int main(int argc, char *argv[]) {
    if (argc != 2 || argv[1][0] == '\0') {
        fprintf(stderr, "Uso: %s palavra\n", argv[0]);
        return EXIT_FAILURE;
    }

    struct dirent **arquivos;
    int quantidade = scandir(DIRETORIO_TEXTOS, &arquivos, arquivo_txt, alphasort);
    if (quantidade < 0) {
        fprintf(stderr, "Nao foi possivel abrir o diretorio %s\n",
                DIRETORIO_TEXTOS);
        return EXIT_FAILURE;
    }
    if (quantidade == 0) {
        fprintf(stderr, "Nenhum arquivo .txt encontrado em %s\n",
                DIRETORIO_TEXTOS);
        free(arquivos);
        return EXIT_FAILURE;
    }

    uint64_t *ocorrencias = calloc((size_t)quantidade, sizeof(*ocorrencias));
    if (ocorrencias == NULL) {
        fprintf(stderr, "Memoria insuficiente\n");
        return EXIT_FAILURE;
    }

    uint64_t total = 0;
    double inicio = omp_get_wtime();

    #pragma omp parallel for schedule(runtime) reduction(+:total)
    for (int i = 0; i < quantidade; i++) {
        char caminho[4096];
        snprintf(caminho, sizeof(caminho), "%s/%s",
                 DIRETORIO_TEXTOS, arquivos[i]->d_name);

        ocorrencias[i] = buscar_no_arquivo(caminho, argv[1]);
        total += ocorrencias[i];
    }

    double tempo = omp_get_wtime() - inicio;

    for (int i = 0; i < quantidade; i++) {
        printf("%s: %" PRIu64 " ocorrencia(s)\n",
               arquivos[i]->d_name, ocorrencias[i]);
    }
    printf("Total: %" PRIu64 " ocorrencia(s)\n", total);
    printf("Threads: %d\n", omp_get_max_threads());
    printf("Tempo paralelo: %.6f segundos\n", tempo);

    for (int i = 0; i < quantidade; i++) {
        free(arquivos[i]);
    }
    free(arquivos);
    free(ocorrencias);
    return EXIT_SUCCESS;
}
