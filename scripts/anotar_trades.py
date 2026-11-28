"""Marca nas capturas do Profit (Renko 23R) os trades de retorno a media dos melhores setups
(venda no toque de media lenta: MME42/55 do 23R, MME 27/55 do 42R e 98R, MME72 do 20R, VWAP).

A posicao horizontal sai do horario (eixo de tempo do Profit) e a vertical do nivel da media (escala de preco),
por isso e aproximada: confira no print.
Uso: python -I anotar_trades.py   (le imagens/prints/toques/spec.json e semanas/toques_*_23R.csv)
Saida: imagens/prints/toques/<id>.png e trades_marcados.json (id da captura de cada trade)
"""
import csv
import glob
import json
import os

from PIL import Image, ImageDraw, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.normpath(os.path.join(AQUI, ".."))
PAST = os.path.join(RAIZ, "imagens", "prints", "toques")
LENTAS = {"E42", "E55", "R42_27", "R42_55", "R98_27", "R98_55", "VWAP_D", "VWAP_S", "R20_72"}


def fonte(n, s):
    try:
        return ImageFont.truetype(f"C:/Windows/Fonts/{n}.ttf", s)
    except OSError:
        return ImageFont.load_default()


def minutos(h):
    p = [int(v) for v in h.split(":")]
    return p[0] * 60 + p[1] + (p[2] / 60 if len(p) > 2 else 0)


def x_de(anc, hora):
    t = minutos(hora)
    pts = [(minutos(a), x) for a, x in anc]
    if t <= pts[0][0]:
        return None
    for (t0, x0), (t1, x1) in zip(pts, pts[1:]):
        if t0 <= t <= t1:
            return x0 + (t - t0) / (t1 - t0) * (x1 - x0) if t1 > t0 else x0
    t0, x0 = pts[-1]
    if t - t0 <= 6:  # alem do ultimo rotulo: extrapola ~ 46 px a cada 6 min
        return x0 + (t - t0) / 6 * 46
    return None


def carregar():
    ev = []
    for caminho in sorted(glob.glob(os.path.join(RAIZ, "semanas", "toques_2*_23R.csv"))):
        with open(caminho, encoding="utf-8") as fh:
            for r in csv.DictReader(fh, delimiter=";"):
                if r["cl_ordem"] == "1" and r["lado"] == "V" and r["media"] in LENTAS:
                    ev.append(r)
    return ev


def main():
    spec = json.load(open(os.path.join(PAST, "spec.json"), encoding="utf-8"))
    ev = carregar()
    fb, fr, fs = fonte("segoeuib", 17), fonte("segoeui", 14), fonte("segoeui", 13)
    marcados = {}
    for cap in spec:
        img = Image.open(os.path.join(PAST, cap["src"])).convert("RGB")
        crop = img.crop((0, 56, 1190, 680))
        W, H = 1190 + 470, 624 + 64 + 26
        tela = Image.new("RGB", (W, H), (20, 24, 32))
        d = ImageDraw.Draw(tela, "RGBA")
        tela.paste(crop, (0, 64))
        d.text((14, 12), f"Profit · WINZ26 Renko 23R · {cap['titulo']} · vendas no toque de média lenta", font=fb, fill=(232, 235, 241))
        p0, y0, pxp = cap["preco"]
        mine = []
        for r in ev:
            if r["dia"] != cap["dia"]:
                continue
            x = x_de(cap["anc"], r["hora"])
            if x is None:
                continue
            y = y0 + (p0 - float(r["nivel"])) * pxp
            if not (82 <= y <= 440 and 36 <= x <= 1105):
                continue
            mine.append((r, x, y))
        mine.sort(key=lambda t: t[0]["hora"])
        px, py = 1190 + 12, 66
        d.text((px, py), "Trades neste print (stop 230 / gain 575)", font=fb, fill=(232, 235, 241))
        py += 26
        d.text((px, py), "#  hora      média     nível    resultado", font=fs, fill=(151, 161, 179))
        py += 20
        for i, (r, x, y) in enumerate(mine, 1):
            res = float(r["a_S2_T5"])
            ok = res > 0
            cor = (76, 195, 138, 255) if ok else (240, 118, 107, 255)
            cy = y + 64 - 56
            d.line((x, 64, x, 64 + 560), fill=cor[:3] + (70,), width=1)
            d.ellipse((x - 12, cy - 12, x + 12, cy + 12), outline=cor, width=3)
            d.text((x - 4, cy - 34), str(i), font=fs, fill=cor)
            d.text((px, py), f"{i:<2} {r['hora']}  {r['media']:<7} {int(float(r['nivel'])):>7}   {'ALVO +575' if ok else 'STOP -230'}", font=fs, fill=cor[:3])
            py += 19
            marcados[f"{r['dia']} {r['hora']} {r['media']}"] = cap["id"]
        if not mine:
            d.text((px, py), "nenhum trade dentro da área visível", font=fs, fill=(151, 161, 179))
        d.text((14, H - 22), "Posição pelo horário do eixo e pelo nível da média: aproximada, confira no print. Não é recomendação de investimento.", font=fs, fill=(151, 161, 179))
        out = os.path.join(PAST, cap["id"] + ".png")
        tela.save(out)
        print(out, len(mine))
    json.dump(marcados, open(os.path.join(PAST, "trades_marcados.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print("marcados:", len(marcados))


if __name__ == "__main__":
    main()
