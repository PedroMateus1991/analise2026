"""Reduz export Trade do Profit (mais novo primeiro) para precos cronologicos.

Uso: tac arquivo.csv | python -I reduce.py > saida.csv
Saida: HH:MM:SS;preco;qtd;agressor  (so quando o preco muda)
"""
import sys

last = None
n = 0
out = sys.stdout
for raw in sys.stdin.buffer:
    parts = raw.split(b";")
    if len(parts) < 8:
        continue
    n += 1
    try:
        price = float(parts[4].replace(b",", b"."))
    except ValueError:
        continue
    if price != last:
        last = price
        agr = parts[7].strip().decode("latin-1")
        out.write(f"{parts[2].decode()};{price:.0f};{parts[5].decode()};{agr}\n")
sys.stderr.write(f"linhas lidas: {n}\n")
