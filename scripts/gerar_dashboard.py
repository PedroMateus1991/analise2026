"""Embute todos os semanas/semana_*.csv no dashboard e grava ../dashboard.html.

Uso: python -I gerar_dashboard.py
"""
import glob
import json
import os

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.normpath(os.path.join(AQUI, ".."))

dados = {}
for caminho in sorted(glob.glob(os.path.join(RAIZ, "semanas", "semana_*.csv"))):
    with open(caminho, encoding="utf-8") as f:
        txt = f.read()
    cab = txt.split("\n", 2)
    prim = cab[1].split(";") if len(cab) > 1 else []
    nome = f"{prim[0]} · {prim[2]}R" if len(prim) > 2 else os.path.basename(caminho)
    dados[nome] = txt

with open(os.path.join(AQUI, "dashboard_template.html"), encoding="utf-8") as f:
    html = f.read()

blob = json.dumps(dados, ensure_ascii=False).replace("</", "<\\/")
html = html.replace("/*__DADOS__*/", blob)
saida = os.path.join(RAIZ, "dashboard.html")
with open(saida, "w", encoding="utf-8") as f:
    f.write(html)
print(f"{saida}  ({os.path.getsize(saida)/1024:.0f} KB, {len(dados)} semana(s): {', '.join(dados)})")
