"""Efeito do contexto de Renko maior (42R = 15 min, 98R = 60 min) nos sinais do scalp4.

Uso: python -I analise_contexto.py [csv_semana]
Mede, no payoff stop 2 / gain 5 tijolos, se o resultado muda quando o preco esta acima, entre
ou abaixo das medias 27 e 55 do Renko maior, e se isso esta a favor ou contra do lado do sinal.
"""
import csv
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
        d = {k: (v if k in ("semana", "ativo", "dia", "hora", "lado", "sinal") else f(v)) for k, v in r.items()}
        d["res"] = d[f"r_S{S}_T{T}"]
        d["win"] = abs(d["res"] - T * d["tijolo_pts"]) < 0.5
        d["seq"] = int(d["seq"])
        d["h"] = int(d["hora"][:2])
        d["D"] = d["seq"] <= 2 and 2 <= d["n_emas"] <= 3 and d["h"] >= 10 if d["sinal"] else False
        rows.append(d)
sig = [r for r in rows if r["sinal"]]
base = [r for r in rows if not r["sinal"]]
be = S / (S + T)
z = rows[0]["tijolo_pts"]


def linha(nome, it):
    n = len(it)
    if not n:
        return f"  {nome:<44} n=  0"
    w = sum(r["win"] for r in it)
    ex = sum(r["res"] for r in it) / n
    dias = {}
    for r in it:
        dias.setdefault(r["dia"], []).append(r["res"])
    pos = sum(1 for v in dias.values() if sum(v) > 0)
    return f"  {nome:<44} n={n:4d} acerto={w/n:5.1%} exp={ex:7.1f} pts  dias+ {pos}/{len(dias)}"


NOMES = {42: "42R (15 min, azuis)", 98: "98R (60 min)"}
print(f"Arquivo: {os.path.basename(CSV)} | tijolo {z:.0f} pts | payoff stop {S} / gain {T} | equilibrio {be:.1%}")
print(linha("TODOS os sinais", sig))
print(linha("Base (sem sinal)", base))

for n in (42, 98):
    print(f"\n==================== {NOMES[n]} ====================")
    print("Posicao do preco em relacao as medias 27 e 55 (cru, sem olhar o lado):")
    for lado, nl in (("V", "venda"), ("C", "compra")):
        for pos, np_ in ((1, "acima das duas"), (0, "entre as duas"), (-1, "abaixo das duas")):
            it = [r for r in sig if r["lado"] == lado and r[f"pos{n}"] == pos]
            print(linha(f"{nl}: preco {np_}", it))
    print("\nA favor / contra do movimento (a favor: venda abaixo das medias, compra acima):")
    for nome, chave in (("posicao (preco x medias)", f"alin_pos{n}"), ("tendencia (27 x 55)", f"alin_tend{n}"),
                        ("inclinacao da media 27", f"alin_incl{n}")):
        print(f"-- {nome}")
        for v, nv in ((1, "a favor"), (0, "entre/neutro"), (-1, "contra")):
            sub = [r for r in sig if r[chave] == v]
            if sub:
                print(linha(f"sinais, {nv}", sub))
        for v, nv in ((1, "a favor"), (-1, "contra")):
            sub = [r for r in base if r[chave] == v]
            if sub:
                print(linha(f"base,   {nv}", sub))
    print("\nPor lado (a favor pela posicao):")
    for lado, nl in (("V", "venda"), ("C", "compra")):
        for v, nv in ((1, "a favor"), (0, "entre"), (-1, "contra")):
            print(linha(f"{nl}, {nv}", [r for r in sig if r["lado"] == lado and r[f"alin_pos{n}"] == v]))
    print("\nDistancia do fechamento a media 27 do Renko maior (em tijolos de 23R; + = a favor):")
    for nome, lo, hi in (("< -20 (contra, longe)", -999, -20), ("-20 a -8", -20, -8), ("-8 a 0", -8, 0),
                         ("0 a 8", 0, 8), ("8 a 20", 8, 20), ("> 20 (a favor, longe)", 20, 999)):
        it = []
        for r in sig:
            sg = -1 if r["lado"] == "V" else 1
            dd = sg * r[f"dist{n}_27"] / z  # >0 = preco do lado favoravel da media
            if lo <= dd < hi:
                it.append(r)
        print(linha(nome, it))
    print("\nIncerteza da calibracao (preco a menos de %d pts de uma das medias):" % (250 if n == 42 else 300))
    print(linha("sinais incertos", [r for r in sig if r[f"incerto{n}"] == 1]))
    print(linha("sinais fora da faixa de incerteza", [r for r in sig if r[f"incerto{n}"] == 0]))

print("\n==================== COMBINADO COM O OPERACIONAL D ====================")
print(linha("D (1o/2o sinal, 2-3 medias, depois das 10h)", [r for r in sig if r["D"]]))
for n in (42, 98):
    for v, nv in ((1, "a favor"), (0, "entre"), (-1, "contra")):
        print(linha(f"D + {n}R posicao {nv}", [r for r in sig if r["D"] and r[f"alin_pos{n}"] == v]))
    print(linha(f"D + {n}R posicao a favor ou entre", [r for r in sig if r["D"] and r[f"alin_pos{n}"] >= 0]))
print(linha("D + 42R a favor + 98R a favor", [r for r in sig if r["D"] and r["alin_pos42"] == 1 and r["alin_pos98"] == 1]))
print(linha("D + 42R tendencia a favor", [r for r in sig if r["D"] and r["alin_tend42"] == 1]))
print(linha("D + 42R inclinacao a favor", [r for r in sig if r["D"] and r["alin_incl42"] == 1]))

print("\n==================== TODOS OS SINAIS, FILTRO 42R ====================")
for v, nv in ((1, "a favor"), (0, "entre"), (-1, "contra")):
    print(linha(f"42R posicao {nv}", [r for r in sig if r["alin_pos42"] == v]))
print(linha("42R posicao a favor + 98R posicao a favor", [r for r in sig if r["alin_pos42"] == 1 and r["alin_pos98"] == 1]))
print(linha("42R a favor + tendencia a favor", [r for r in sig if r["alin_pos42"] == 1 and r["alin_tend42"] == 1]))
