#!/usr/bin/env python3
"""Gera gráficos PNG dos resultados finais medidos no LAD."""

import sys
from pathlib import Path

sys.path.insert(0, "/tmp/tp1_pdf_deps")
from PIL import Image, ImageDraw, ImageFont


BASE = Path(__file__).resolve().parent
LARGURA, ALTURA = 1600, 900
FUNDO = "#FFFFFF"
TEXTO = "#172033"
GRADE = "#DCE2EA"
AZUL = "#2869B1"
LARANJA = "#E4553D"
VERDE = "#26966F"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def fonte(tamanho, negrito=False):
    return ImageFont.truetype(FONT_BOLD if negrito else FONT, tamanho)


def texto_central(draw, xy, texto, fnt, cor=TEXTO):
    caixa = draw.textbbox((0, 0), texto, font=fnt)
    draw.text((xy[0] - (caixa[2] - caixa[0]) / 2, xy[1]), texto, font=fnt, fill=cor)


def linha_tracejada(draw, pontos, cor, largura=5, traco=14, espaco=10):
    for (x1, y1), (x2, y2) in zip(pontos, pontos[1:]):
        dx, dy = x2 - x1, y2 - y1
        distancia = (dx * dx + dy * dy) ** 0.5
        pos = 0
        while pos < distancia:
            fim = min(pos + traco, distancia)
            a = (x1 + dx * pos / distancia, y1 + dy * pos / distancia)
            b = (x1 + dx * fim / distancia, y1 + dy * fim / distancia)
            draw.line([a, b], fill=cor, width=largura)
            pos += traco + espaco


def grafico_linhas(arquivo, titulo, subtitulo, xs, series, ymax, yticks,
                   eixo_y, formato_valor):
    img = Image.new("RGB", (LARGURA, ALTURA), FUNDO)
    d = ImageDraw.Draw(img)
    texto_central(d, (LARGURA / 2, 38), titulo, fonte(48, True))
    texto_central(d, (LARGURA / 2, 102), subtitulo, fonte(24), "#526078")

    esquerda, direita, topo, fundo = 155, 1510, 185, 760
    d.line((esquerda, topo, esquerda, fundo), fill=TEXTO, width=3)
    d.line((esquerda, fundo, direita, fundo), fill=TEXTO, width=3)

    for valor in yticks:
        y = fundo - (fundo - topo) * valor / ymax
        d.line((esquerda, y, direita, y), fill=GRADE, width=2)
        rotulo = formato_valor(valor)
        caixa = d.textbbox((0, 0), rotulo, font=fonte(22))
        d.text((esquerda - 18 - (caixa[2] - caixa[0]), y - 13), rotulo,
               font=fonte(22), fill=TEXTO)

    pos_x = []
    for i, valor in enumerate(xs):
        x = esquerda + (direita - esquerda) * i / (len(xs) - 1)
        pos_x.append(x)
        texto_central(d, (x, fundo + 18), str(valor), fonte(23))

    cores = [AZUL, LARANJA, VERDE]
    for indice, (nome, valores, tracejado) in enumerate(series):
        pontos = [(pos_x[i], fundo - (fundo - topo) * v / ymax)
                  for i, v in enumerate(valores)]
        if tracejado:
            linha_tracejada(d, pontos, cores[indice])
        else:
            d.line(pontos, fill=cores[indice], width=7, joint="curve")
        for (x, y), valor in zip(pontos, valores):
            d.ellipse((x - 9, y - 9, x + 9, y + 9), fill=cores[indice], outline=FUNDO, width=3)
            if nome != "Ideal":
                texto_central(d, (x, y - 42), formato_valor(valor), fonte(22, True), cores[indice])

    legenda_x = esquerda + 40
    for indice, (nome, _, tracejado) in enumerate(series):
        y = 145
        x = legenda_x + indice * 245
        if tracejado:
            linha_tracejada(d, [(x, y), (x + 55, y)], cores[indice], 5)
        else:
            d.line((x, y, x + 55, y), fill=cores[indice], width=7)
        d.text((x + 68, y - 16), nome, font=fonte(23), fill=TEXTO)

    texto_central(d, ((esquerda + direita) / 2, 815), "Número de threads", fonte(25, True))
    img.save(BASE / arquivo, quality=95)


def grafico_escalonadores():
    dados = {
        "static": [28.565, 27.859, 27.915],
        "dynamic": [26.545, 26.881, 27.251],
        "guided": [26.653, 27.097, 28.531],
    }
    chunks = [1, 4, 16]
    img = Image.new("RGB", (LARGURA, ALTURA), FUNDO)
    d = ImageDraw.Draw(img)
    texto_central(d, (LARGURA / 2, 38), "Escalonadores com 16 threads", fonte(48, True))
    texto_central(d, (LARGURA / 2, 102), "Mediana de 15 execuções — menor tempo é melhor", fonte(24), "#526078")

    esquerda, direita, topo, fundo = 150, 1510, 190, 755
    minimo, maximo = 24, 30
    d.line((esquerda, topo, esquerda, fundo), fill=TEXTO, width=3)
    d.line((esquerda, fundo, direita, fundo), fill=TEXTO, width=3)
    for valor in range(minimo, maximo + 1):
        y = fundo - (fundo - topo) * (valor - minimo) / (maximo - minimo)
        d.line((esquerda, y, direita, y), fill=GRADE, width=2)
        d.text((100, y - 13), str(valor), font=fonte(22), fill=TEXTO)

    cores = [AZUL, LARANJA, VERDE]
    nomes = list(dados)
    largura_grupo = (direita - esquerda) / 3
    largura_barra = 90
    for gi, chunk in enumerate(chunks):
        centro = esquerda + largura_grupo * (gi + 0.5)
        for si, nome in enumerate(nomes):
            valor = dados[nome][gi]
            x1 = centro + (si - 1) * (largura_barra + 12) - largura_barra / 2
            x2 = x1 + largura_barra
            y = fundo - (fundo - topo) * (valor - minimo) / (maximo - minimo)
            d.rectangle((x1, y, x2, fundo), fill=cores[si])
            texto_central(d, ((x1 + x2) / 2, y - 32), f"{valor:.3f}".replace(".", ","), fonte(19, True), cores[si])
        texto_central(d, (centro, fundo + 18), f"chunk {chunk}", fonte(23, True))

    for i, nome in enumerate(nomes):
        x = esquerda + 40 + i * 280
        d.rectangle((x, 142, x + 28, 170), fill=cores[i])
        d.text((x + 42, 140), nome, font=fonte(23), fill=TEXTO)
    texto_central(d, ((esquerda + direita) / 2, 815), "Tamanho do chunk", fonte(25, True))
    img.save(BASE / "grafico_escalonadores.png", quality=95)


threads = [1, 2, 4, 8, 16]
grafico_linhas(
    "grafico_speedup_forte.png",
    "Escalabilidade forte",
    "Corpus fixo: 1.024 arquivos (105,8 MB) — static, chunk 1",
    threads,
    [("Ideal", [1, 2, 4, 8, 16], True),
     ("Medido", [1.033, 2.020, 4.041, 7.171, 7.589], False)],
    16, [0, 4, 8, 12, 16], "Speed-up",
    lambda v: f"{v:.1f}".replace(".", ",") if v % 1 else str(int(v)),
)
grafico_linhas(
    "grafico_eficiencia_fraca.png",
    "Escalabilidade fraca",
    "Carga fixa por thread: 64 arquivos (6,61 MB) — static, chunk 1",
    threads,
    [("Ideal", [100, 100, 100, 100, 100], True),
     ("Medida", [99.4, 104.3, 99.9, 87.6, 48.3], False)],
    110, [0, 25, 50, 75, 100], "Eficiência (%)",
    lambda v: f"{v:.1f}%".replace(".", ","),
)
grafico_escalonadores()

for nome in (
    "grafico_speedup_forte.png",
    "grafico_eficiencia_fraca.png",
    "grafico_escalonadores.png",
):
    print(BASE / nome)
