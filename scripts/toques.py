"""Toques e retornos as medias (WINZ26, Renko 23R): detecta quando o preco volta a encostar numa
media, simula a entrada no toque (limite no nivel) e na virada de box (primeiro tijolo a favor
depois do toque) e grava tudo em CSV para o dashboard.

Medias (todas exponenciais dos fechamentos de tijolos, exceto VWAP):
  23R: 9, 17, 25, 29, 42, 55 | 20R: 20 e 72 | 42R: 27 e 55 | 98R: 27 e 55 | VWAP diaria e semanal

Uso (na pasta scripts):
  python -I toques.py --dias 2026-11-23,2026-11-24,2026-11-25,2026-11-26,2026-11-27
Saidas em ../semanas: toques_<1o dia>_23R.csv, rejeicao_<1o dia>_23R.csv, toques_graficos_<1o dia>_23R.json
"""
import argparse
import bisect
import csv
import glob
import json
import os
import sys

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import renko  # noqa: E402

Z = 115  # tijolo 23R em pontos
STOPS = (1, 2, 3, 4)
ALVOS = (1, 2, 3, 4, 5, 6, 8, 10)
DMIN = Z  # distancia minima do preco ate a media antes do retorno
INI_S, FIM_S = 9 * 3600, 14 * 3600  # janela dos toques analisados
FIM_RES = 17 * 3600 + 55 * 60  # resultados acompanhados ate o fim do pregao

# (nome, tijolo em ticks, periodo, deslocamento da grade em pts) -- deslocamentos calibrados na legenda do Profit
MEDIAS = [("E9", 23, 9, 0), ("E17", 23, 17, 0), ("E25", 23, 25, 0), ("E29", 23, 29, 0), ("E42", 23, 42, 0),
          ("E55", 23, 55, 0), ("R20_20", 20, 20, 0), ("R20_72", 20, 72, 0), ("R42_27", 42, 27, -35),
          ("R42_55", 42, 55, -35), ("R98_27", 98, 27, -165), ("R98_55", 98, 55, -165)]
NOMES = [m[0] for m in MEDIAS] + ["VWAP_D", "VWAP_S"]


def num(x, nd=1):
    return str(round(float(x), nd)).replace(".", ",")


def seg(t):
    h, m, s = t.split(":")
    return int(h) * 3600 + int(m) * 60 + int(s)


def hms(s):
    return f"{s // 3600:02d}:{s % 3600 // 60:02d}:{s % 60:02d}"


def a(n):
    return 2.0 / (n + 1)


def tijolos_int(ts, ps, size, prev_close, desloca):
    """Tijolos do dia como (seg, abertura, fechamento, direcao); gap de abertura preenchido (arredonda p/ cima)."""
    pr = ps.tolist()
    if desloca:
        pr[0] = pr[0] + desloca
    br, _ = renko.build(list(zip(ts.tolist(), pr)), size, None)
    pre = []
    if prev_close is not None and len(pr):
        gap = float(ps[0]) - prev_close
        step = size if gap > 0 else -size
        cur = prev_close
        for _ in range(-int(-abs(gap) // size)):
            pre.append((int(ts[0]), cur, cur + step, 1 if step > 0 else -1))
            cur += step
    return pre + br, len(pre)


def carregar_vwap(dados, dias):
    """VWAP diaria e semanal por minuto (volume financeiro / (qtd * 0,20)); valor ao FIM de cada minuto."""
    linhas = []
    for ar in sorted(glob.glob(os.path.join(dados, "WINZ26_F_0_1min_*.csv"))):
        with open(ar, encoding="latin-1") as f:
            for r in csv.reader(f, delimiter=";"):
                if len(r) < 9:
                    continue
                d = r[1]
                dia = f"{d[6:10]}-{d[3:5]}-{d[0:2]}"
                fv = lambda s: float(s.replace(".", "").replace(",", "."))
                linhas.append((dia, seg(r[2]), fv(r[7]), fv(r[8])))
    linhas.sort()
    por_dia = {}
    sem_fin = sem_q = 0.0
    dia_atual = None
    dfin = dq = 0.0
    for dia, s, fin, q in linhas:
        if dia not in dias:
            continue
        if dia != dia_atual:
            dia_atual, dfin, dq = dia, 0.0, 0.0
        dfin += fin
        dq += q
        sem_fin += fin
        sem_q += q
        por_dia.setdefault(dia, ([], [], []))
        por_dia[dia][0].append(s + 60)  # fim do minuto
        por_dia[dia][1].append(dfin / (dq * 0.2) if dq else float("nan"))
        por_dia[dia][2].append(sem_fin / (sem_q * 0.2) if sem_q else float("nan"))
    return por_dia


def vwap_em(vw, dia, s):
    v = vw.get(dia)
    if not v:
        return float("nan"), float("nan")
    i = bisect.bisect_right(v[0], s) - 1
    return (v[1][i], v[2][i]) if i >= 0 else (float("nan"), float("nan"))


def grade_resultados(ps_seg, entrada, lado):
    """Primeiro a ser atingido (alvo ou stop) para a grade stop x alvo, em pontos. ps_seg = precos apos a entrada."""
    fav = (entrada - ps_seg) if lado == "V" else (ps_seg - entrada)
    run_fav = np.maximum.accumulate(fav)
    run_adv = np.maximum.accumulate(-fav)
    n = len(ps_seg)
    it = {T: int(np.searchsorted(run_fav, T * Z, "left")) for T in ALVOS}
    is_ = {S: int(np.searchsorted(run_adv, S * Z, "left")) for S in STOPS}
    res = {}
    for S in STOPS:
        for T in ALVOS:
            if it[T] >= n and is_[S] >= n:
                r = float(fav[-1])
            elif it[T] < is_[S]:
                r = float(T * Z)
            else:
                r = float(-S * Z)
            res[(S, T)] = r
    held1 = int(it[1] < is_[1])
    held2 = int(it[2] < is_[1])
    return res, held1, held2, float(run_fav[-1]), float(run_adv[-1])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dias", required=True)
    ap.add_argument("--dados", default=os.path.join(AQUI, "..", "dados"))
    ap.add_argument("--semana_csv", default=None, help="CSV do gerar_semana (sinais do scalp4)")
    ap.add_argument("--saida", default=os.path.join(AQUI, "..", "semanas"))
    args = ap.parse_args()
    dias = [d.strip() for d in args.dias.split(",")]
    hist = sorted(nm[7:17] for nm in os.listdir(args.dados)
                  if nm.startswith("precos_") and nm.endswith(".csv") and nm[7:17] < dias[0])
    todos = hist + dias
    semana_csv = args.semana_csv or os.path.join(args.saida, f"semana_{dias[0]}_23R.csv")

    # ---------- series de tijolos e medias (continuas entre os dias)
    tamanhos = {}  # ticks -> (periodos, desloca)
    for nome, tk, p, g in MEDIAS:
        tamanhos.setdefault(tk, ([], g))[0].append(p)
    estado = {tk: {p: None for p in tamanhos[tk][0]} for tk in tamanhos}
    prev = {tk: None for tk in tamanhos}
    S = {tk: {"t": [], "c": [], "ema": []} for tk in tamanhos}  # tempos absolutos (dia*86400 + seg)
    B23 = {}
    ticks = {}
    for di, d in enumerate(todos):
        rows = renko.load(os.path.join(args.dados, f"precos_{d}.csv"))
        ts = np.array([seg(r[0]) for r in rows], dtype=np.int64)
        ps = np.array([r[1] for r in rows], dtype=np.float64)
        del rows
        if d in dias:
            ticks[d] = (ts, ps)
        for tk, (periodos, g) in tamanhos.items():
            tb, ngap = tijolos_int(ts, ps, tk * 5, prev[tk], g)
            for (t, o, c, dr) in tb:
                for p in periodos:
                    estado[tk][p] = c if estado[tk][p] is None else estado[tk][p] + a(p) * (c - estado[tk][p])
                S[tk]["t"].append(di * 86400 + t)
                S[tk]["c"].append(c)
                S[tk]["ema"].append([estado[tk][p] for p in periodos])
            if tb:
                prev[tk] = tb[-1][2]
            if tk == 23:
                B23[d] = dict(tb=tb, ngap=ngap, base=len(S[23]["t"]) - len(tb))
        print("  dia", d, "ok", flush=True)

    for tk in S:
        S[tk]["t"] = np.array(S[tk]["t"], dtype=np.int64)
        S[tk]["ema"] = np.array(S[tk]["ema"], dtype=np.float64)
        S[tk]["c"] = np.array(S[tk]["c"], dtype=np.float64)
    # MACD (89,21,42) sobre os fechamentos 23R (continuo)
    L = C = sg = None
    hist_macd = np.zeros(len(S[23]["c"]))
    for i, c in enumerate(S[23]["c"]):
        L = c if L is None else L + a(89) * (c - L)
        C = c if C is None else C + a(21) * (c - C)
        m = C - L
        sg = m if sg is None else sg + a(42) * (m - sg)
        hist_macd[i] = m - sg

    vw = carregar_vwap(args.dados, set(dias))

    # sinais do scalp4 (do CSV semanal)
    sinais = {}
    if os.path.exists(semana_csv):
        with open(semana_csv, encoding="utf-8") as f:
            for r in csv.DictReader(f, delimiter=";"):
                if r["sinal"]:
                    sinais.setdefault(r["dia"], {})[int(r["idx_dia"])] = (r["sinal"], int(r["seq"]), int(r["n_emas"]), r["hora"])

    def niveis(t_abs, dia, s_dia):
        """Nivel de cada media no instante (ultimo tijolo concluido) e VWAPs."""
        out = {}
        for nome, tk, p, g in MEDIAS:
            j = int(np.searchsorted(S[tk]["t"], t_abs, "right")) - 1
            col = tamanhos[tk][0].index(p)
            out[nome] = float(S[tk]["ema"][j, col]) if j >= 0 else float("nan")
        out["VWAP_D"], out["VWAP_S"] = vwap_em(vw, dia, s_dia)
        return out

    eventos, rejeicoes, graficos = [], [], {}
    for d in dias:
        di = todos.index(d)
        ts, ps = ticks[d]
        info = B23[d]
        tb, ngap, base = info["tb"], info["ngap"], info["base"]
        nb = len(tb)
        t_br = np.array([x[0] for x in tb], dtype=np.int64)
        cl = np.array([x[2] for x in tb])
        op = np.array([x[1] for x in tb])
        dr = np.array([x[3] for x in tb])
        hi, lo = np.zeros(nb), np.zeros(nb)
        lvl = {n: np.zeros(nb) for n in NOMES}
        i0s = np.zeros(nb, dtype=np.int64)
        i1s = np.zeros(nb, dtype=np.int64)
        for k in range(nb):
            t_prev = int(t_br[k - 1]) if k > 0 else int(ts[0]) - 1
            i0 = int(np.searchsorted(ts, t_prev, "right"))
            i1 = int(np.searchsorted(ts, t_br[k], "right"))
            i0s[k], i1s[k] = i0, i1
            if i1 > i0:
                hi[k] = max(ps[i0:i1].max(), op[k], cl[k])
                lo[k] = min(ps[i0:i1].min(), op[k], cl[k])
            else:
                hi[k], lo[k] = max(op[k], cl[k]), min(op[k], cl[k])
            nv = niveis(di * 86400 + t_prev, d, t_prev)
            for n in NOMES:
                lvl[n][k] = nv[n]
        graficos[d] = dict(t=t_br.tolist(), o=[int(x) for x in op], c=[int(x) for x in cl],
                           h=[int(x) for x in hi], l=[int(x) for x in lo],
                           gap=[1 if k < ngap else 0 for k in range(nb)],
                           med={n: [None if np.isnan(x) else int(round(x)) for x in lvl[n]] for n in NOMES})

        # rejeicao por tijolo: a media esta dentro da alta-baixa do tijolo
        for k in range(ngap, nb):
            for n in NOMES:
                Lv = lvl[n][k]
                if np.isnan(Lv) or not (lo[k] <= Lv <= hi[k]):
                    continue
                c_lo, c_hi = min(op[k], cl[k]), max(op[k], cl[k])
                tipo = "corpo" if c_lo < Lv < c_hi else ("pavio_acima" if Lv >= c_hi else "pavio_abaixo")
                prox = int(dr[k + 1]) if k + 1 < nb else 0
                alem = ""
                if k + 1 < nb:
                    alem = int((tipo == "pavio_acima" and cl[k + 1] > Lv) or (tipo == "pavio_abaixo" and cl[k + 1] < Lv))
                rejeicoes.append([d, hms(int(t_br[k])), n, int(round(Lv)), tipo, prox, alem, k + 1])

        # eventos de retorno a media
        jend = int(np.searchsorted(ts, min(FIM_RES, int(ts[-1])), "right"))
        for k in range(max(ngap, 2), nb):
            i0, i1 = int(i0s[k]), int(i1s[k])
            if i1 <= i0:
                continue
            seg_p = ps[i0:i1]
            p0 = float(ps[i0 - 1]) if i0 > 0 else float(seg_p[0])
            c1, c2 = cl[k - 1], cl[k - 2]
            for n in NOMES:
                Lv = lvl[n][k]
                if np.isnan(Lv):
                    continue
                if p0 <= Lv - DMIN and seg_p.max() >= Lv and c1 < Lv and c2 < Lv:
                    lado, j = "V", i0 + int(np.argmax(seg_p >= Lv))
                elif p0 >= Lv + DMIN and seg_p.min() <= Lv and c1 > Lv and c2 > Lv:
                    lado, j = "C", i0 + int(np.argmax(seg_p <= Lv))
                else:
                    continue
                t_touch = int(ts[j])
                if not (INI_S <= t_touch <= FIM_S):
                    continue
                path = ps[j:jend]
                if len(path) < 2:
                    continue
                resA, h1, h2, mfeA, maeA = grade_resultados(path, float(Lv), lado)
                # virada de box: primeiro tijolo a favor formado depois do toque
                fav_dir = -1 if lado == "V" else 1
                m = next((kk for kk in range(k, nb) if dr[kk] == fav_dir and t_br[kk] > t_touch), None)
                resB, b_ok, hora_b, ent_b = None, 0, "", ""
                if m is not None:
                    jm = int(np.searchsorted(ts, t_br[m], "right"))
                    if jm > j and jend - jm > 1:
                        janela = ps[j:jm]
                        exceed = float(janela.max() - Lv) if lado == "V" else float(Lv - janela.min())
                        if exceed < 2 * Z:  # a media nao foi rompida por 2 tijolos antes da virada
                            resB = grade_resultados(ps[jm:jend], float(cl[m]), lado)[0]
                            b_ok, hora_b, ent_b = 1, hms(int(t_br[m])), int(cl[m])
                # contexto no instante do toque
                sgn = -1 if lado == "V" else 1  # sentido favoravel
                rel = {y: 0 if (y == n or np.isnan(lvl[y][k])) else (1 if Lv > lvl[y][k] else -1) for y in NOMES}
                prox60 = sum(1 for y in NOMES if y != n and not np.isnan(lvl[y][k]) and abs(lvl[y][k] - Lv) <= 60)
                prox115 = sum(1 for y in NOMES if y != n and not np.isnan(lvl[y][k]) and abs(lvl[y][k] - Lv) <= 115)
                hist_k = float(hist_macd[base + k - 1])
                h_prev = float(hist_macd[base + k - 2])
                vd, vs = lvl["VWAP_D"][k], lvl["VWAP_S"][k]
                inc = Lv - lvl[n][max(0, k - 6)]
                if np.isnan(inc):
                    inc = 0.0  # VWAP ainda indefinida nos primeiros tijolos do dia
                ctx = {}
                for rn in ("R42", "R98"):
                    m27, m55 = lvl[rn + "_27"][k], lvl[rn + "_55"][k]
                    if np.isnan(m27) or np.isnan(m55):
                        ctx[rn] = 0
                    else:
                        ctx[rn] = (1 if p0 > max(m27, m55) else (-1 if p0 < min(m27, m55) else 0)) * sgn
                sc = sc_d = 0
                for kk in range(max(1, k - 4), k + 1):
                    s_ = sinais.get(d, {}).get(kk)
                    if s_ and s_[0] == lado:
                        sc = 1
                        if s_[1] <= 2 and 2 <= s_[2] <= 3 and int(s_[3][:2]) >= 10:
                            sc_d = 1
                nan_ = lambda x: np.isnan(x)
                linha = dict(dia=d, hora=hms(t_touch), idx=k + 1, media=n, lado=lado, nivel=int(round(Lv)),
                             p0=int(p0), dist_antes=int(round(abs(p0 - Lv))), tijolo_dir=int(dr[k]),
                             b_ok=b_ok, hora_b=hora_b, entrada_b=ent_b, held1=h1, held2=h2,
                             mfe=int(mfeA), mae=int(maeA), hist=hist_k, hist_alin=int((hist_k * sgn) > 0),
                             hist_cresce=int(((hist_k - h_prev) * sgn) > 0), incl=int(round(inc)),
                             incl_alin=int((inc * sgn) > 0),
                             vwap_d=("" if nan_(vd) else int(round(vd))), vwap_s=("" if nan_(vs) else int(round(vs))),
                             vwap_d_alin=("" if nan_(vd) else int(((Lv - vd) * sgn) > 0)),
                             vwap_d_dist=("" if nan_(vd) else int(round(Lv - vd))),
                             vwap_s_alin=("" if nan_(vs) else int(((Lv - vs) * sgn) > 0)),
                             prox60=prox60, prox115=prox115, ctx42=ctx["R42"], ctx98=ctx["R98"],
                             scalp4=sc, scalpD=sc_d)
                for y in NOMES:
                    linha["rel_" + y] = rel[y]
                for (s_, t_), r_ in resA.items():
                    linha[f"a_S{s_}_T{t_}"] = int(r_)
                for s_ in STOPS:
                    for t_ in ALVOS:
                        linha[f"b_S{s_}_T{t_}"] = int(resB[(s_, t_)]) if resB else ""
                eventos.append(linha)
        print("  eventos", d, sum(1 for e in eventos if e["dia"] == d), flush=True)

    # clusters: toques do mesmo lado em ate 5 minutos sao o mesmo movimento (varias medias encostam juntas).
    # cl_ordem = 1 marca o primeiro toque do movimento, que e a entrada realista (as demais ja estariam posicionadas).
    eventos.sort(key=lambda e: (e["dia"], e["lado"], seg(e["hora"]), abs(e["p0"] - e["nivel"])))
    grupos, cur = [], None
    for e in eventos:
        t = seg(e["hora"])
        if cur and cur["dia"] == e["dia"] and cur["lado"] == e["lado"] and t - cur["t0"] <= 300:
            cur["itens"].append(e)
        else:
            cur = dict(dia=e["dia"], lado=e["lado"], t0=t, itens=[e])
            grupos.append(cur)
    for g in grupos:
        for ordem, e in enumerate(g["itens"], 1):
            e["cluster"] = f"{g['dia']}_{g['lado']}_{hms(g['t0'])}"
            e["cluster_n"] = len(g["itens"])
            e["cl_ordem"] = ordem
    os.makedirs(args.saida, exist_ok=True)
    pref = f"{dias[0]}_23R"
    cols = list(eventos[0].keys())
    with open(os.path.join(args.saida, f"toques_{pref}.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(cols)
        for e in eventos:
            w.writerow([num(e[c]) if isinstance(e[c], float) else e[c] for c in cols])
    with open(os.path.join(args.saida, f"rejeicao_{pref}.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["dia", "hora", "media", "nivel", "tipo", "prox_dir", "fecha_alem", "idx"])
        w.writerows(rejeicoes)
    with open(os.path.join(args.saida, f"toques_graficos_{pref}.json"), "w", encoding="utf-8") as f:
        json.dump(graficos, f, separators=(",", ":"))
    print("eventos:", len(eventos), "| rejeicoes:", len(rejeicoes))


if __name__ == "__main__":
    main()
