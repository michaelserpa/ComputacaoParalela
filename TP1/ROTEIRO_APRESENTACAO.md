# Roteiro de apresentação — TP1 OpenMP — Grupo 11

Tempo total: aproximadamente 5 minutos. Use três slides.

## Antes de apresentar: o que realmente foi feito

Você não precisa dizer que “rodou muitos comandos Bash”. Bash foi apenas uma
forma de repetir automaticamente o mesmo experimento. A metodologia é:

1. O programa sequencial e o paralelo foram compilados com `gcc -O2 -fopenmp`.
2. Um nodo do LAD com 8 núcleos físicos e 16 threads lógicas foi reservado.
3. O próprio código mediu a região de busca com `omp_get_wtime()`.
4. A versão sequencial forneceu o tempo de referência.
5. A versão paralela foi executada com 1, 2, 4, 8 e 16 threads.
6. Cada configuração foi medida 15 vezes; usamos a mediana.
7. Na escala forte, o mesmo conjunto de arquivos foi usado sempre.
8. Na escala fraca, a quantidade de arquivos cresceu junto com as threads.
9. `OMP_SCHEDULE` selecionou `static`, `dynamic` ou `guided` e o chunk.

Se fosse feito manualmente, seria exatamente a mesma execução repetida 15
vezes, anotando o campo `Tempo` impresso pelo programa. A automação não altera o
algoritmo nem fabrica os resultados; apenas evita erros de digitação.

## Slide 1 — Problema e solução (cerca de 1 minuto)

### Coloque no slide

- Busca de uma palavra em vários arquivos TXT.
- Cada arquivo pode ser processado independentemente.
- `parallel for`, `schedule(runtime)` e `reduction(+:total)`.
- LAD: 8 núcleos físicos e 16 threads lógicas.

### Fala sugerida

“Nosso trabalho é um buscador que conta ocorrências de uma palavra em vários
arquivos de texto. Esse problema é paralelizável porque a busca em um arquivo
não depende dos outros. Na versão sequencial, percorremos um arquivo de cada
vez. Na paralela, usamos `parallel for` para distribuir os arquivos entre as
threads. Usamos `reduction` para somar o total sem condição de corrida e
`schedule(runtime)` para testar diferentes escalonadores sem recompilar. Os
testes foram feitos em um nodo do Atlantica com oito núcleos físicos e 16
threads lógicas.”

## Slide 2 — Escalabilidade forte (cerca de 1 minuto e 40 segundos)

Use `grafico_speedup_forte.png`.

### Coloque no slide

- Entrada constante: 1.024 arquivos, 105,8 MB.
- Tempo sequencial: 216,781 ms.
- Speed-up: 2,020; 4,041; 7,171; 7,589.
- Eficiência em 8 threads: 89,6%.

### Fala sugerida

“Na escalabilidade forte, mantivemos exatamente a mesma entrada e aumentamos o
número de threads. O tempo sequencial de referência foi 216,781 milissegundos.
Com duas threads, o speed-up foi 2,020; com quatro, 4,041; e com oito, 7,171.
Isso mostra ganho quase linear até os oito núcleos físicos, com eficiência de
89,6% em oito threads. Com 16 threads, o speed-up aumentou pouco, para 7,589, e
a eficiência caiu para 47,4%. Isso acontece porque a máquina só tem oito
núcleos físicos. As threads adicionais usam SMT e compartilham recursos do
mesmo núcleo. Os valores ligeiramente acima do ideal em duas e quatro threads
são pequenos e podem ser explicados por cache e variação experimental.”

Não diga que 16 threads “pioraram” o programa: houve uma pequena redução do
tempo, mas o ganho adicional foi pequeno e a eficiência caiu.

## Slide 3 — Escalabilidade fraca e conclusão (cerca de 1 minuto e 40 segundos)

Use `grafico_eficiencia_fraca.png`. Se houver espaço, coloque uma miniatura de
`grafico_escalonadores.png`.

### Coloque no slide

- Carga por thread: 64 arquivos, 6,61 MB.
- Eficiência: 99,4%, 104,3%, 99,9%, 87,6% e 48,3%.
- Melhor mediana: `dynamic,1`, 16 threads, 26,545 ms.
- Resultado validado: 786.432 ocorrências nas duas versões.

### Fala sugerida

“Na escalabilidade fraca, aumentamos a entrada proporcionalmente: cada thread
recebeu 64 arquivos, ou 6,61 megabytes. O ideal é o tempo permanecer constante,
o que equivale a eficiência de 100%. Ficamos praticamente no ideal até quatro
threads. Com oito, a eficiência foi 87,6%; com 16, caiu para 48,3% novamente por
causa do SMT e do compartilhamento de recursos.

Também testamos `static`, `dynamic` e `guided` com chunks 1, 4 e 16. O menor
tempo mediano foi 26,545 milissegundos com `dynamic,1` e 16 threads, mas a
diferença para `guided,1` foi muito pequena. Portanto, não afirmamos que existe
um vencedor absoluto. Finalmente, validamos a correção: as duas versões
encontraram exatamente 786.432 ocorrências. A conclusão é que a paralelização
funciona muito bem até os oito núcleos físicos e que 16 threads trazem pouco
benefício adicional.”

## Explicações que você precisa dominar

### O que é escalabilidade forte?

O tamanho da entrada não muda. A pergunta é: “quanto mais rápido resolvo o
mesmo problema quando adiciono processadores?”.

`speed-up = tempo sequencial / tempo paralelo`

`eficiência = speed-up / número de threads`

### O que é escalabilidade fraca?

A carga por thread é mantida constante. Ao dobrar as threads, também dobramos a
entrada. O ideal é o tempo total permanecer constante e a eficiência ficar em
100%.

### Por que usar a mediana de 15 execuções?

O tempo varia por cache, sistema operacional e sistema de arquivos. A mediana
representa melhor uma execução típica e é menos afetada por um valor isolado.

### Como o programa mede o tempo?

Ele chama `omp_get_wtime()` antes e depois da região que abre, lê e pesquisa os
arquivos. A enumeração inicial do diretório e a impressão final ficam fora da
região medida, igualmente nas duas versões.

### Por que `reduction`?

Várias threads precisam atualizar o total. `reduction(+:total)` cria um total
privado para cada thread e soma tudo ao final, evitando condição de corrida e o
custo de uma região crítica a cada arquivo.

### Por que `schedule(runtime)`?

Permite escolher o escalonador pela variável `OMP_SCHEDULE`. Assim, o mesmo
executável testa `static`, `dynamic` e `guided` com chunks diferentes.

### O que significam os escalonadores?

- `static`: divide as iterações antecipadamente; tem pouco overhead.
- `dynamic`: entrega novos blocos quando uma thread termina; ajuda no
  desbalanceamento, mas custa mais.
- `guided`: começa com blocos maiores e diminui o tamanho ao longo da execução.
- `chunk`: número de iterações, neste caso arquivos, entregues por bloco.

### Por que os arquivos foram aumentados?

Os oito textos originais terminam em microssegundos e geram medições instáveis.
O conteúdo foi repetido para aumentar o trabalho de busca sem mudar o algoritmo.
Antes da coleta, foi confirmado que as duas versões continuavam produzindo o
mesmo total.

## Perguntas prováveis do professor

**Onde está o paralelismo?**  
No laço que percorre a lista de arquivos, marcado com `#pragma omp parallel for`.

**Existe condição de corrida?**  
O total seria uma condição de corrida sem `reduction`. O vetor é seguro porque
cada iteração escreve em um índice diferente.

**Por que não houve speed-up 16?**  
Porque existem oito núcleos físicos. As 16 threads são lógicas e compartilham
recursos via SMT. Além disso, abertura de arquivos e memória não escalam
indefinidamente.

**Por que algumas eficiências passam um pouco de 100%?**  
Por efeitos de cache, frequência e ruído de medição. Não tratamos isso como
ganho superlinear comprovado.

**Qual escalonador escolheriam?**  
`Dynamic,1` teve a melhor mediana com 16 threads, mas a diferença para
`guided,1` ficou dentro da variação. `Static` continua sendo uma opção simples
e competitiva quando os arquivos têm trabalho parecido.

**Como garantiram a correção?**  
Executamos as duas versões sobre a mesma entrada e ambas retornaram 786.432
ocorrências.

## Frase final

“O ponto principal é que o paralelismo acompanha bem os oito núcleos físicos;
depois disso, o SMT não duplica a capacidade da máquina e o ganho estabiliza.”
