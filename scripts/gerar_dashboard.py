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

with open(os.path.join(AQUI, "modelo_dashboard.tpl"), encoding="utf-8") as f:
    html = f.read()

blob = json.dumps(dados, ensure_ascii=False).replace("</", "<\\/")
html = html.replace("/*__DADOS__*/", blob)

# retorno a media: toques (CSV), rejeicao (CSV) e graficos (JSON) de cada semana + indice das capturas do Profit
toques = {}
for caminho in sorted(glob.glob(os.path.join(RAIZ, "semanas", "toques_2*_23R.csv"))):
    pref = os.path.basename(caminho)[len("toques_"):-len(".csv")]  # ex.: 2026-11-23_23R
    rej = os.path.join(RAIZ, "semanas", f"rejeicao_{pref}.csv")
    graf = os.path.join(RAIZ, "semanas", f"toques_graficos_{pref}.json")
    if not (os.path.exists(rej) and os.path.exists(graf)):
        continue
    with open(caminho, encoding="utf-8") as f:
        csv_t = f.read()
    with open(rej, encoding="utf-8") as f:
        csv_r = f.read()
    with open(graf, encoding="utf-8") as f:
        graficos = json.load(f)
    toques[pref.replace("_", " · ")] = {"csv": csv_t, "rej": csv_r, "graf": graficos}
html = html.replace("/*__TOQUES__*/", json.dumps(toques, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/"))
jan = os.path.join(RAIZ, "imagens", "prints", "janelas.json")
janelas = []
if os.path.exists(jan):
    with open(jan, encoding="utf-8") as f:
        janelas = json.load(f)
html = html.replace("/*__JANELAS__*/", json.dumps(janelas, ensure_ascii=False).replace("</", "<\\/"))
mar = os.path.join(RAIZ, "imagens", "prints", "toques", "trades_marcados.json")
marcados = {}
if os.path.exists(mar):
    with open(mar, encoding="utf-8") as f:
        marcados = json.load(f)
html = html.replace("/*__MARCADOS__*/", json.dumps(marcados, ensure_ascii=False).replace("</", "<" + chr(92) + "/"))
print(f"  toques: {len(toques)} semana(s) | capturas indexadas: {len(janelas)}")
saida = os.path.join(RAIZ, "dashboard.html")
with open(saida, "w", encoding="utf-8") as f:
    f.write(html)
print(f"{saida}  ({os.path.getsize(saida)/1024:.0f} KB, {len(dados)} semana(s): {', '.join(dados)})")
