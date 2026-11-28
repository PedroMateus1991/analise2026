"""Medias exponenciais de Renko maiores (42R = 15 min, 98R = 60 min) para o filtro de contexto.

Mesmas regras validadas no 23R: grade ancorada no primeiro preco do dia, gap de abertura
preenchido com tijolos (arredondado para cima), EMAs continuando entre os dias.

Uso como modulo:  htf.Serie(dias, ticks).estado(dia, segundos, preco)
Uso direto (validacao contra a legenda do Profit): python -I htf.py
"""
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import renko  # noqa: E402

DADOS = os.path.join(AQUI, "..", "dados")
PONTOS_POR_TICK = 5
# Deslocamento (pts) da grade em relacao ao primeiro preco do dia, calibrado contra a legenda do
# Profit em 27/11/2026 (erro medio ~40 pts no 98R; no 42R os 3 primeiros pontos ficam a ~20 pts).
GRADE = {42: -35, 98: -165}


def a(n):
    return 2.0 / (n + 1)


def seg(t):
    h, m, s = t.split(":")
    return int(h) * 3600 + int(m) * 60 + int(s)


def tijolos_do_dia(seq, size, prev_close, desloca=0):
    """Tijolos do dia (com o gap de abertura na frente). seq = [(HH:MM:SS, preco)].
    desloca: deslocamento (pts) da grade em relacao ao primeiro preco do dia."""
    seq2 = [(seq[0][0], seq[0][1] + desloca)] + list(seq[1:]) if (seq and desloca) else seq
    br, _ = renko.build(seq2, size, None)
    pre = []
    if prev_close is not None and seq:
        gap = seq[0][1] - prev_close
        step = size if gap > 0 else -size
        cur = prev_close
        for _ in range(-int(-abs(gap) // size)):
            pre.append((seq[0][0], cur, cur + step, 1 if step > 0 else -1))
            cur += step
    return pre + br


class Serie:
    """EMAs 27 e 55 dos fechamentos de tijolos, consultaveis por (dia, segundo)."""

    def __init__(self, dias, ticks, periodos=(27, 55), dados=DADOS, desloca=None):
        if desloca is None:
            desloca = GRADE.get(ticks, 0)
        self.size = ticks * PONTOS_POR_TICK
        self.periodos = periodos
        self.por_dia = {}  # dia -> lista de (seg, ema_curta, ema_longa, fechamento, direcao)
        e = {p: None for p in periodos}
        prev = None
        for d in dias:
            rows = renko.load(os.path.join(dados, f"precos_{d}.csv"))
            seq = [(t, p) for t, p, ag in rows]
            tb = tijolos_do_dia(seq, self.size, prev, desloca)
            lst = []
            for (t, o, c, dr) in tb:
                for p in periodos:
                    e[p] = c if e[p] is None else e[p] + a(p) * (c - e[p])
                lst.append((seg(t), e[periodos[0]], e[periodos[1]], c, dr))
            self.por_dia[d] = lst
            if tb:
                prev = tb[-1][2]
        self.ordem = list(dias)

    def estado(self, dia, s, preco):
        """EMAs vigentes no segundo `s` do `dia`, com o preco ao vivo aplicado.
        Retorna (curta, longa, curta_do_tijolo_anterior, direcao_do_ultimo_tijolo)."""
        lst = self.por_dia[dia]
        lo, hi = 0, len(lst)
        while lo < hi:  # ultimo tijolo com tempo <= s
            mid = (lo + hi) // 2
            if lst[mid][0] <= s:
                lo = mid + 1
            else:
                hi = mid
        k = lo - 1
        if k >= 0:
            _, ec, el, _, dr = lst[k]
            ant = lst[k - 1][1] if k >= 1 else ec
        else:  # antes do primeiro tijolo do dia: usa o ultimo tijolo do dia anterior
            i = self.ordem.index(dia)
            pl = []
            while i > 0 and not pl:
                i -= 1
                pl = self.por_dia[self.ordem[i]]
            if not pl:
                return None
            _, ec, el, _, dr = pl[-1]
            ant = pl[-2][1] if len(pl) >= 2 else ec
        pc, pl_ = self.periodos
        return ec + a(pc) * (preco - ec), el + a(pl_) * (preco - el), ant, dr


if __name__ == "__main__":
    dias = ["2026-11-16", "2026-11-17", "2026-11-18", "2026-11-19", "2026-11-23", "2026-11-24",
            "2026-11-25", "2026-11-26", "2026-11-27"]
    rows27 = renko.load(os.path.join(DADOS, "precos_2026-11-27.csv"))
    seq27 = [(seg(t), p) for t, p, ag in rows27]

    def preco_em(s):
        ult = None
        for t, p in seq27:
            if t > s:
                break
            ult = p
        return ult

    # leituras da legenda do Profit em 27/11 (hora, media 27, media 55)
    leg = {
        42: [("12:56:48", 179942.62, 180827.37), ("13:08:07", 179592.04, 180553.77),
             ("13:11:45", 179597.75, 180556.63), ("13:42:00", 179330.95, 180318.45),
             ("13:43:08", 179236.24, 180235.74)],
        98: [("12:56:48", 181399.88, 179831.59), ("13:08:07", 181155.30, 179764.94),
             ("13:11:45", 181161.36, 179767.14), ("13:43:08", 180917.98, 179694.81)],
    }
    for ticks, pontos in leg.items():
        for ini in (dias, dias[3:]):  # com 9 dias e com 6 dias de historico
            ser = Serie(ini, ticks)
            erros = []
            for hora, l27, l55 in pontos:
                s = seg(hora)
                r = ser.estado("2026-11-27", s, preco_em(s))
                erros.append((r[0] - l27, r[1] - l55))
            m27 = sum(abs(x) for x, _ in erros) / len(erros)
            m55 = sum(abs(y) for _, y in erros) / len(erros)
            det = " ".join(f"({x:+.0f},{y:+.0f})" for x, y in erros)
            print(f"{ticks}R ({ticks*5} pts) historico={len(ini)} dias: erro medio 27={m27:.0f} 55={m55:.0f} pts | {det}")
