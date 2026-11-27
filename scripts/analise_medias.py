"""Analise das medias (17/25/29/42/55) e filtros do scalp4 a partir do CSV semanal.

Uso: python -I analise_medias.py [caminho_do_csv]
Mede, no payoff stop 2 tijolos / gain 5 tijolos (230/575 no 23R), o que muda
quando o fechamento do tijolo atravessa cada media e em combinacao com MACD,
hora e sequencia. Resultado em pontos por trade.
"""
import csv
import itertools
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
CSV = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, "..", "semanas", "semana_2026-11-23_23R.csv")
S, T = 2, 5


def f(x):
    return float(x.replace(",", ".")) if x != "" else float("nan")


rows = []
with open(CSV, encoding="utf-8") as fh:
    for r in csv.DictReader(fh, delimiter=";"):
        z = f(r["tijolo_pts"])
        d = {k: (v if k in ("semana", "ativo", "dia", "hora", "lado", "sinal") else f(v)) for k, v in r.items()}
        d["z"] = z
        d["res"] = d[f"r_S{S}_T{T}"]
        d["win"] = abs(d["res"] - T * z) < 0.5
        d["h"] = int(d["hora"][:2])
        d["horab"] = "09h" if d["h"] == 9 else ("10-11h" if d["h"] in (10, 11) else "12-13h")
        # distancia atravessada de cada media, em tijolos, positiva = fechamento passou da media
        # (V: fechamento acima da media; C: fechamento abaixo). dist_eXX = close - media.
        sg = 1 if d["lado"] == "V" else -1
        for n in (17, 25, 29, 42, 55):
            d[f"x{n}"] = sg * d[f"dist_e{n}"] / z
        d["histb"] = "<150" if abs(d["hist"]) < 150 else ("150-300" if abs(d["hist"]) < 300 else ">=300")
        d["runb"] = "1" if d["run"] == 1 else ("2-3" if d["run"] <= 3 else "4+")
        d["nb"] = "1" if d["n_emas"] == 1 else ("2-3" if d["n_emas"] <= 3 else "4-5")
        d["seqb"] = "1" if d["seq"] == 1 else ("2" if d["seq"] == 2 else ("3+" if d["seq"] >= 3 else "-"))
        d["x55b"] = "<3 tij" if abs(d["dist_e55"]) / z < 3 else ("3-6 tij" if abs(d["dist_e55"]) / z < 6 else ">=6 tij")
        rows.append(d)

sig = [r for r in rows if r["sinal"]]
base = [r for r in rows if not r["sinal"]]
be = S / (S + T)


def st(it):
    n = len(it)
    if not n:
        return None
    w = sum(r["win"] for r in it)
    return dict(n=n, w=w, wr=w / n, exp=sum(r["res"] for r in it) / n, tot=sum(r["res"] for r in it))


def line(nome, it):
    s = st(it)
    if not s:
        return f"  {nome:<34} n=  0"
    dias = {}
    for r in it:
        dias.setdefault(r["dia"], []).append(r["res"])
    pos = sum(1 for v in dias.values() if sum(v) > 0)
    return f"  {nome:<34} n={s['n']:4d} acerto={s['wr']:5.1%} exp={s['exp']:7.1f} pts  dias+ {pos}/{len(dias)}"


print(f"Arquivo: {os.path.basename(CSV)}   payoff stop {S} / gain {T} tijolos   equilibrio {be:.1%}")
print(line("TODOS os sinais", sig))
print(line("Base (tijolos sem sinal)", base))

print("\n### 1) O que cada media diz? (sinais; distancia atravessada pelo fechamento, em tijolos)")
for n in (17, 25, 29, 42, 55):
    print(f"-- media {n}")
    for nome, lo, hi in (("nao atravessou (<=0)", -99, 0), ("0 a 1 tijolo", 0, 1), ("1 a 2 tijolos", 1, 2), ("2 a 4 tijolos", 2, 4), (">4 tijolos", 4, 99)):
        it = [r for r in sig if lo < r[f"x{n}"] <= hi]
        print(line(nome, it))

print("\n### 2) Quantas medias o fechamento atravessou")
for k in (1, 2, 3, 4, 5):
    print(line(f"{k} de 5", [r for r in sig if r["n_emas"] == k]))

print("\n### 3) Media mais distante que o fechamento atravessou")
for n in (17, 25, 29, 42, 55):
    it = [r for r in sig if r[f"x{n}"] > 0 and all(r[f"x{m}"] <= 0 for m in (17, 25, 29, 42, 55) if m > n)]
    print(line(f"para na media {n}", it))

print("\n### 4) Spread entre media 25 e 29 (confirmacao de tendencia), em tijolos")
for nome, lo, hi in (("<0,25", 0, 0.25), ("0,25-0,5", 0.25, 0.5), ("0,5-1", 0.5, 1.0), (">1", 1.0, 99)):
    it = [r for r in sig if lo <= abs(r["spread_25_29"]) / r["z"] < hi]
    print(line(nome, it))

print("\n### 5) Cada filtro, sozinho (sinais)")
for chave, titulo in (("horab", "hora"), ("histb", "|hist| MACD"), ("runb", "run (tijolos seguidos)"), ("nb", "medias cruzadas"), ("seqb", "ordem no episodio"), ("x55b", "distancia a media 55"), ("lado", "lado")):
    print(f"-- {titulo}")
    for v in sorted({r[chave] for r in sig}):
        print(line(str(v), [r for r in sig if r[chave] == v]))

print("\n### 6) Melhores combinacoes de 2 filtros (n>=15, ao menos 3 dias com resultado positivo)")
chaves = ["horab", "histb", "runb", "nb", "seqb", "x55b", "lado"]
achados = []
for a, b in itertools.combinations(chaves, 2):
    va = sorted({r[a] for r in sig})
    vb = sorted({r[b] for r in sig})
    for x in va:
        for y in vb:
            it = [r for r in sig if r[a] == x and r[b] == y]
            s = st(it)
            if not s or s["n"] < 15:
                continue
            dias = {}
            for r in it:
                dias.setdefault(r["dia"], []).append(r["res"])
            pos = sum(1 for v in dias.values() if sum(v) > 0)
            achados.append((s["exp"], s["n"], s["wr"], pos, len(dias), f"{a}={x} & {b}={y}"))
achados.sort(reverse=True)
for e, n, wr, p, nd, nome in achados[:12]:
    print(f"  exp={e:7.1f} n={n:3d} acerto={wr:5.1%} dias+ {p}/{nd}  {nome}")
print(f"  (total de combinacoes testadas com n>=15: {len(achados)} -> parte do 'melhor' e sorte)")

print("\n### 7) Teste fora da amostra: regra escolhida em 23-25/11, avaliada em 26-27/11")
treino = [r for r in sig if r["dia"] <= "2026-11-25"]
teste = [r for r in sig if r["dia"] > "2026-11-25"]
for nome, fn in (
    ("hist 150-300", lambda r: r["histb"] == "150-300"),
    ("run 2-3", lambda r: r["runb"] == "2-3"),
    ("2-3 medias", lambda r: r["nb"] == "2-3"),
    ("hora != 09h", lambda r: r["horab"] != "09h"),
    ("hist<300 & run>=2 & hora!=09h", lambda r: r["histb"] != ">=300" and r["runb"] != "1" and r["horab"] != "09h"),
):
    print(f"-- {nome}")
    print("   treino:" + line("", [r for r in treino if fn(r)]).strip())
    print("   teste :" + line("", [r for r in teste if fn(r)]).strip())
