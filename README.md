# analise2026

Análise semanal do padrão `___scalp4_Pedro_2026_` no WINFUT (Renko), com dashboard.

## Estrutura

| Pasta/arquivo | Conteúdo |
|---|---|
| `semanas/semana_<1º dia>_<N>R.csv` | CSV consolidado de cada semana (um tijolo por linha, com e sem sinal). É o que o dashboard lê. |
| `dados/precos_AAAA-MM-DD.csv` | Preços do dia reduzidos (só mudanças de preço, ordem cronológica). |
| `scripts/` | `reduce.py`, `renko.py`, `gerar_semana.py`, `gerar_dashboard.py`, `dashboard_template.html`, `analise_medias.py` (estudo das médias e filtros) e `avaliar_operacional.py` (mede os candidatos de operacional). |
| `imagens/` | Print do Profit anotado mostrando como cada sinal é analisado. |
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
- Sinal calculado pela lógica literal do indicador (`abertura` = abertura do tijolo). Conferido com as setas do Profit na segunda 23/11 (candles 24, 28 e 29).
- A grade do Renko é ancorada no primeiro preço do dia; o gap de abertura é preenchido com tijolos (arredondado para cima) e eles alimentam as médias, mas não são operáveis.

## Operacional proposto (semana 23–27/11/2026, 23R)

Só o 1º e o 2º sinal do episódio, fechamento atravessando 2 ou 3 médias, depois das 10:00, stop 230 / gain 575: 25 trades, 48% de acerto, +167 pts por trade, positivo nos 5 dias. Foi escolhido olhando a mesma semana, então precisa ser confirmado em semanas novas (`python -I scripts/avaliar_operacional.py <csv>` mede os mesmos candidatos sem reotimizar).

## Limitações

- O histograma do MACD calculado difere cerca de 47 pts do Profit.
- O viés do gráfico 98R (60 min) não está incluído.
- Resultados de poucas semanas não são conclusivos.
