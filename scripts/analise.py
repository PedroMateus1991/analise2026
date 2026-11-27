"""Analise dos sinais do ___scalp4_Pedro_2026_ no WINZ26 (Renko 23R = 115 pts).

Saidas: analise_sinais.csv (um sinal por linha) + resumo no stdout.
Uso: python -I analise.py [modo_hist]   modo_hist: ema42 (padrao) | sma28
"""
import bisect
import sys

import numpy as np

sys.path.insert(0, ".")
import renko  # noqa: E402

DADOS = "C:/Users/Pedro Reis/Documents/01-Projetos e Sistemas/07-Analise Tela/dados"
DIAS = ["2026-11-19", "2026-11-23", "2026-11-24", "2026-11-25", "2026-11-26", "2026-11-27"]
SIZE = 115
JAN_INI, JAN_FIM = 9 * 3600, 14 * 3600
MODO = sys.argv[1] if len(sys.argv) > 1 else "ema42"
OUT = sys.argv[2] if len(sys.argv) > 2 else f"{DADOS}/analise_sinais.csv"


def a(n):
    return 2.0 / (n + 1)


def seg(t):
    h, m, s = t.split(":")
    return int(h) * 3600 + int(m) * 60 + int(s)


def hms(s):
    return f"{s // 3600:02d}:{s % 3600 // 60:02d}:{s % 60:02d}"


# ---------------------------------------------------------------- dados
ticks = {}
bricks = []
for d in DIAS:
    rows = renko.load(f"{DADOS}/precos_{d}.csv")
    ts = np.array([seg(t) for t, p, ag in rows], dtype=np.int32)
    ps = np.array([p for t, p, ag in rows], dtype=np.float64)
    ticks[d] = (ts, ps)
    br, _ = renko.build([(t, p) for t, p, ag in rows], SIZE, None)
    for i, (t, o, c, dr) in enumerate(br, 1):
        bricks.append(dict(dia=d, idx=i, t=seg(t), o=o, c=c, dir=dr))

# ---------------------------------------------------------------- indicadores
e = {n: None for n in (9, 17, 25, 29, 42, 55)}
L = C = None
macds = []
sg = None
for b in bricks:
    for n in e:
        e[n] = b["c"] if e[n] is None else e[n] + a(n) * (b["c"] - e[n])
    L = b["c"] if L is None else L + a(89) * (b["c"] - L)
    C = b["c"] if C is None else C + a(21) * (b["c"] - C)
    m = C - L
    macds.append(m)
    if MODO == "ema42":
        sg = m if sg is None else sg + a(42) * (m - sg)
    else:  # sma28
        sg = sum(macds[-28:]) / len(macds[-28:])
    b["e"] = dict(e)
    b["hist"] = m - sg
    b["macd"] = m

# ---------------------------------------------------------------- sinais
for b in bricks:
    ee, o, c, h = b["e"], b["o"], b["c"], b["hist"]
    acima = c > ee[17] or c > ee[25] or c > ee[29] or c > ee[42] or c > ee[55]
    abaixo = c < ee[17] or c < ee[25] or c < ee[29] or c < ee[42] or c < ee[55]
    venda = c > o and acima and h < 0 and h < -60 and o <= ee[55] and ee[25] < ee[29]
    compra = c < o and abaixo and h > 0 and h > 60 and o >= ee[55] and ee[25] > ee[29]
    b["sig"] = "V" if venda else ("C" if compra else "")

# sequencia dentro de um episodio (mesmo lado, intervalo <= 3 tijolos do mesmo dia)
last = {}
for b in bricks:
    if not b["sig"]:
        continue
    k = (b["dia"], b["sig"])
    if k in last and b["idx"] - last[k][0] <= 3:
        b["seq"] = last[k][1] + 1
    else:
        b["seq"] = 1
    last[k] = (b["idx"], b["seq"])

# tijolo anterior / sequencia de direcao
prev = None
run = 0
for b in bricks:
    if prev and prev["dia"] == b["dia"] and prev["dir"] == b["dir"]:
        run += 1
    else:
        run = 1
    b["run"] = run
    prev = b


# ---------------------------------------------------------------- desfecho
def desfecho(b, lado, fim_s):
    """MFE/MAE e testes alvo/stop a partir do fechamento do tijolo (b['c']).
    lado: 'V' (venda) ou 'C' (compra). Usa ticks com tempo estritamente > t."""
    ts, ps = ticks[b["dia"]]
    i0 = int(np.searchsorted(ts, b["t"], side="right"))
    i1 = int(np.searchsorted(ts, fim_s, side="right"))
    if i1 <= i0:
        return None
    seg_p = ps[i0:i1]
    seg_t = ts[i0:i1]
    ent = b["c"]
    sgn = -1.0 if lado == "V" else 1.0  # direcao favoravel
    mov = (seg_p - ent) * sgn  # positivo = a favor
    r = {}
    for nome, mins in (("10m", 10), ("30m", 30), ("60m", 60), ("fim", None)):
        if mins is None:
            k = len(mov)
        else:
            k = int(np.searchsorted(seg_t, b["t"] + mins * 60, side="right"))
            k = max(k, 1)
        sl = mov[:k]
        r[f"mfe_{nome}"] = float(sl.max())
        r[f"mae_{nome}"] = float(-sl.min())
    # teste alvo/stop (stop contra, alvo a favor), primeiro a ser atingido
    for S, T in ((115, 115), (115, 230), (230, 230), (230, 345), (345, 345), (345, 690)):
        hit_t = np.argmax(mov >= T) if (mov >= T).any() else None
        hit_s = np.argmax(mov <= -S) if (mov <= -S).any() else None
        if hit_t is None and hit_s is None:
            res = float(mov[-1])  # sem desfecho: marca a mercado no fim da janela
            tag = "mm"
        elif hit_s is None or (hit_t is not None and hit_t < hit_s):
            res, tag = float(T), "alvo"
        else:
            res, tag = float(-S), "stop"
        r[f"res_S{S}_T{T}"] = res
        r[f"tag_S{S}_T{T}"] = tag
    # ordem: qual extremo veio primeiro e em quanto tempo
    r["t_mfe_min"] = float((seg_t[int(np.argmax(mov))] - b["t"]) / 60.0)
    return r


sinais = []
base = {"V": [], "C": []}
for b in bricks:
    if b["dia"] == "2026-11-19":
        continue
    if not (JAN_INI <= b["t"] <= JAN_FIM):
        continue
    if b["sig"]:
        d = desfecho(b, b["sig"], JAN_FIM)
        if d:
            sinais.append((b, d))
    # base de comparacao: todo tijolo de alta (lado V) / baixa (lado C) na janela
    lado = "V" if b["dir"] == 1 else "C"
    d = desfecho(b, lado, JAN_FIM)
    if d:
        base[lado].append(d)

# ---------------------------------------------------------------- csv
cols = ["dia", "hora", "lado", "seq", "idx_dia", "entrada", "hist", "macd", "run", "n_emas_cruzadas",
        "dist_e17", "dist_e25", "dist_e29", "dist_e42", "dist_e55", "spread_25_29",
        "mfe_10m", "mae_10m", "mfe_30m", "mae_30m", "mfe_60m", "mae_60m", "mfe_fim", "mae_fim", "t_mfe_min"]
cols += [f"res_S{S}_T{T}" for S, T in ((115, 115), (115, 230), (230, 230), (230, 345), (345, 345), (345, 690))]
with open(OUT, "w", encoding="utf-8") as f:
    f.write(";".join(cols) + "\n")
    for b, d in sinais:
        ee = b["e"]
        lado = b["sig"]
        if lado == "V":
            ncr = sum(b["c"] > ee[n] for n in (17, 25, 29, 42, 55))
        else:
            ncr = sum(b["c"] < ee[n] for n in (17, 25, 29, 42, 55))
        row = [b["dia"], hms(b["t"]), lado, b["seq"], b["idx"], int(b["c"]), round(b["hist"], 1), round(b["macd"], 1),
               b["run"], ncr] + [round(b["c"] - ee[n], 1) for n in (17, 25, 29, 42, 55)] + [round(ee[25] - ee[29], 1)]
        row += [round(d[k], 1) for k in cols[16:25]]
        row += [round(d[c], 1) for c in cols[25:]]
        f.write(";".join(str(x).replace(".", ",") for x in row) + "\n")


# ---------------------------------------------------------------- resumo
def resumo(titulo, itens):
    if not itens:
        print(f"{titulo}: sem dados")
        return
    n = len(itens)
    print(f"\n### {titulo}  (n={n})")
    for h in ("10m", "30m", "60m", "fim"):
        mf = np.array([i[f"mfe_{h}"] for i in itens])
        ma = np.array([i[f"mae_{h}"] for i in itens])
        print(f"  {h:>3}: a favor med={mf.mean():7.0f} mediana={np.median(mf):7.0f} | contra med={ma.mean():7.0f} mediana={np.median(ma):7.0f}")
    for S, T in ((115, 115), (115, 230), (230, 230), (230, 345), (345, 345), (345, 690)):
        res = np.array([i[f"res_S{S}_T{T}"] for i in itens])
        tags = [i[f"tag_S{S}_T{T}"] for i in itens]
        print(f"  stop {S:>3}/alvo {T:>3}: alvo={tags.count('alvo')/n:5.1%} stop={tags.count('stop')/n:5.1%} mm={tags.count('mm')/n:5.1%} expectativa={res.mean():7.1f} pts")


print(f"Modo histograma: {MODO}")
print(f"Sinais na janela 09:00-14:00 (23 a 27/11): {len(sinais)}  V={sum(1 for b, d in sinais if b['sig']=='V')} C={sum(1 for b, d in sinais if b['sig']=='C')}")
resumo("TODOS os sinais V (venda)", [d for b, d in sinais if b["sig"] == "V"])
resumo("TODOS os sinais C (compra)", [d for b, d in sinais if b["sig"] == "C"])
resumo("BASE: todo tijolo de alta como venda", base["V"])
resumo("BASE: todo tijolo de baixa como compra", base["C"])
for lado in ("V", "C"):
    for s in (1, 2, 3):
        it = [d for b, d in sinais if b["sig"] == lado and (b["seq"] == s if s < 3 else b["seq"] >= 3)]
        resumo(f"Lado {lado}, sinal #{s}{'+' if s == 3 else ''} do episodio", it)
