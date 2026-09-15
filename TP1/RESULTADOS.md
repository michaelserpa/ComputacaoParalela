# TP1 — busca paralela de texto em arquivos

## Identificação

- Disciplina: Computação Paralela
- Trabalho: TP1 — OpenMP
- Grupo: 11
- Aplicação: busca de uma palavra em múltiplos arquivos TXT
- Integrantes: preencher antes da entrega
- Coleta final: 14/09/2026, no LAD/PUCRS

## 1. Problema e paralelização

A aplicação procura uma palavra em todos os arquivos `.txt` da pasta `textos`.
A busca é literal, diferencia maiúsculas de minúsculas e não conta ocorrências
sobrepostas. O tempo medido inclui abertura, leitura, busca e fechamento dos
arquivos, mas não inclui a enumeração do diretório nem a impressão.

Os arquivos são independentes, portanto cada iteração pode ser executada por
uma thread diferente. A versão paralela usa:

```c
#pragma omp parallel for schedule(runtime) reduction(+:total)
```

`parallel for` distribui os arquivos; `schedule(runtime)` permite testar
escalonadores e chunks sem recompilar; e `reduction(+:total)` elimina a condição
de corrida no acumulador. Cada iteração escreve em uma posição exclusiva do
vetor de resultados, dispensando região crítica.

## 2. Ambiente

As medições foram realizadas em um nodo exclusivo, e não na hospedeira.

| Item | Valor |
|---|---|
| Cluster/nodo | Atlantica — `atlantica07` |
| CPU | Intel Xeon E5520 @ 2,27 GHz |
| Topologia | 2 soquetes, 4 núcleos por soquete |
| Total | 8 núcleos físicos, 16 threads lógicas |
| NUMA | 2 nodos |
| Cache L2/L3 | 2 MiB / 16 MiB |
| Compilador | GCC 9.4.0, `-O2 -fopenmp` |
| Slurm | job 37496, 16 CPUs por tarefa |
| Afinidade | `OMP_PROC_BIND=spread`, `OMP_PLACES=cores` |

Assim, até oito threads foram espalhadas pelos núcleos físicos. Com 16 threads,
cada núcleo executou duas threads de hardware (SMT).

## 3. Metodologia

Os oito arquivos originais eram pequenos demais para medições estáveis. Um
ensaio com milhares de arquivos de aproximadamente 100 bytes ficou dominado
pela abertura de arquivos no NFS e apresentou forte oscilação. Na coleta final,
cada arquivo-base foi expandido 1.024 vezes. Isso preservou diferenças de
tamanho e conteúdo e aumentou a granularidade do trabalho.

- alocação exclusiva de um nodo com 16 CPUs lógicas;
- validação das versões antes da coleta;
- aquecimento de cada corpus para reduzir o efeito de cache frio;
- 15 medições por configuração e mediana como valor principal;
- corpus forte fixo: 1.024 arquivos e 105.775.104 bytes;
- corpus fraco: 64 arquivos e 6.610.944 bytes por thread;
- threads: 1, 2, 4, 8 e 16;
- escalonadores: `static`, `dynamic` e `guided`;
- chunks: 1, 4 e 16.

As duas versões encontraram 786.432 ocorrências no corpus forte. As 780
medições finais estão em `resultados_lad.csv`; a descrição integral do nodo está
em `ambiente_lad.txt`.

## 4. Fórmulas

```text
Speed-up forte(p) = Tsequencial / Tparalelo(p)
Eficiência forte(p) = Speed-up(p) / p

Speed-up fraco escalado(p) = p × Tsequencial(base) / Tparalelo(p × base)
Eficiência fraca(p) = Tsequencial(base) / Tparalelo(p × base)
```

A referência é a implementação sequencial, não a versão OpenMP com uma thread.

## 5. Escalabilidade forte

Configuração principal: `static`, chunk 1.

| Versão | Threads | Mediana (ms) | Speed-up | Eficiência |
|---|---:|---:|---:|---:|
| Sequencial | 1 | 216,781 | 1,000 | 100,0% |
| OpenMP | 1 | 209,847 | 1,033 | 103,3% |
| OpenMP | 2 | 107,295 | 2,020 | 101,0% |
| OpenMP | 4 | 53,642 | 4,041 | 101,0% |
| OpenMP | 8 | 30,229 | 7,171 | 89,6% |
| OpenMP | 16 | 28,565 | 7,589 | 47,4% |

Dispersão das 15 execuções:

| Versão | Threads | Média (ms) | Desvio-padrão (ms) | Mínimo–máximo (ms) |
|---|---:|---:|---:|---:|
| Sequencial | 1 | 216,010 | 4,225 | 210,342–224,313 |
| OpenMP | 1 | 206,635 | 14,955 | 174,050–220,655 |
| OpenMP | 2 | 111,078 | 10,697 | 98,467–129,003 |
| OpenMP | 4 | 53,871 | 0,850 | 52,715–55,522 |
| OpenMP | 8 | 30,501 | 1,015 | 29,258–33,044 |
| OpenMP | 16 | 28,731 | 1,448 | 26,617–31,309 |

O ganho é quase linear até quatro threads e chega a 7,171 nos oito núcleos
físicos. De oito para 16 threads, o tempo cai apenas de 30,229 para 28,565 ms:
as threads adicionais usam SMT e compartilham unidades de execução, cache e
largura de banda. Por isso o speed-up estabiliza e a eficiência por thread
lógica cai para 47,4%.

Os valores pouco acima de 100% com duas e quatro threads não provam ganho
superlinear; podem decorrer de cache, variação de frequência, dispersão e melhor
aproveitamento agregado da hierarquia de memória.

Dados para o gráfico:

| Threads | Speed-up ideal | Speed-up medido | Eficiência |
|---:|---:|---:|---:|
| 1 | 1,000 | 1,033 | 103,3% |
| 2 | 2,000 | 2,020 | 101,0% |
| 4 | 4,000 | 4,041 | 101,0% |
| 8 | 8,000 | 7,171 | 89,6% |
| 16 | 16,000 | 7,589 | 47,4% |

## 6. Escalonadores e chunks

Medianas para o corpus forte; `S`, `D` e `G` significam `static`, `dynamic` e
`guided`.

| Threads | Esc. | Chunk | Tempo (ms) | Speed-up | Eficiência |
|---:|:---:|---:|---:|---:|---:|
| 1 | S | 1 | 209,847 | 1,033 | 103,3% |
| 1 | S | 4 | 217,736 | 0,996 | 99,6% |
| 1 | S | 16 | 218,076 | 0,994 | 99,4% |
| 1 | D | 1 | 216,431 | 1,002 | 100,2% |
| 1 | D | 4 | 216,295 | 1,002 | 100,2% |
| 1 | D | 16 | 217,480 | 0,997 | 99,7% |
| 1 | G | 1 | 218,849 | 0,991 | 99,1% |
| 1 | G | 4 | 218,147 | 0,994 | 99,4% |
| 1 | G | 16 | 215,988 | 1,004 | 100,4% |
| 2 | S | 1 | 107,295 | 2,020 | 101,0% |
| 2 | S | 4 | 115,610 | 1,875 | 93,8% |
| 2 | S | 16 | 126,924 | 1,708 | 85,4% |
| 2 | D | 1 | 103,723 | 2,090 | 104,5% |
| 2 | D | 4 | 105,773 | 2,049 | 102,5% |
| 2 | D | 16 | 136,212 | 1,591 | 79,6% |
| 2 | G | 1 | 134,002 | 1,618 | 80,9% |
| 2 | G | 4 | 103,936 | 2,086 | 104,3% |
| 2 | G | 16 | 107,388 | 2,019 | 100,9% |
| 4 | S | 1 | 53,642 | 4,041 | 101,0% |
| 4 | S | 4 | 53,894 | 4,022 | 100,6% |
| 4 | S | 16 | 50,616 | 4,283 | 107,1% |
| 4 | D | 1 | 49,908 | 4,344 | 108,6% |
| 4 | D | 4 | 49,997 | 4,336 | 108,4% |
| 4 | D | 16 | 50,677 | 4,278 | 106,9% |
| 4 | G | 1 | 49,778 | 4,355 | 108,9% |
| 4 | G | 4 | 49,993 | 4,336 | 108,4% |
| 4 | G | 16 | 50,864 | 4,262 | 106,5% |
| 8 | S | 1 | 30,229 | 7,171 | 89,6% |
| 8 | S | 4 | 29,941 | 7,240 | 90,5% |
| 8 | S | 16 | 29,509 | 7,346 | 91,8% |
| 8 | D | 1 | 28,459 | 7,617 | 95,2% |
| 8 | D | 4 | 28,968 | 7,483 | 93,5% |
| 8 | D | 16 | 29,744 | 7,288 | 91,1% |
| 8 | G | 1 | 28,818 | 7,522 | 94,0% |
| 8 | G | 4 | 28,361 | 7,644 | 95,5% |
| 8 | G | 16 | 29,738 | 7,290 | 91,1% |
| 16 | S | 1 | 28,565 | 7,589 | 47,4% |
| 16 | S | 4 | 27,859 | 7,781 | 48,6% |
| 16 | S | 16 | 27,915 | 7,766 | 48,5% |
| 16 | D | 1 | 26,545 | 8,167 | 51,0% |
| 16 | D | 4 | 26,881 | 8,064 | 50,4% |
| 16 | D | 16 | 27,251 | 7,955 | 49,7% |
| 16 | G | 1 | 26,653 | 8,133 | 50,8% |
| 16 | G | 4 | 27,097 | 8,000 | 50,0% |
| 16 | G | 16 | 28,531 | 7,598 | 47,5% |

O menor tempo foi 26,545 ms com 16 threads, `dynamic,1`. A diferença para
`guided,1` é apenas 0,108 ms, menor que a dispersão, logo não é possível afirmar
que um deles seja sempre superior. `Dynamic` e `guided` podem corrigir o
desbalanceamento de arquivos diferentes; `static` evita esse overhead e também
foi competitivo.

## 7. Balanceamento

Bytes aproximam o trabalho atribuído no escalonamento estático:

| Threads | Chunk | Menor carga | Maior carga | Maior desvio da média |
|---:|---:|---:|---:|---:|
| 2 | 1 | 51.642.368 | 54.132.736 | 2,4% |
| 2 | 4 | 47.448.064 | 58.327.040 | 10,3% |
| 2 | 16 | 52.887.552 | 52.887.552 | 0,0% |
| 4 | 1 | 24.117.248 | 30.015.488 | 13,5% |
| 4 | 4 | 23.724.032 | 29.163.520 | 10,3% |
| 4 | 16 | 26.443.776 | 26.443.776 | 0,0% |
| 8 | 1 | 8.650.752 | 15.728.640 | 34,6% |
| 8 | 4 | 11.862.016 | 14.581.760 | 10,3% |
| 8 | 16 | 13.221.888 | 13.221.888 | 0,0% |
| 16 | 1 | 4.325.376 | 7.864.320 | 34,6% |
| 16 | 4 | 5.931.008 | 7.290.880 | 10,3% |
| 16 | 16 | 6.610.944 | 6.610.944 | 0,0% |

O chunk 16 distribui ciclos completos dos oito arquivos-base e fica perfeitamente
balanceado em bytes, mas não é sempre o mais rápido. Conteúdo, cache, NUMA,
sistema de arquivos e overhead também influenciam. Os bons resultados de
`dynamic` e `guided` mostram que redistribuir trabalho pode compensar uma divisão
estática imperfeita.

## 8. Escalabilidade fraca

Configuração `static,1`, com 64 arquivos e 6.610.944 bytes por thread:

| Threads | Arquivos | Volume (bytes) | Mediana (ms) | Speed-up escalado | Eficiência |
|---:|---:|---:|---:|---:|---:|
| 1, sequencial | 64 | 6.610.944 | 13,700 | 1,000 | 100,0% |
| 1, OpenMP | 64 | 6.610.944 | 13,789 | 0,994 | 99,4% |
| 2, OpenMP | 128 | 13.221.888 | 13,132 | 2,087 | 104,3% |
| 4, OpenMP | 256 | 26.443.776 | 13,714 | 3,996 | 99,9% |
| 8, OpenMP | 512 | 52.887.552 | 15,641 | 7,007 | 87,6% |
| 16, OpenMP | 1.024 | 105.775.104 | 28,379 | 7,724 | 48,3% |

Idealmente, o tempo permaneceria constante. Isso ocorre aproximadamente até
quatro threads. Com oito, o tempo aumenta 14,2% e a eficiência cai para 87,6%.
Com 16, a carga por núcleo físico dobra por causa do SMT, o tempo chega a 28,379
ms e a eficiência cai para 48,3%. Os 104,3% com duas threads estão próximos do
ideal e refletem variação/cache, não escalabilidade acima do limite teórico.

| Threads | Eficiência ideal | Eficiência medida |
|---:|---:|---:|
| 1 | 100,0% | 99,4% |
| 2 | 100,0% | 104,3% |
| 4 | 100,0% | 99,9% |
| 8 | 100,0% | 87,6% |
| 16 | 100,0% | 48,3% |

## 9. Conclusão

A implementação paralela preservou o resultado e apresentou speed-up próximo
do ideal até quatro threads. Com oito núcleos físicos, atingiu speed-up 7,171.
O uso de 16 threads trouxe pouco ganho adicional porque duas threads de hardware
passaram a compartilhar cada núcleo, estabilizando o speed-up em torno de oito
e reduzindo a eficiência por thread lógica para aproximadamente 50%.

Não houve um escalonador vencedor absoluto. `Dynamic` e `guided` lidaram bem
com arquivos de tamanhos diferentes, enquanto `static` manteve baixo overhead.
Na melhor mediana, `dynamic,1` com 16 threads atingiu 26,545 ms e speed-up 8,167,
mas sua diferença para `guided,1` ficou dentro da variação experimental.
