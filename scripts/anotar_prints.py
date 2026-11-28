"""Anota capturas do Profit (Renko 23R) com as setas do indicador e os sinais calculados.

Para cada janela: detecta as setas (fucsia = venda, verde-limao = compra) por cor e forma,
compara com os sinais do CSV semanal no mesmo trecho de tempo e grava um PNG anotado.

Uso: python -I anotar_prints.py janelas.json
janelas.json = lista de {"id", "src", "titulo", "trechos": [{"dia", "x0", "x1", "t0", "t1"}]}
  src    : caminho da captura (jpg/png) do Profit
  trechos: pedaco horizontal da captura (x0..x1) que pertence a cada dia e o intervalo
           de horas visivel nele (so a janela 09:00-14:00 existe no CSV).
Saida: ../imagens/prints/<id>.png e ../imagens/prints/conferencia_setas.csv
"""
import csv
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.normpath(os.path.join(AQUI, ".."))
SAIDA = os.path.join(RAIZ, "imagens", "prints")
CSV = os.environ.get("ANOTAR_CSV") or os.path.join(RAIZ, "semanas", "semana_2026-11-23_23R.csv")
DIAS_PT = {"2026-11-23": "segunda 23/11", "2026-11-24": "terça 24/11", "2026-11-25": "quarta 25/11",
           "2026-11-26": "quinta 26/11", "2026-11-27": "sexta 27/11"}


def fonte(n, s):
    try:
        return ImageFont.truetype(f"C:/Windows/Fonts/{n}.ttf", s)
    except OSError:
        return ImageFont.load_default()


def f(x):
    return float(x.replace(",", ".")) if x != "" else float("nan")


def carregar_sinais():
    por_dia = {}
    with open(CSV, encoding="utf-8") as fh:
        for r in csv.DictReader(fh, delimiter=";"):
            if r["sinal"]:
                por_dia.setdefault(r["dia"], []).append(r)
    return por_dia


def detectar(img):
    """Retorna lista de (x, y, tipo) com tipo 'V' (fucsia) ou 'C' (verde) no painel de preco."""
    a = np.asarray(img.convert("RGB")).astype(int)
    h, w, _ = a.shape
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    fuc = (r > 145) & (r < 235) & (g > 30) & (g < 115) & (b > 105) & (b < 210) & (r - g > 65) & (b - g > 40)
    ver = (g > 205) & (r < 70) & (b < 70)
    regiao = np.zeros((h, w), bool)
    regiao[166:438, 36:1108] = True
    out = []
    for mask, tipo in ((fuc & regiao, "V"), (ver & regiao, "C")):
        # nucleo: janela 5x5 com >= 18 pixels da cor (remove linhas finas e tracejados)
        cs = np.pad(mask.astype(int), ((1, 0), (1, 0))).cumsum(0).cumsum(1)
        k = 5
        soma = cs[k:, k:] - cs[:-k, k:] - cs[k:, :-k] + cs[:-k, :-k]
        nucleo = np.zeros_like(mask)
        nucleo[k // 2:k // 2 + soma.shape[0], k // 2:k // 2 + soma.shape[1]] = soma >= (22 if tipo == "C" else 18)
        visto = np.zeros_like(nucleo)
        for y0, x0 in zip(*np.nonzero(nucleo)):
            if visto[y0, x0]:
                continue
            pilha = [(y0, x0)]
            visto[y0, x0] = True
            pts = []
            while pilha:
                y, x = pilha.pop()
                pts.append((y, x))
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        yy, xx = y + dy, x + dx
                        if 0 <= yy < h and 0 <= xx < w and nucleo[yy, xx] and not visto[yy, xx]:
                            visto[yy, xx] = True
                            pilha.append((yy, xx))
            if 4 <= len(pts) <= 140:
                ys = [p[0] for p in pts]
                xs = [p[1] for p in pts]
                out.append((sum(xs) / len(xs), sum(ys) / len(ys), tipo))
    return out


def status(nv, nc, mv, mc):
    """Compara setas visiveis no print com sinais calculados (setas podem sair da area visivel)."""
    if nv == mv and nc == mc:
        return "bate"
    return "mais" if (nv > mv or nc > mc) else "menos"


def passa_d(r):
    return int(r["seq"]) <= 2 and 2 <= int(r["n_emas"]) <= 3 and int(r["hora"][:2]) >= 10


def processar(jan, sinais):
    img = Image.open(jan["src"]).convert("RGB")
    setas = detectar(img)
    crop = img.crop((0, 56, 1190, 680))  # so o grafico: sem painel de ordens, conta nem abas
    W, H = 1190 + 600, 624 + 64 + 26
    tela = Image.new("RGB", (W, H), (20, 24, 32))
    d = ImageDraw.Draw(tela, "RGBA")
    fb, fr, fs = fonte("segoeuib", 17), fonte("segoeui", 14), fonte("segoeui", 13)
    d.text((14, 12), f"Profit · WINZ26 Renko 23R · {jan['titulo']}", font=fb, fill=(232, 235, 241))
    tela.paste(crop, (0, 64))
    oy = 64 - 56
    linhas = []
    resumo = []
    for tr in jan["trechos"]:
        x0, x1 = tr["x0"], tr["x1"]
        d.rectangle((x0, 64, x1, 68), fill=(110, 160, 255, 255))
        d.text((x0 + 4, 44), DIAS_PT[tr["dia"]], font=fs, fill=(110, 160, 255))
        mine = [r for r in sinais.get(tr["dia"], []) if tr["t0"] <= r["hora"][:5] <= tr["t1"]]
        mine.sort(key=lambda r: r["hora"])
        arrows = sorted([s for s in setas if x0 <= s[0] <= x1], key=lambda s: s[0])
        nv = sum(1 for s in arrows if s[2] == "V")
        nc = sum(1 for s in arrows if s[2] == "C")
        mv = sum(1 for r in mine if r["sinal"] == "V")
        mc = sum(1 for r in mine if r["sinal"] == "C")
        for i, (x, y, t) in enumerate(arrows, 1):
            cor = (240, 118, 107, 255) if t == "V" else (76, 195, 138, 255)
            cx, cy = x, y + oy
            d.ellipse((cx - 13, cy - 13, cx + 13, cy + 13), outline=cor, width=2)
            d.text((cx - 4, cy - 31 if t == "V" else cy + 14), str(i), font=fs, fill=cor)
        resumo.append((tr["dia"], tr["t0"], tr["t1"], nv, nc, mv, mc))
        linhas.append((tr, arrows, mine))
    px, y = 1190 + 12, 66
    d.text((px, y), "Conferência: setas no Profit × sinais calculados", font=fb, fill=(232, 235, 241))
    y += 26
    for dia, t0, t1, nv, nc, mv, mc in resumo:
        st = status(nv, nc, mv, mc)
        cor = (76, 195, 138) if st == "bate" else (229, 180, 90)
        d.text((px, y), f"{DIAS_PT[dia]} {t0}–{t1}", font=fr, fill=(232, 235, 241))
        y += 19
        d.text((px + 8, y), f"setas visíveis ▼ {nv}  ▲ {nc}   |   calculados ▼ {mv}  ▲ {mc}", font=fs, fill=cor)
        y += 18
        d.text((px + 8, y), {"bate": "contagem igual",
                             "menos": "faltam setas no print (podem estar abaixo da área visível)",
                             "mais": "há mais setas no print que sinais calculados"}[st], font=fs, fill=cor)
        y += 22
    y += 4
    d.text((px, y), "Sinais calculados no trecho (stop 230 / gain 575)", font=fb, fill=(232, 235, 241))
    y += 24
    d.text((px, y), "hora      tijolo  lado  seq  médias  MACD   resultado  op.D", font=fs, fill=(151, 161, 179))
    y += 18
    n = 0
    for tr, arrows, mine in linhas:
        for r in mine:
            if y > H - 40:
                break
            res = f(r["r_S2_T5"])
            tag = "ALVO" if abs(res - 575) < 1 else ("STOP" if abs(res + 230) < 1 else "mm")
            cor = (76, 195, 138) if tag == "ALVO" else ((240, 118, 107) if tag == "STOP" else (229, 180, 90))
            d.text((px, y), f"{r['hora']}  {int(r['idx_dia']):>4}   {'▼' if r['sinal']=='V' else '▲'}    {r['seq']:>2}    {r['n_emas']}     {f(r['hist']):>6.0f}   ", font=fs, fill=(214, 219, 228))
            d.text((px + 338, y), f"{tag:<5}", font=fs, fill=cor)
            d.text((px + 392, y), "sim" if passa_d(r) else "não", font=fs, fill=(76, 195, 138) if passa_d(r) else (151, 161, 179))
            y += 17
            n += 1
    if n == 0:
        d.text((px, y), "nenhum sinal calculado neste trecho", font=fs, fill=(151, 161, 179))
    d.text((14, H - 22), "Setas fora da área visível do painel de preço não são contadas. O CSV cobre 09:00–14:00. Não é recomendação de investimento.", font=fs, fill=(151, 161, 179))
    os.makedirs(SAIDA, exist_ok=True)
    out = os.path.join(SAIDA, f"{jan['id']}.png")
    tela.save(out)
    return out, resumo


def main():
    janelas = json.load(open(sys.argv[1], encoding="utf-8"))
    sinais = carregar_sinais()
    linhas = [["janela", "dia", "de", "ate", "setas_venda", "setas_compra", "calc_venda", "calc_compra", "bate"]]
    for jan in janelas:
        out, resumo = processar(jan, sinais)
        for dia, t0, t1, nv, nc, mv, mc in resumo:
            linhas.append([jan["id"], dia, t0, t1, nv, nc, mv, mc, status(nv, nc, mv, mc)])
        print(out, [(r[0][8:], r[3:]) for r in resumo])
    with open(os.path.join(SAIDA, "conferencia_setas.csv"), "w", encoding="utf-8", newline="") as fh:
        csv.writer(fh, delimiter=";").writerows(linhas)


if __name__ == "__main__":
    main()
