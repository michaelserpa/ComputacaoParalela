#!/usr/bin/env python3
"""Gera o relatório simples do TP1 a partir das medições realizadas no LAD."""

import csv
import statistics
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, "/tmp/tp1_pdf_deps")
from fpdf import FPDF


BASE = Path(__file__).resolve().parent
CSV = BASE / "resultados_lad.csv"
SAIDA = BASE / "Relatorio_TP1_Grupo11.pdf"
FONTES = Path("/usr/share/fonts/truetype/dejavu")


def carregar_resultados():
    grupos = defaultdict(list)
    with CSV.open(newline="", encoding="utf-8") as arquivo:
        for linha in csv.DictReader(arquivo):
            chave = (
                linha["escala"], linha["versao"], int(linha["threads"]),
                linha["schedule"], int(linha["chunk"]),
                int(linha["arquivos"]), int(linha["bytes"]),
            )
            grupos[chave].append(float(linha["tempo_s"]))
    return grupos


class Relatorio(FPDF):
    def footer(self):
        self.set_y(-7)
        self.set_font("DejaVu", "", 7)
        self.set_text_color(90)
        self.cell(0, 4, f"Grupo 11 — TP1 OpenMP   |   Página {self.page_no()}", align="C")


pdf = Relatorio(format="A4", unit="mm")
pdf.set_margins(10, 8, 10)
pdf.set_auto_page_break(True, 10)
pdf.add_font("DejaVu", "", str(FONTES / "DejaVuSans.ttf"))
pdf.add_font("DejaVu", "B", str(FONTES / "DejaVuSans-Bold.ttf"))
pdf.add_font("Mono", "", str(FONTES / "DejaVuSansMono.ttf"))


def titulo_pagina(titulo, subtitulo=None):
    pdf.set_text_color(0)
    pdf.set_font("DejaVu", "B", 13)
    pdf.cell(0, 6, titulo, align="C", new_x="LMARGIN", new_y="NEXT")
    if subtitulo:
        pdf.set_font("DejaVu", "", 8)
        pdf.cell(0, 4, subtitulo, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)


def secao_coluna(x, y, largura, titulo, paragrafos):
    pdf.set_xy(x, y)
    pdf.set_font("DejaVu", "B", 10)
    pdf.multi_cell(largura, 4.4, titulo)
    y = pdf.get_y() + 0.5
    for texto in paragrafos:
        pdf.set_xy(x, y)
        pdf.set_font("DejaVu", "", 10)
        pdf.multi_cell(largura, 4.6, texto, align="J")
        y = pdf.get_y() + 1.1
    return y


def tabela(x, y, larguras, cabecalho, linhas, altura=5.2, fonte=8):
    pdf.set_xy(x, y)
    pdf.set_draw_color(70)
    pdf.set_font("DejaVu", "B", fonte)
    pdf.set_fill_color(225, 232, 240)
    for largura, texto in zip(larguras, cabecalho):
        pdf.cell(largura, altura, str(texto), border=1, align="C", fill=True)
    pdf.ln(altura)
    pdf.set_x(x)
    pdf.set_font("DejaVu", "", fonte)
    for linha in linhas:
        for largura, texto in zip(larguras, linha):
            pdf.cell(largura, altura, str(texto), border=1, align="C")
        pdf.ln(altura)
        pdf.set_x(x)
    return pdf.get_y()


def grafico(x, y, largura, altura, titulo, xs, series, ymax):
    margem_x, margem_y = 10, 8
    gx, gy = x + margem_x, y + 5
    gw, gh = largura - margem_x - 3, altura - margem_y - 8
    pdf.set_font("DejaVu", "B", 7.5)
    pdf.set_xy(x, y)
    pdf.cell(largura, 4, titulo, align="C")
    pdf.set_draw_color(70)
    pdf.line(gx, gy, gx, gy + gh)
    pdf.line(gx, gy + gh, gx + gw, gy + gh)
    pdf.set_font("DejaVu", "", 6)
    for i in range(5):
        valor = ymax * i / 4
        py = gy + gh - gh * i / 4
        pdf.set_draw_color(220)
        pdf.line(gx, py, gx + gw, py)
        pdf.set_xy(x, py - 2)
        pdf.cell(margem_x - 1, 4, f"{valor:.0f}", align="R")
    cores = [(35, 100, 180), (210, 70, 55)]
    for indice, (nome, valores) in enumerate(series):
        pontos = []
        for i, valor in enumerate(valores):
            px = gx + gw * i / (len(xs) - 1)
            py = gy + gh - gh * valor / ymax
            pontos.append((px, py))
        pdf.set_draw_color(*cores[indice])
        pdf.set_fill_color(*cores[indice])
        for a, b in zip(pontos, pontos[1:]):
            pdf.line(a[0], a[1], b[0], b[1])
        for px, py in pontos:
            pdf.ellipse(px - 0.8, py - 0.8, 1.6, 1.6, style="F")
    pdf.set_text_color(0)
    for i, valor in enumerate(xs):
        px = gx + gw * i / (len(xs) - 1)
        pdf.set_xy(px - 4, gy + gh + 1)
        pdf.cell(8, 3, str(valor), align="C")
    lx = x + largura - 33
    for i, (nome, _) in enumerate(series):
        pdf.set_fill_color(*cores[i])
        pdf.rect(lx, y + 1 + i * 3.5, 2.5, 2.5, style="F")
        pdf.set_xy(lx + 3.5, y + i * 3.5)
        pdf.cell(28, 4, nome)


grupos = carregar_resultados()
forte_seq = statistics.median(
    grupos[("forte", "sequencial", 1, "none", 0, 1024, 105775104)]
)
fraca_seq = statistics.median(
    grupos[("fraca", "sequencial", 1, "none", 0, 64, 6610944)]
)
threads = [1, 2, 4, 8, 16]
bytes_fracos = {1: 6610944, 2: 13221888, 4: 26443776,
                8: 52887552, 16: 105775104}

forte = []
for p in threads:
    tempos = grupos[("forte", "openmp", p, "static", 1, 1024, 105775104)]
    mediana = statistics.median(tempos)
    speedup = forte_seq / mediana
    forte.append((p, mediana, speedup, speedup / p))

fraca = []
for p in threads:
    tempos = grupos[("fraca", "openmp", p, "static", 1,
                     64 * p, bytes_fracos[p])]
    mediana = statistics.median(tempos)
    speedup = p * fraca_seq / mediana
    fraca.append((p, mediana, speedup, speedup / p))

# Página 1: texto em duas colunas.
pdf.add_page()
titulo_pagina(
    "Busca paralela de texto com OpenMP",
    "Computação Paralela — TP1 — Grupo 11 — Integrantes: ______________________________",
)
inicio_y = pdf.get_y()
coluna = 92
espaco = 6

y = secao_coluna(10, inicio_y, coluna, "1. Problema", [
    "A aplicação busca uma palavra em vários arquivos TXT e informa as ocorrências por arquivo e o total. A busca é literal, diferencia maiúsculas de minúsculas e não conta ocorrências sobrepostas. O tempo inclui abertura, leitura, busca e fechamento dos arquivos.",
    "Há potencial de paralelização porque cada arquivo pode ser pesquisado independentemente. Os limites principais são o acesso ao sistema de arquivos e o desbalanceamento causado por arquivos de tamanhos diferentes.",
])
y = secao_coluna(10, y, coluna, "2. Implementação OpenMP", [
    "A versão sequencial percorre os arquivos em ordem. A versão paralela aplica parallel for com schedule(runtime) e reduction(+:total). A redução evita condição de corrida, enquanto schedule(runtime) permite comparar static, dynamic e guided sem recompilar.",
    "Cada iteração escreve em uma posição exclusiva do vetor de resultados. Portanto, somente o total precisa da redução e não é necessária uma região crítica.",
])
secao_coluna(10, y, coluna, "3. Metodologia", [
    "As medições foram feitas no nodo atlantica07 do LAD: dois Xeon E5520, oito núcleos físicos e 16 threads lógicas. O código foi compilado com GCC 9.4.0, -O2 e -fopenmp. Foram usados OMP_PROC_BIND=spread e OMP_PLACES=cores.",
    "Cada configuração teve um aquecimento e 15 execuções; a mediana foi usada por ser menos sensível a variações. Na escala forte foram mantidos 1.024 arquivos e 105,8 MB. Na fraca foram mantidos 64 arquivos e 6,61 MB por thread.",
])

x2 = 10 + coluna + espaco
y = secao_coluna(x2, inicio_y, coluna, "4. Resultados", [
    "As versões sequencial e paralela encontraram 786.432 ocorrências, confirmando a correção. Na escala forte, o speed-up foi 2,020 com duas threads, 4,041 com quatro, 7,171 com oito e 7,589 com 16.",
    "O ganho foi quase linear até quatro threads e permaneceu alto nos oito núcleos físicos. De oito para 16 threads houve pouca melhora, pois as threads adicionais usam SMT e compartilham as unidades de execução, cache e largura de banda. Assim, a eficiência caiu de 89,6% para 47,4%.",
])
y = secao_coluna(x2, y, coluna, "5. Escalonamento e balanceamento", [
    "Foram avaliados static, dynamic e guided com chunks 1, 4 e 16. A menor mediana foi 26,545 ms com dynamic,1 e 16 threads, mas guided,1 obteve 26,653 ms. A diferença é menor que a dispersão e não permite declarar um vencedor permanente.",
    "O chunk 16 teve distribuição perfeita em bytes; mesmo assim, nem sempre foi o mais rápido. Conteúdo, cache, NUMA e overhead também influenciam. Dynamic e guided podem compensar diferenças entre os arquivos, enquanto static possui menor custo de distribuição.",
])
secao_coluna(x2, y, coluna, "6. Conclusão", [
    "A paralelização preservou o resultado e explorou bem os oito núcleos físicos. A escala fraca ficou próxima do ideal até quatro threads e atingiu 87,6% de eficiência com oito. O principal limite surgiu com 16 threads, quando o SMT não duplicou os recursos físicos. Valores pouco acima de 100% foram tratados como efeitos de cache e variação experimental.",
    "Ferramenta de IA foi usada para apoiar a organização dos testes, os cálculos estatísticos e a redação. O grupo revisou o código, as fórmulas e a interpretação dos resultados.",
])

# Página 2: tabelas e gráficos em coluna única.
pdf.add_page()
titulo_pagina("Resultados medidos no LAD", "Medianas de 15 execuções")
pdf.set_font("DejaVu", "B", 9)
pdf.cell(0, 5, "Escalabilidade forte — corpus fixo de 1.024 arquivos (static, chunk 1)", new_x="LMARGIN", new_y="NEXT")
linhas_forte = [["Seq.", "1", "216,781", "1,000", "100,0%"]]
for p, tempo, speedup, eficiencia in forte:
    linhas_forte.append(["OpenMP", str(p), f"{tempo*1000:.3f}".replace(".", ","),
                         f"{speedup:.3f}".replace(".", ","),
                         f"{eficiencia*100:.1f}%".replace(".", ",")])
y = tabela(10, pdf.get_y(), [31, 25, 42, 42, 50],
           ["Versão", "Threads", "Tempo (ms)", "Speed-up", "Eficiência"], linhas_forte)

pdf.set_y(y + 3)
pdf.set_font("DejaVu", "B", 9)
pdf.cell(0, 5, "Escalabilidade fraca — 64 arquivos e 6,61 MB por thread (static, chunk 1)", new_x="LMARGIN", new_y="NEXT")
linhas_fraca = [["Seq.", "1", "64", "13,700", "1,000", "100,0%"]]
for p, tempo, speedup, eficiencia in fraca:
    linhas_fraca.append(["OpenMP", str(p), str(64*p),
                         f"{tempo*1000:.3f}".replace(".", ","),
                         f"{speedup:.3f}".replace(".", ","),
                         f"{eficiencia*100:.1f}%".replace(".", ",")])
y = tabela(10, pdf.get_y(), [27, 20, 27, 36, 40, 40],
           ["Versão", "Threads", "Arquivos", "Tempo (ms)", "Speed-up", "Eficiência"], linhas_fraca)

grafico(10, y + 5, 91, 61, "Speed-up forte",
        threads, [("Ideal", threads), ("Medido", [r[2] for r in forte])], 16)
grafico(108, y + 5, 91, 61, "Eficiência fraca (%)",
        threads, [("Ideal", [100]*5), ("Medida", [r[3]*100 for r in fraca])], 110)

pdf.set_y(y + 68)
pdf.set_font("DejaVu", "B", 9)
pdf.cell(0, 5, "Melhor escalonamento observado por quantidade de threads", new_x="LMARGIN", new_y="NEXT")
melhores = []
for p in threads:
    candidatos = []
    for sched in ("static", "dynamic", "guided"):
        for chunk in (1, 4, 16):
            med = statistics.median(
                grupos[("forte", "openmp", p, sched, chunk, 1024, 105775104)]
            )
            candidatos.append((med, sched, chunk))
    med, sched, chunk = min(candidatos)
    sp = forte_seq / med
    melhores.append([str(p), f"{sched},{chunk}",
                     f"{med*1000:.3f}".replace(".", ","),
                     f"{sp:.3f}".replace(".", ","),
                     f"{sp/p*100:.1f}%".replace(".", ",")])
tabela(10, pdf.get_y(), [30, 45, 40, 38, 37],
       ["Threads", "Configuração", "Tempo (ms)", "Speed-up", "Eficiência"], melhores)

# Código-fonte em páginas adicionais, coluna única.
for nome, titulo in (
    ("buscador_sequencial.c", "Código-fonte — versão sequencial"),
    ("buscador_paralelo.c", "Código-fonte — versão paralela OpenMP"),
):
    pdf.add_page()
    titulo_pagina(titulo, nome)
    pdf.set_font("Mono", "", 6.7)
    with (BASE / nome).open(encoding="utf-8") as fonte:
        for numero, linha in enumerate(fonte, 1):
            texto = f"{numero:3d}  {linha.rstrip()}"
            pdf.multi_cell(0, 3.1, texto, new_x="LMARGIN", new_y="NEXT")

pdf.output(SAIDA)
print(SAIDA)
