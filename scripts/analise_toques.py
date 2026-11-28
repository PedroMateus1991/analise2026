"""Analise dos retornos as medias (toques): qual media segura mais o preco, se compensa entrar no
toque ou na virada de box, por horario, e quais confluencias melhoram o resultado.

Uso: python -I analise_toques.py [toques_csv] [rejeicao_csv]
Payoff padrao: stop 2 tijolos / gain 5 tijolos (230 / 575 pts no 23R). Equilibrio de acerto = 28,6%.
"""
import csv
import glob
import itertools
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
SEM = os.path.join(AQUI, "..", "semanas")
TQ = sys.argv[1] if len(sys.argv) > 1 else sorted(glob.glob(os.path.join(SEM, "toques_2*_23R.csv")))[-1]
RJ = sys.argv[2] if len(sys.argv) > 2 else TQ.replace("toques_", "rejeicao_")
S, T = 2, 5
Z = 115
BE = S / (S + T)


def f(x):
    if x == "":
        return float("nan")
    return float(x.replace(",", "."))


def ler(path):
    with open(path, encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter=";"))


raw = ler(TQ)
ev = []
for r in raw:
    d = {k: (v if k in ("dia", "hora", "media", "lado", "hora_b", "cluster") else f(v)) for k, v in r.items()}
    d["m30"] = d["hora"][:2] + (":00" if int(d["hora"][3:5]) < 30 else ":30")
    d["resA"] = d[f"a_S{S}_T{T}"]
    d["resB"] = d[f"b_S{S}_T{T}"]
    ev.append(d)


def stats(it, chave):
    xs = [r[chave] for r in it if r[chave] == r[chave]]
    n = len(xs)
    if not n:
        return None
    w = sum(1 for x in xs if abs(x - T * Z) < 0.5)
    tot = sum(xs)
    dias = {}
    for r in it:
        if r[chave] == r[chave]:
            dias.setdefault(r["dia"], []).append(r[chave])
    pos = sum(1 for v in dias.values() if sum(v) > 0)
    return n, w / n, tot / n, tot, pos, len(dias)


def lin(nome, it, chave, minimo=0):
    s = stats(it, chave)
    if not s or s[0] < minimo:
        return None
    n, wr, ex, tot, pos, nd = s
    return f"  {nome:<38} n={n:4d} acerto={wr:5.1%} exp={ex:7.1f} pts  total={tot:8.0f}  dias+ {pos}/{nd}"


def pr(x):
    if x:
        print(x)


print(f"Arquivo: {os.path.basename(TQ)} | eventos={len(ev)} | payoff stop {S}/gain {T} | equilibrio {BE:.1%}")
medias = sorted({r["media"] for r in ev})

print("\n### 1) Ranking das medias: entrada no TOQUE (A) e na VIRADA DE BOX (B) -- todos os lados")
print(f"  {'media':<8} {'n':>4} {'acerto A':>9} {'exp A':>8} | {'nB':>4} {'acerto B':>9} {'exp B':>8} | held1 held2")
rank = []
for m in medias:
    it = [r for r in ev if r["media"] == m]
    sa, sb = stats(it, "resA"), stats(it, "resB")
    h1 = sum(r["held1"] for r in it) / len(it)
    h2 = sum(r["held2"] for r in it) / len(it)
    rank.append((sa[2], m, sa, sb, h1, h2))
for ex, m, sa, sb, h1, h2 in sorted(rank, reverse=True):
    sb_t = f"{sb[0]:4d} {sb[1]:9.1%} {sb[2]:8.1f}" if sb else "   -         -        -"
    print(f"  {m:<8} {sa[0]:4d} {sa[1]:9.1%} {sa[2]:8.1f} | {sb_t} | {h1:5.1%} {h2:5.1%}")
print("  (held1 = 1 tijolo a favor antes de 1 tijolo contra; held2 = 2 a favor antes de 1 contra)")

print("\n### 2) Quantas vezes cada media 'segura' o preco -- nivel dentro da alta-baixa do tijolo")
rj = ler(RJ)
print(f"  {'media':<8} {'toques':>6} {'corpo':>6} {'pavio':>6} | pavio seguido de fechamento alem da media")
agg = {}
for r in rj:
    a_ = agg.setdefault(r["media"], dict(n=0, corpo=0, pav=0, alem=0, pav_ok=0))
    a_["n"] += 1
    if r["tipo"] == "corpo":
        a_["corpo"] += 1
    else:
        a_["pav"] += 1
        if r["fecha_alem"] != "":
            a_["pav_ok"] += 1
            a_["alem"] += int(r["fecha_alem"])
for m, a_ in sorted(agg.items(), key=lambda kv: -(1 - kv[1]["alem"] / max(1, kv[1]["pav_ok"]))):
    rej = 1 - a_["alem"] / a_["pav_ok"] if a_["pav_ok"] else float("nan")
    print(f"  {m:<8} {a_['n']:6d} {a_['corpo']:6d} {a_['pav']:6d} | rejeicao {rej:5.1%} (n={a_['pav_ok']})")

ev_todos = ev
if "--todos" not in sys.argv:
    ev = [r for r in ev if r["cl_ordem"] == 1]
n_cl = len({r["cluster"] for r in ev_todos})
print(f"\n>>> A partir daqui: {'TODOS os toques' if '--todos' in sys.argv else 'so o PRIMEIRO toque de cada movimento'}"
      f" (n={len(ev)}). {len(ev_todos)} toques = {n_cl} movimentos independentes (varias medias encostam juntas).")

print("\n### 2b) Resultado quando a media foi a PRIMEIRA tocada do movimento")
for m in medias:
    it = [r for r in ev_todos if r["media"] == m and r["cl_ordem"] == 1]
    pr(lin(f"{m}: 1a do movimento (toque)", it, "resA", 5))
    pr(lin(f"{m}: 1a do movimento (virada)", it, "resB", 5))

print("\n### 3) Por lado (venda no toque vindo de baixo; compra no toque vindo de cima)")
for lado, nl in (("V", "venda"), ("C", "compra")):
    it = [r for r in ev if r["lado"] == lado]
    pr(lin(f"{nl}: toque", it, "resA"))
    pr(lin(f"{nl}: virada de box", it, "resB"))

print("\n### 4) Horario (blocos de 30 min) -- entrada no toque / na virada")
for b in sorted({r["m30"] for r in ev}):
    it = [r for r in ev if r["m30"] == b]
    pr(lin(f"{b}  toque", it, "resA"))
    pr(lin(f"{b}  virada", it, "resB"))

print("\n### 5) Alinhamentos (todas as medias juntas)")


def grp(nome, fn, minimo=15):
    for rot, ok in (("sim", True), ("nao", False)):
        it = [r for r in ev if fn(r) == ok]
        pr(lin(f"{nome}: {rot}", it, "resA", minimo))
        pr(lin(f"{'':<{min(len(nome), 30)}}  (virada)", it, "resB", minimo))


grp("MACD alinhado", lambda r: r["hist_alin"] == 1)
grp("MACD crescendo a favor", lambda r: r["hist_cresce"] == 1)
grp("media inclinada a favor", lambda r: r["incl_alin"] == 1)
grp("nivel a favor da VWAP diaria", lambda r: r["vwap_d_alin"] == 1)
grp("nivel a favor da VWAP semanal", lambda r: r["vwap_s_alin"] == 1)
grp("42R: preco a favor das medias", lambda r: r["ctx42"] == 1)
grp("98R: preco a favor das medias", lambda r: r["ctx98"] == 1)
grp("scalp4 do mesmo lado (5 tijolos)", lambda r: r["scalp4"] == 1)
grp("operacional D recente", lambda r: r["scalpD"] == 1)

print("\n### 6) Confluencia: outras medias/VWAPs a menos de 60 pts do nivel tocado")
for lo_, hi_, nome in ((0, 0, "nenhuma"), (1, 1, "1 junto"), (2, 3, "2-3 juntas"), (4, 99, "4 ou mais")):
    it = [r for r in ev if lo_ <= r["prox60"] <= hi_]
    pr(lin(f"{nome}: toque", it, "resA"))
    pr(lin(f"{'':<{len(nome)}}  virada", it, "resB"))
it = [r for r in ev if r["vwap_d_dist"] == r["vwap_d_dist"] and abs(r["vwap_d_dist"]) <= 60]
pr(lin("toque com a VWAP D junto (<=60)", it, "resA"))
pr(lin("virada com a VWAP D junto", it, "resB"))

print("\n### 7) Quem esta por baixo/cima de quem (X = media tocada, Y = outra) -- melhores casos, n>=20")
print("   Venda tende a funcionar com X por BAIXO de Y; compra com X por CIMA.")
achados = []
for lado, nl in (("V", "venda"), ("C", "compra")):
    for m in medias:
        for y in medias + ["VWAP_D", "VWAP_S"]:
            if y == m:
                continue
            for v, nv in ((1, "X acima de Y"), (-1, "X abaixo de Y")):
                it = [r for r in ev if r["lado"] == lado and r["media"] == m and r.get("rel_" + y) == v]
                s = stats(it, "resA")
                if s and s[0] >= 20:
                    achados.append((s[2], nl, m, y, nv, s))
achados.sort(reverse=True)
for ex, nl, m, y, nv, s in achados[:14]:
    print(f"  {nl:<6} {m:<7} {nv:<14} {y:<7} n={s[0]:3d} acerto={s[1]:5.1%} exp={ex:7.1f} dias+ {s[4]}/{s[5]}")
print("  ... e os piores:")
for ex, nl, m, y, nv, s in achados[-6:]:
    print(f"  {nl:<6} {m:<7} {nv:<14} {y:<7} n={s[0]:3d} acerto={s[1]:5.1%} exp={ex:7.1f} dias+ {s[4]}/{s[5]}")

print("\n### 8) Melhores combinacoes (toque), n>=25, ao menos 3 dias positivos")
filtros = {
    "MACD alinhado": lambda r: r["hist_alin"] == 1,
    "VWAP D a favor": lambda r: r["vwap_d_alin"] == 1,
    "42R a favor": lambda r: r["ctx42"] == 1,
    "media inclinada a favor": lambda r: r["incl_alin"] == 1,
    "2+ medias juntas": lambda r: r["prox60"] >= 2,
    "scalp4 recente": lambda r: r["scalp4"] == 1,
    "depois das 10h": lambda r: int(r["hora"][:2]) >= 10,
}
res8 = []
for r_ in (1, 2, 3):
    for combo in itertools.combinations(filtros, r_):
        it = [r for r in ev if all(filtros[c](r) for c in combo)]
        s = stats(it, "resA")
        if s and s[0] >= 25 and s[4] >= 3:
            res8.append((s[2], " + ".join(combo), s))
res8.sort(reverse=True)
for ex, nome, s in res8[:12]:
    print(f"  exp={ex:7.1f} n={s[0]:4d} acerto={s[1]:5.1%} dias+ {s[4]}/{s[5]}  {nome}")
print(f"  (combinacoes testadas com n>=25 e 3 dias+: {len(res8)} -> parte do 'melhor' e sorte)")

print("\n### 9) Medias dentro do filtro MACD alinhado + VWAP D a favor, toque e virada (n>=12)")
base = [r for r in ev if r["hist_alin"] == 1 and r["vwap_d_alin"] == 1]
for m in medias:
    it = [r for r in base if r["media"] == m]
    pr(lin(f"{m}: toque", it, "resA", 12))
    pr(lin(f"{m}: virada", it, "resB", 12))
