# analise2026

Análise semanal do padrão `___scalp4_Pedro_2026_` no WINFUT (Renko), com dashboard.

## Estrutura

| Pasta/arquivo | Conteúdo |
|---|---|
| `semanas/semana_<1º dia>_<N>R.csv` | CSV consolidado de cada semana (um tijolo por linha, com e sem sinal). É o que o dashboard lê. |
| `dados/precos_AAAA-MM-DD.csv` | Preços do dia reduzidos (só mudanças de preço, ordem cronológica). |
| `scripts/` | `reduce.py`, `renko.py`, `pipeline.py`, `analise.py`, `gerar_semana.py`, `gerar_dashboard.py`, `dashboard_template.html`. |
| `dashboard.html` | Dashboard. Abre no navegador, carrega as semanas deste repositório e aceita arrastar um CSV. |

## Fluxo para uma nova semana

1. No Profit: Arquivo → Exportar Dados Históricos → Intervalo "Trade", um dia por vez (mais o dia útil anterior, só para aquecer os indicadores).
2. Reduzir: `tac <bruto.csv> | python -I scripts/reduce.py > dados/precos_AAAA-MM-DD.csv` e apagar o bruto.
3. Gerar a semana: `python -I scripts/gerar_semana.py --ticks 23 --aquecimento <dia> --dias <d1,d2,...>`.
4. Gerar o dashboard: `python -I scripts/gerar_dashboard.py`.
5. Subir para este repositório (`git add . && git commit && git push`).

## Regras usadas

- Renko 23R = 23 ticks × 5 pts = 115 pts por tijolo. O Renko recomeça a cada dia.
- Stop de 2 tijolos (230 pts) e gain de 5 tijolos (575 pts) para o 23R; janela 09:00–14:00.
- Sinal calculado pela lógica do indicador (`abertura` tratada como `Close`).

## Limitações

- O histograma do MACD calculado difere cerca de 47 pts do Profit.
- O viés do gráfico 98R (60 min) não está incluído.
- Resultados de poucas semanas não são conclusivos.
