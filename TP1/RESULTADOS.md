# TP1 — busca paralela de texto em arquivos

## Identificação

- Disciplina: Computação Paralela
- Trabalho: TP1 — OpenMP
- Aplicação: busca de uma palavra em múltiplos arquivos TXT
- Integrantes: preencher antes da entrega
- Data da coleta local: 14/09/2026

> **Importante:** estes são resultados preliminares obtidos no Codespace. O
> enunciado determina que as medições finais sejam realizadas no cluster
> Atlantica do LAD, com 8 cores e 16 threads. Portanto, as tabelas devem ser
> repetidas no Atlantica antes da entrega do PDF.

## 1. Descrição do problema

A aplicação procura uma palavra em todos os arquivos com extensão .txt da pasta
textos. Para cada arquivo, o programa informa a quantidade de ocorrências e, ao
final, apresenta a soma global e o tempo de execução.

A busca é literal, diferencia letras maiúsculas e minúsculas e não conta
ocorrências sobrepostas. A enumeração do diretório é feita antes da região
medida. O tempo apresentado inclui abertura, leitura, busca e fechamento dos
arquivos, mas não inclui a listagem do diretório nem a impressão dos resultados.

O problema possui potencial de paralelização porque cada arquivo pode ser
pesquisado independentemente. Na versão paralela, cada iteração do laço
corresponde a um arquivo e pode ser executada por uma thread diferente.

## 2. Implementações

Foram produzidas duas versões:

- buscador_sequencial.c: percorre os arquivos um por vez;
- buscador_paralelo.c: utiliza OpenMP para distribuir os arquivos.

A principal diretiva OpenMP utilizada foi:

    #pragma omp parallel for schedule(runtime) reduction(+:total)

O vetor de resultados é compartilhado, mas cada iteração escreve em uma posição
exclusiva. Por isso, não é necessário proteger essas escritas. A variável total
usa reduction para que cada thread acumule seu valor localmente e o OpenMP
realize a soma final sem condição de corrida. O índice do laço é privado por
definição no parallel for.

O schedule(runtime) permite testar os escalonadores static, dynamic e guided,
além de diferentes chunks, sem recompilar o código.

## 3. Ambiente local

| Item | Valor |
|---|---|
| Ambiente | GitHub Codespace virtualizado |
| Processador informado | AMD EPYC 9V74 80-Core Processor |
| Soquetes visíveis | 1 |
| Núcleos visíveis | 2 |
| Threads por núcleo | 2 |
| CPUs lógicas disponíveis | 4 |
| Cache L1 de dados | 64 KiB, 2 instâncias |
| Cache L2 | 2 MiB, 2 instâncias |
| Cache L3 | 32 MiB |
| Compilador | GCC 13.3.0 |
| Otimização | -O2 |
| API paralela | OpenMP, opção -fopenmp |

Como o Codespace fornece somente dois núcleos físicos, o ponto de 4 threads usa
SMT, isto é, duas threads de hardware por núcleo. Isso deve ser considerado ao
interpretar a eficiência.

## 4. Metodologia

Os oito textos pequenos incluídos no repositório totalizam 807 bytes. Esse
volume é suficiente para testar a correção, mas produz tempos de poucos
microssegundos. Para obter medições menos instáveis sem criar textos enormes,
foi montado um corpus temporário com cópias dos mesmos oito arquivos.

| Corpus | Arquivos pequenos | Volume total |
|---|---:|---:|
| Base fraca | 1.024 | 103.296 bytes |
| Intermediário fraco | 2.048 | 206.592 bytes |
| Forte/máximo fraco | 4.096 | 413.184 bytes |

Procedimento:

1. Compilação com GCC, -O2 e -fopenmp.
2. Validação de que as versões sequencial e paralela retornam o mesmo total.
3. Uma execução de aquecimento antes de cada configuração.
4. Quinze medições por configuração.
5. Uso da mediana como tempo principal, por ser menos sensível a interferências
   do ambiente virtualizado.
6. Escalabilidade forte com 4.096 arquivos em todas as execuções.
7. Escalabilidade fraca com 1.024 arquivos por thread.
8. Avaliação de static, dynamic e guided com chunks 1, 4 e 16.

No corpus forte, ambas as versões encontraram 3.072 ocorrências da palavra
OpenMP. Os resultados foram idênticos em todos os testes.

## 5. Fórmulas

Para escalabilidade forte:

    Speed-up(p) = T_sequencial / T_paralelo(p)
    Eficiência(p) = Speed-up(p) / p

Para escalabilidade fraca, com o problema crescendo proporcionalmente a p:

    Speed-up escalado(p) = p * T_sequencial(1 unidade) / T_paralelo(p unidades)
    Eficiência fraca(p) = Speed-up escalado(p) / p
                         = T_sequencial(1 unidade) / T_paralelo(p unidades)

T_sequencial foi medido na implementação sequencial, e não na versão OpenMP com
uma thread.

## 6. Escalabilidade forte

Para a tabela principal foi mantida a mesma configuração, static com chunk 1,
em todas as quantidades de threads.

| Versão | Threads | Tempo mediano (ms) | Speed-up | Eficiência |
|---|---:|---:|---:|---:|
| Sequencial | 1 | 37,801 | 1,000 | 100,0% |
| OpenMP static,1 | 1 | 36,878 | 1,025 | 102,5% |
| OpenMP static,1 | 2 | 20,394 | 1,854 | 92,7% |
| OpenMP static,1 | 4 | 13,471 | 2,806 | 70,2% |

Dados de dispersão das quinze medições:

| Versão | Threads | Média (ms) | Desvio-padrão (ms) | Amplitude (ms) |
|---|---:|---:|---:|---:|
| Sequencial | 1 | 37,829 | 1,227 | 4,255 |
| OpenMP static,1 | 1 | 36,886 | 0,322 | 1,155 |
| OpenMP static,1 | 2 | 20,496 | 1,028 | 3,642 |
| OpenMP static,1 | 4 | 15,166 | 2,808 | 9,177 |

O valor ligeiramente acima de 100% com uma thread não representa ganho
superlinear comprovado. A diferença é pequena e pode ser explicada por cache do
sistema de arquivos, ordem das execuções, variação da máquina virtual e ruído
de medição.

Com duas threads, o speed-up de 1,854 ficou próximo do ideal 2. Com quatro
threads, o speed-up chegou a 2,806, mas a eficiência caiu para 70,2%. A partir
da terceira thread passam a ser compartilhados os dois núcleos físicos, além de
existirem custos de criação das threads, escalonamento e acesso concorrente ao
sistema de arquivos.

Gráfico do speed-up forte (primeira linha: ideal; segunda linha: medido):

~~~mermaid
xychart-beta
    title "Speed-up forte — static, chunk 1"
    x-axis "Threads" [1, 2, 4]
    y-axis "Speed-up" 0 --> 4
    line [1, 2, 4]
    line [1.025, 1.854, 2.806]
~~~

Gráfico da eficiência forte (primeira linha: ideal; segunda linha: medida):

~~~mermaid
xychart-beta
    title "Eficiência forte — static, chunk 1"
    x-axis "Threads" [1, 2, 4]
    y-axis "Eficiência (%)" 0 --> 110
    line [100, 100, 100]
    line [102.5, 92.7, 70.2]
~~~

## 7. Escalonadores e chunks

A tabela mostra as medianas da escalabilidade forte. Todos os casos usam os
mesmos 4.096 arquivos e produziram as mesmas 3.072 ocorrências.

| Threads | Schedule | Chunk | Tempo (ms) | Speed-up | Eficiência |
|---:|---|---:|---:|---:|---:|
| 1 | static | 1 | 36,878 | 1,025 | 102,5% |
| 1 | static | 4 | 36,151 | 1,046 | 104,6% |
| 1 | static | 16 | 36,009 | 1,050 | 105,0% |
| 1 | dynamic | 1 | 35,947 | 1,052 | 105,2% |
| 1 | dynamic | 4 | 35,710 | 1,059 | 105,9% |
| 1 | dynamic | 16 | 36,029 | 1,049 | 104,9% |
| 1 | guided | 1 | 35,804 | 1,056 | 105,6% |
| 1 | guided | 4 | 35,914 | 1,053 | 105,3% |
| 1 | guided | 16 | 36,860 | 1,026 | 102,6% |
| 2 | static | 1 | 20,394 | 1,854 | 92,7% |
| 2 | static | 4 | 19,766 | 1,912 | 95,6% |
| 2 | static | 16 | 20,139 | 1,877 | 93,9% |
| 2 | dynamic | 1 | 19,659 | 1,923 | 96,1% |
| 2 | dynamic | 4 | 19,398 | 1,949 | 97,4% |
| 2 | dynamic | 16 | 19,450 | 1,943 | 97,2% |
| 2 | guided | 1 | 19,494 | 1,939 | 97,0% |
| 2 | guided | 4 | 21,018 | 1,799 | 89,9% |
| 2 | guided | 16 | 18,826 | 2,008 | 100,4% |
| 4 | static | 1 | 13,471 | 2,806 | 70,2% |
| 4 | static | 4 | 13,373 | 2,827 | 70,7% |
| 4 | static | 16 | 13,460 | 2,808 | 70,2% |
| 4 | dynamic | 1 | 13,402 | 2,821 | 70,5% |
| 4 | dynamic | 4 | 13,379 | 2,825 | 70,6% |
| 4 | dynamic | 16 | 13,474 | 2,805 | 70,1% |
| 4 | guided | 1 | 12,724 | 2,971 | 74,3% |
| 4 | guided | 4 | 14,164 | 2,669 | 66,7% |
| 4 | guided | 16 | 13,872 | 2,725 | 68,1% |

O menor tempo mediano com quatro threads foi 12,724 ms, obtido por guided com
chunk 1. Entretanto, a diferença entre vários resultados é menor que a
amplitude observada nas repetições. Portanto, não é possível afirmar com
segurança que guided é sempre superior nesse corpus.

Os arquivos possuem tamanhos próximos e o trabalho de cada iteração é simples.
Por isso, static já apresenta bom desempenho. Dynamic e guided podem compensar
arquivos de tamanhos diferentes, mas adicionam overhead de distribuição durante
a execução.

## 8. Balanceamento de carga

O balanceamento foi estimado pelo número total de bytes atribuídos a cada
thread no escalonamento static. Bytes são uma aproximação do trabalho, pois o
custo da busca também depende do conteúdo.

| Threads | Chunk | Bytes por thread | Maior desvio acima da média |
|---:|---:|---|---:|
| 1 | 1 | 413.184 | 0,0% |
| 2 | 1 | 201.728; 211.456 | 2,4% |
| 4 | 1 | 106.496; 94.208; 95.232; 117.248 | 13,5% |
| 4 | 4 | 113.920; 92.672; 113.920; 92.672 | 10,3% |
| 4 | 16 | 103.296; 103.296; 103.296; 103.296 | 0,0% |

O chunk 16 oferece distribuição perfeita em bytes neste corpus porque cada
bloco contém ciclos completos dos oito arquivos-base. Mesmo assim, seu tempo
ficou próximo dos demais, mostrando que balanceamento em bytes não é o único
fator: interferência do sistema, abertura de arquivos, cache e SMT também
afetam a execução.

## 9. Escalabilidade fraca

Foi mantida a carga de 1.024 arquivos, ou 103.296 bytes, por thread. A
configuração paralela foi static com chunk 1.

| Threads | Arquivos | Volume (bytes) | Ocorrências | Tempo mediano (ms) | Speed-up escalado | Eficiência fraca |
|---:|---:|---:|---:|---:|---:|---:|
| 1, sequencial | 1.024 | 103.296 | 768 | 9,600 | 1,000 | 100,0% |
| 1, OpenMP | 1.024 | 103.296 | 768 | 9,258 | 1,037 | 103,7% |
| 2, OpenMP | 2.048 | 206.592 | 1.536 | 10,559 | 1,818 | 90,9% |
| 4, OpenMP | 4.096 | 413.184 | 3.072 | 14,268 | 2,691 | 67,3% |

Na escalabilidade fraca ideal, o tempo permaneceria constante e a eficiência
seria 100%. Com duas threads, o tempo aumentou de 9,600 para 10,559 ms e a
eficiência ficou em 90,9%. Com quatro threads, o tempo chegou a 14,268 ms e a
eficiência caiu para 67,3%.

A queda ocorre porque o aumento do número de threads não elimina os custos
fixos e cria concorrência pelos recursos compartilhados. Além disso, quatro
threads lógicas estão executando em apenas dois núcleos físicos no Codespace.

Gráfico da eficiência fraca (primeira linha: ideal; segunda linha: medida):

~~~mermaid
xychart-beta
    title "Eficiência da escalabilidade fraca"
    x-axis "Threads" [1, 2, 4]
    y-axis "Eficiência (%)" 0 --> 110
    line [100, 100, 100]
    line [103.7, 90.9, 67.3]
~~~

## 10. Conclusão

A paralelização está correta, pois as versões sequencial e OpenMP produziram os
mesmos resultados. Na escalabilidade forte, duas threads quase reduziram o
tempo pela metade. Quatro threads melhoraram o desempenho, mas não atingiram
speed-up 4 devido a overhead, compartilhamento dos núcleos físicos,
balanceamento e concorrência no acesso aos arquivos.

Os escalonadores produziram tempos semelhantes porque os arquivos são pequenos
e de tamanhos próximos. Guided com chunk 1 obteve o menor tempo local com quatro
threads, mas a dispersão impede concluir que essa diferença seja permanente.
Static é uma escolha adequada para o caso simples e possui menor complexidade de
escalonamento.

Na escalabilidade fraca, a eficiência diminuiu conforme o conjunto e a
quantidade de threads cresceram. O resultado mostra que manter o mesmo número de
arquivos por thread não garante tempo constante quando as threads disputam
núcleos, cache, memória e sistema de arquivos.

## 11. Comandos para repetir no Atlantica

Compilação e teste:

    cd TP1
    make clean
    make
    make test

Execução sequencial:

    ./buscador_sequencial OpenMP

Execuções paralelas:

    OMP_NUM_THREADS=1 OMP_SCHEDULE=static,1 ./buscador OpenMP
    OMP_NUM_THREADS=2 OMP_SCHEDULE=static,1 ./buscador OpenMP
    OMP_NUM_THREADS=4 OMP_SCHEDULE=static,1 ./buscador OpenMP
    OMP_NUM_THREADS=8 OMP_SCHEDULE=static,1 ./buscador OpenMP
    OMP_NUM_THREADS=16 OMP_SCHEDULE=static,1 ./buscador OpenMP

Para comparar escalonadores, substituir static,1 por dynamic,1, guided,1 e
pelas demais combinações de chunk desejadas. Cada configuração deve ser
executada várias vezes, usando o mesmo corpus na escalabilidade forte. Para a
fraca, usar uma quantidade de arquivos proporcional às threads.

## 12. Uso de inteligência artificial

Uma ferramenta de IA foi utilizada para auxiliar na leitura do enunciado, na
estruturação das versões sequencial e OpenMP, na criação dos testes, na
organização da metodologia experimental, nos cálculos de speed-up e eficiência
e na redação inicial desta análise. Os resultados foram obtidos executando os
programas no ambiente descrito e comparando as saídas das duas versões. O grupo
deve revisar o texto, compreender o código e ser capaz de explicar as decisões
na apresentação.
