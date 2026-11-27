"""Gera o CSV consolidado de uma semana para o dashboard.

Cada linha = um tijolo de Renko dentro da janela (padrao 09:00-14:00).
Coluna `sinal` = V (venda), C (compra) ou vazio (tijolo sem sinal, usado como
base de comparacao). Para cada linha o desfecho e calculado, a partir do
fechamento do tijolo, para uma grade de stops x alvos (em tijolos).

Uso (na pasta scripts):
  python -I gerar_semana.py --ticks 23 --aquecimento 2026-11-19 \
      --dias 2026-11-23,2026-11-24,2026-11-25,2026-11-26,2026-11-27

Entrada : ../dados/precos_AAAA-MM-DD.csv  (saida de reduce.py)
Saida   : ../semanas/semana_<primeiro dia>_<ticks>R.csv
"""
import argparse
import os
import sys

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import renko  # noqa: E402

PONTOS_POR_TICK = 5  # WIN: 1 tick = 5 pontos
STOPS = (1, 2, 3, 4)  # em tijolos
ALVOS = (1, 2, 3, 4, 5, 6, 8, 10)  # em tijolos
DEFAULT_S, DEFAULT_T = 2, 5  # regra do Pedro: stop 2 tijolos, gain 5 tijolos


def a(n):
    return 2.0 / (n + 1)


def seg(t):
    h, m, s = t.split(":")
    return int(h) * 3600 + int(m) * 60 + int(s)


def hms(s):
    return f"{s // 3600:02d}:{s % 3600 // 60:02d}:{s % 60:02d}"


def num(x, nd=1):
    return str(round(float(x), nd)).replace(".", ",")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ticks", type=int, default=23)
    ap.add_argument("--aquecimento", default="2026-11-19", help="dia anterior, so para aquecer indicadores")
    ap.add_argument("--dias", required=True, help="dias da semana separados por virgula")
    ap.add_argument("--dados", default=os.path.join(AQUI, "..", "dados"))
    ap.add_argument("--saida", default=None)
    ap.add_argument("--ini", default="09:00:00")
    ap.add_argument("--fim", default="14:00:00")
    ap.add_argument("--ativo", default="WINZ26")
    args = ap.parse_args()

    size = args.ticks * PONTOS_POR_TICK
    dias = [d.strip() for d in args.dias.split(",")]
    todos = [args.aquecimento] + dias
    ini, fim = seg(args.ini), seg(args.fim)

    ticks = {}
    bricks = []
    prev_close = None
    for d in todos:
        rows = renko.load(os.path.join(args.dados, f"precos_{d}.csv"))
        ts = np.array([seg(t) for t, p, ag in rows], dtype=np.int32)
        ps = np.array([p for t, p, ag in rows], dtype=np.float64)
        ticks[d] = (ts, ps)
        # a grade do Renko e ancorada no primeiro preco do dia; o gap de abertura e preenchido
        # com tijolos a partir do fechamento do ultimo tijolo do dia anterior (como o Profit faz).
        br, _ = renko.build([(t, p) for t, p, ag in rows], size, None)
        pre = []
        if prev_close is not None and rows:
            gap = rows[0][1] - prev_close
            step = size if gap > 0 else -size
            cur = prev_close
            for _ in range(-int(-abs(gap) // size)):  # arredonda para cima (Profit: 790 pts = 7 tijolos de 115)
                pre.append((rows[0][0], cur, cur + step, 1 if step > 0 else -1))
                cur += step
        todos_br = pre + br
        for i, (t, o, c, dr) in enumerate(todos_br, 1):
            bricks.append(dict(dia=d, idx=i, t=seg(t), o=o, c=c, dir=dr, gap=i <= len(pre)))
        if todos_br:
            prev_close = todos_br[-1][2]

    # indicadores (continuam entre os dias)
    e = {n: None for n in (9, 17, 25, 29, 42, 55)}
    L = C = sg = None
    for b in bricks:
        for n in e:
            e[n] = b["c"] if e[n] is None else e[n] + a(n) * (b["c"] - e[n])
        L = b["c"] if L is None else L + a(89) * (b["c"] - L)
        C = b["c"] if C is None else C + a(21) * (b["c"] - C)
        m = C - L
        sg = m if sg is None else sg + a(42) * (m - sg)
        b["e"] = dict(e)
        b["macd"] = m
        b["hist"] = m - sg

    # sinais (logica literal do ___scalp4_Pedro_2026_: `abertura` = abertura do tijolo, validada
    # contra as setas do Profit na segunda 23/11: candles 24, 28 e 29)
    for b in bricks:
        ee, o, c, h = b["e"], b["o"], b["c"], b["hist"]
        acima = o > ee[17] or c > ee[25] or c > ee[29] or c > ee[42] or c > ee[55]
        abaixo = o < ee[17] or c < ee[25] or c < ee[29] or c < ee[42] or c < ee[55]
        v = c > o and acima and h < 0 and h < -60 and o <= ee[55] and ee[25] < ee[29]
        k = c < o and abaixo and h > 0 and h > 60 and o >= ee[55] and ee[25] > ee[29]
        b["sig"] = "V" if v else ("C" if k else "")

    last = {}
    prev = None
    run = 0
    for b in bricks:
        run = run + 1 if (prev and prev["dia"] == b["dia"] and prev["dir"] == b["dir"]) else 1
        b["run"] = run
        prev = b
        if b["sig"]:
            k = (b["dia"], b["sig"])
            b["seq"] = last[k][1] + 1 if (k in last and b["idx"] - last[k][0] <= 3) else 1
            last[k] = (b["idx"], b["seq"])
        else:
            b["seq"] = 0

    def desfecho(b, lado):
        ts, ps = ticks[b["dia"]]
        i0 = int(np.searchsorted(ts, b["t"], side="right"))
        i1 = int(np.searchsorted(ts, fim, side="right"))
        if i1 <= i0:
            return None
        seg_p, seg_t = ps[i0:i1], ts[i0:i1]
        mov = (seg_p - b["c"]) * (-1.0 if lado == "V" else 1.0)  # positivo = a favor
        r = {}
        for nome, mins in (("10m", 10), ("30m", 30), ("60m", 60), ("fim", None)):
            k = len(mov) if mins is None else max(int(np.searchsorted(seg_t, b["t"] + mins * 60, side="right")), 1)
            r[f"mfe_{nome}"] = float(mov[:k].max())
            r[f"mae_{nome}"] = float(-mov[:k].min())
        r["t_mfe_min"] = float((seg_t[int(np.argmax(mov))] - b["t"]) / 60.0)
        big = len(mov) + 1
        ht, hs = {}, {}
        for T in ALVOS:
            ix = np.flatnonzero(mov >= T * size)
            ht[T] = int(ix[0]) if ix.size else big
        for S in STOPS:
            ix = np.flatnonzero(mov <= -S * size)
            hs[S] = int(ix[0]) if ix.size else big
        for S in STOPS:
            for T in ALVOS:
                if ht[T] == big and hs[S] == big:
                    res = float(mov[-1])
                elif ht[T] < hs[S]:
                    res = float(T * size)
                else:
                    res = float(-S * size)
                r[f"r_S{S}_T{T}"] = res
        # minutos ate a resolucao do payoff padrao (alvo ou stop); vazio se nenhum
        k = min(ht[DEFAULT_T], hs[DEFAULT_S])
        r["min_padrao"] = float((seg_t[k] - b["t"]) / 60.0) if k < big else None
        return r

    saida = args.saida or os.path.join(AQUI, "..", "semanas", f"semana_{dias[0]}_{args.ticks}R.csv")
    os.makedirs(os.path.dirname(saida), exist_ok=True)
    cols = ["semana", "ativo", "renko_ticks", "tijolo_pts", "dia", "hora", "idx_dia", "lado", "sinal", "seq",
            "entrada", "hist", "macd", "run", "n_emas", "dist_e17", "dist_e25", "dist_e29", "dist_e42",
            "dist_e55", "spread_25_29", "mfe_10m", "mae_10m", "mfe_30m", "mae_30m", "mfe_60m", "mae_60m",
            "mfe_fim", "mae_fim", "t_mfe_min", "min_padrao"]
    cols += [f"r_S{S}_T{T}" for S in STOPS for T in ALVOS]

    n_lin = n_sig = 0
    with open(saida, "w", encoding="utf-8", newline="") as f:
        f.write(";".join(cols) + "\n")
        for b in bricks:
            if b["dia"] not in dias or not (ini <= b["t"] <= fim) or b["gap"]:
                continue  # tijolos de gap alimentam as medias mas nao sao operaveis
            lado = b["sig"] or ("V" if b["dir"] == 1 else "C")
            d = desfecho(b, lado)
            if d is None:
                continue
            ee = b["e"]
            if lado == "V":
                ncr = sum(b["c"] > ee[n] for n in (17, 25, 29, 42, 55))
            else:
                ncr = sum(b["c"] < ee[n] for n in (17, 25, 29, 42, 55))
            row = [dias[0], args.ativo, args.ticks, size, b["dia"], hms(b["t"]), b["idx"], lado, b["sig"], b["seq"],
                   int(b["c"]), num(b["hist"]), num(b["macd"]), b["run"], ncr]
            row += [num(b["c"] - ee[n]) for n in (17, 25, 29, 42, 55)] + [num(ee[25] - ee[29])]
            row += [num(d[k]) for k in ("mfe_10m", "mae_10m", "mfe_30m", "mae_30m", "mfe_60m", "mae_60m",
                                       "mfe_fim", "mae_fim", "t_mfe_min")]
            row += [num(d["min_padrao"]) if d["min_padrao"] is not None else ""]
            row += [num(d[f"r_S{S}_T{T}"], 0) for S in STOPS for T in ALVOS]
            f.write(";".join(str(x) for x in row) + "\n")
            n_lin += 1
            n_sig += 1 if b["sig"] else 0
    print(f"{saida}\n  linhas={n_lin}  sinais={n_sig}  tijolo={size} pts")


if __name__ == "__main__":
    main()
