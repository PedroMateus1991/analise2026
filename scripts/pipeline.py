"""Pipeline: Renko 23R (115 pts) -> EMAs/MACD -> sinais do ___scalp4_Pedro_2026_.

Valores de EMA e MACD sao calculados sobre os fechamentos dos tijolos.
"""
import sys

sys.path.insert(0, ".")
import renko  # noqa: E402

DADOS = "C:/Users/Pedro Reis/Documents/01-Projetos e Sistemas/07-Analise Tela/dados"
DIAS = ["2026-11-19", "2026-11-23", "2026-11-24", "2026-11-25", "2026-11-26", "2026-11-27"]
SIZE = 115


def ema_step(prev, x, n):
    a = 2.0 / (n + 1)
    return x if prev is None else prev + a * (x - prev)


class Indic:
    """Estado incremental das EMAs e do MACD(89,21,42)."""

    def __init__(self):
        self.e = {n: None for n in (9, 17, 25, 29, 42, 55)}
        self.l = None  # EMA longa 89
        self.c = None  # EMA curta 21
        self.s = None  # sinal 42

    def step(self, close, commit=True):
        e = {n: ema_step(v, close, n) for n, v in self.e.items()}
        l = ema_step(self.l, close, 89)
        c = ema_step(self.c, close, 21)
        macd = c - l
        s = ema_step(self.s, macd, 42)
        hist = macd - s
        if commit:
            self.e, self.l, self.c, self.s = e, l, c, s
        return e, hist


def run(carry, dias=DIAS, size=SIZE, with_prices=False):
    """Retorna lista de tijolos com indicadores. carry=True continua o Renko
    entre os dias; False recomeca a cada dia (EMAs continuam)."""
    ind = Indic()
    state = None
    out = []
    prices_by_day = {}
    for d in dias:
        rows = renko.load(f"{DADOS}/precos_{d}.csv")
        seq = [(t, p) for t, p, a in rows]
        if with_prices:
            prices_by_day[d] = seq
        if not carry:
            state = None
        bricks, state = renko.build(seq, size, state)
        for (t, o, c, dr) in bricks:
            e, hist = ind.step(c)
            out.append(dict(dia=d, t=t, o=o, c=c, dir=dr, e=e, hist=hist))
    return out, ind, prices_by_day


def sinais(bricks, uso_filtro=1, resist=-60, suporte=60):
    """Aplica a logica do codigo-fonte do indicador a cada tijolo."""
    res = []
    for b in bricks:
        e, o, c, h = b["e"], b["o"], b["c"], b["hist"]
        alta, baixa = c > o, c < o
        acima = o > e[17] or c > e[25] or c > e[29] or c > e[42] or c > e[55]
        abaixo = o < e[17] or c < e[25] or c < e[29] or c < e[42] or c < e[55]
        cond_v = h < 0 and h < resist
        cond_c = h > 0 and h > suporte
        f_v = o <= e[55]
        f_c = o >= e[55]
        if uso_filtro == 1:
            m_v, m_c = e[25] < e[29], e[25] > e[29]
        else:
            m_v = m_c = True
        venda = alta and acima and cond_v and f_v and m_v
        compra = baixa and abaixo and cond_c and f_c and m_c
        res.append("V" if venda else ("C" if compra else ""))
    return res


if __name__ == "__main__":
    # Validacao contra a legenda do Profit (13:08:07 e 13:11:45 de 27/11)
    alvos = [
        ("13:08:07", dict(e25=178910.59, e9=178443.47, e55=179401.34, e29=178992.28, hist=-227.36)),
        ("13:11:45", dict(e25=178870.16, e9=178430.17, e55=179365.13, e29=178951.84, hist=-223.61)),
    ]
    for carry in (True, False):
        bricks, ind, pbd = run(carry, with_prices=True)
        print(f"=== carry={carry}  tijolos totais={len(bricks)}  hoje={sum(1 for b in bricks if b['dia']=='2026-11-27')}")
        hoje = pbd["2026-11-27"]
        for hora, ref in alvos:
            ate = [b for b in bricks if b["dia"] == "2026-11-27" and b["t"] <= hora]
            # estado do indicador ate o ultimo tijolo concluido
            ind2 = Indic()
            for b in bricks:
                if b["dia"] == "2026-11-27" and b["t"] > hora:
                    break
                ind2.step(b["c"])
            preco = [p for t, p in hoje if t <= hora][-1]
            e, h = ind2.step(preco, commit=False)
            print(f"  {hora} preco={preco:.0f} ultimo tijolo={ate[-1]['t']} close={ate[-1]['c']:.0f}")
            print(f"    calc live : e9={e[9]:.2f} e25={e[25]:.2f} e29={e[29]:.2f} e55={e[55]:.2f} hist={h:.2f}")
            e0 = ind2.e
            print(f"    calc tijolo: e9={e0[9]:.2f} e25={e0[25]:.2f} e29={e0[29]:.2f} e55={e0[55]:.2f}")
            print(f"    legenda   : e9={ref['e9']:.2f} e25={ref['e25']:.2f} e29={ref['e29']:.2f} e55={ref['e55']:.2f} hist={ref['hist']:.2f}")
