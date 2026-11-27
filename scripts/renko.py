"""Reconstrucao de Renko a partir de precos cronologicos (HH:MM:SS;preco;qtd;agressor).

Regra padrao: tijolo de `size` pontos. Dado o ultimo tijolo com minima L e maxima H:
  - continuacao de alta : preco >= H + size  -> novo tijolo (open=H, close=H+size)
  - continuacao de baixa: preco <= L - size  -> novo tijolo (open=L, close=L-size)
  - reversao exige o mesmo movimento a partir da ponta oposta (2 tijolos desde o fechamento).
Direcao inicial indefinida (0): qualquer lado a partir do primeiro preco.
"""
import sys


def build(prices, size=23, state=None):
    bricks = []
    if state is None:
        top = bot = None
        d = 0
    else:
        top, bot, d = state
    for t, p in prices:
        if top is None:
            top = bot = p
            continue
        while True:
            if d == 1:
                up_lvl, dn_lvl = top + size, bot - size
            elif d == -1:
                up_lvl, dn_lvl = top + size, bot - size
            else:
                up_lvl, dn_lvl = top + size, bot - size
            if p >= up_lvl:
                o, c = top, top + size
                bricks.append((t, o, c, 1))
                bot, top, d = o, c, 1
            elif p <= dn_lvl:
                o, c = bot, bot - size
                bricks.append((t, o, c, -1))
                top, bot, d = o, c, -1
            else:
                break
    return bricks, (top, bot, d)


def load(path):
    out = []
    with open(path, encoding="latin-1") as f:
        for line in f:
            a = line.split(";")
            if len(a) < 2:
                continue
            out.append((a[0], float(a[1]), a[3].strip() if len(a) > 3 else ""))
    return out


if __name__ == "__main__":
    rows = load(sys.argv[1])
    for skip in (False, True):
        seq = [(t, p) for t, p, a in rows if not (skip and a.startswith("Leil"))]
        b, _ = build(seq, int(sys.argv[2]))
        n1316 = sum(1 for x in b if x[0] <= "13:16:00")
        n1132 = sum(1 for x in b if x[0] <= "11:32:59")
        print(f"skip_leilao={skip} total={len(b)} ate13:16={n1316} ate11:32:59={n1132}")
