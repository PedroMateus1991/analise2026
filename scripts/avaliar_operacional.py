"""Avalia candidatos de operacional (filtros sobre os sinais do scalp4) num CSV semanal.

Uso: python -I avaliar_operacional.py [csv_semana]
Reaproveite com outras semanas: os mesmos candidatos sao medidos de novo, sem
reotimizar (teste fora da amostra de verdade).
"""
import csv
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
CSV = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, "..", "semanas", "semana_2026-11-23_23R.csv")


def f(x):
    return float(x.replace(",", ".")) if x != "" else float("nan")


rows = []
with open(CSV, encoding="utf-8") as fh:
    for r in csv.DictReader(fh, delimiter=";"):
        d = {k: (v if k in ("semana", "ativo", "dia", "hora", "lado", "sinal") else f(v)) for k, v in r.items()}
        d["h"] = int(d["hora"][:2])
        d["min"] = int(d["hora"][:2]) * 60 + int(d["hora"][3:5])
        sg = 1 if d["lado"] == "V" else -1
        d["ate25_29"] = (sg * d["dist_e25"] > 0 or sg * d["dist_e29"] > 0) and sg * d["dist_e42"] <= 0 and sg * d["dist_e55"] <= 0
        rows.append(d)
sig = [r for r in rows if r["sinal"]]
z = sig[0]["tijolo_pts"]

CANDIDATOS = {
    "0. Todos os sinais": lambda r: True,
    "A. so 1o e 2o sinal do episodio": lambda r: r["seq"] <= 2,
    "B. fechamento atravessa 2 ou 3 medias": lambda r: 2 <= r["n_emas"] <= 3,
    "C. A + B": lambda r: r["seq"] <= 2 and 2 <= r["n_emas"] <= 3,
    "D. C + depois das 10:00": lambda r: r["seq"] <= 2 and 2 <= r["n_emas"] <= 3 and r["h"] >= 10,
    "E. C + |hist| entre 150 e 300": lambda r: r["seq"] <= 2 and 2 <= r["n_emas"] <= 3 and 150 <= abs(r["hist"]) < 300,
    "F. so |hist| entre 150 e 300": lambda r: 150 <= abs(r["hist"]) < 300,
}


def res(r, S, T):
    return r[f"r_S{S}_T{T}"]


def stats(it, S=2, T=5):
    n = len(it)
    if not n:
        return None
    w = sum(1 for r in it if abs(res(r, S, T) - T * z) < 0.5)
    tot = sum(res(r, S, T) for r in it)
    return n, w / n, tot / n, tot


print(f"Arquivo: {os.path.basename(CSV)}  tijolo={z:.0f} pts  | payoff padrao stop 2 / gain 5 (equilibrio 28.6%)\n")
dias = sorted({r["dia"] for r in sig})
for nome, fn in CANDIDATOS.items():
    it = [r for r in sig if fn(r)]
    s = stats(it)
    if not s:
        print(f"{nome}: sem sinais")
        continue
    n, wr, ex, tot = s
    por_dia = []
    for d in dias:
        sd = stats([r for r in it if r["dia"] == d])
        por_dia.append(f"{d[8:]}:{sd[0]}/{sd[2]:+.0f}" if sd else f"{d[8:]}:0")
    tr = stats([r for r in it if r["dia"] <= "2026-11-25"])
    te = stats([r for r in it if r["dia"] > "2026-11-25"])
    print(f"{nome}\n   n={n} acerto={wr:.1%} exp={ex:+.1f} pts/trade ({ex*0.2:+.2f} R$) total={tot:+.0f} pts ({tot*0.2:+.0f} R$) | trades/dia={n/len(dias):.1f}")
    print(f"   por dia (n/exp): {'  '.join(por_dia)}")
    print(f"   treino 23-25: {('n=%d exp=%+.0f' % (tr[0], tr[2])) if tr else '-'} | teste 26-27: {('n=%d exp=%+.0f' % (te[0], te[2])) if te else '-'}")

print("\n--- melhor payoff para cada candidato (n>=15), ordenado por expectativa ---")
for nome, fn in CANDIDATOS.items():
    it = [r for r in sig if fn(r)]
    if len(it) < 15:
        continue
    g = []
    for S in (1, 2, 3, 4):
        for T in (1, 2, 3, 4, 5, 6, 8, 10):
            n, wr, ex, tot = stats(it, S, T)
            g.append((ex, S, T, wr))
    g.sort(reverse=True)
    pad = stats(it, 2, 5)
    print(f"{nome}: padrao 2/5 = {pad[2]:+.0f} | top: " + "; ".join(f"{S}/{T} {ex:+.0f} ({wr:.0%})" for ex, S, T, wr in g[:3]))

print("\n--- pior sequencia e queda maxima (payoff 2/5, ordem cronologica) ---")
for nome, fn in CANDIDATOS.items():
    it = sorted([r for r in sig if fn(r)], key=lambda r: (r["dia"], r["hora"]))
    if not it:
        continue
    cum = pk = dd = 0
    streak = ms = 0
    for r in it:
        x = res(r, 2, 5)
        cum += x
        pk = max(pk, cum)
        dd = max(dd, pk - cum)
        streak = streak + 1 if x < 0 else 0
        ms = max(ms, streak)
    print(f"{nome}: maior queda {dd:.0f} pts ({dd*0.2:.0f} R$), stops seguidos {ms}")
