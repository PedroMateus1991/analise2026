<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Dashboard scalp4 · Renko</title>
<style>
:root{
  --bg:#f5f6f8; --card:#ffffff; --ink:#1b1f27; --mut:#667085; --line:#e3e6ec;
  --pos:#157f4a; --neg:#c23a2f; --posbg:#e4f4ea; --negbg:#fbe7e4; --acc:#2563eb; --warn:#b7791f; --warnbg:#fdf3dc;
  --heat0:#f1f3f7;
  color-scheme:light;
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    --bg:#0f1319; --card:#171c25; --ink:#e8ebf1; --mut:#97a1b3; --line:#2a3140;
    --pos:#4cc38a; --neg:#f0766b; --posbg:#14352a; --negbg:#3d1d1a; --acc:#6ea0ff; --warn:#e5b45a; --warnbg:#3a2f14;
    --heat0:#222a37; color-scheme:dark;
  }
}
:root[data-theme="dark"]{
  --bg:#0f1319; --card:#171c25; --ink:#e8ebf1; --mut:#97a1b3; --line:#2a3140;
  --pos:#4cc38a; --neg:#f0766b; --posbg:#14352a; --negbg:#3d1d1a; --acc:#6ea0ff; --warn:#e5b45a; --warnbg:#3a2f14;
  --heat0:#222a37; color-scheme:dark;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.45 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
.wrap{max-width:1240px;margin:0 auto;padding:18px 16px 60px}
h1{font-size:20px;margin:0 0 2px}
h2{font-size:15px;margin:0 0 4px}
.sub{color:var(--mut);font-size:13px}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 16px;margin-top:14px}
.row{display:flex;flex-wrap:wrap;gap:12px;align-items:flex-end}
label{display:flex;flex-direction:column;font-size:12px;color:var(--mut);gap:3px}
select,input[type=number],input[type=search]{background:var(--card);color:var(--ink);border:1px solid var(--line);border-radius:8px;padding:6px 8px;font:inherit;min-width:84px}
button{background:var(--card);color:var(--ink);border:1px solid var(--line);border-radius:8px;padding:6px 10px;font:inherit;cursor:pointer}
button.on{background:var(--acc);color:#fff;border-color:var(--acc)}
.chips{display:flex;gap:6px;flex-wrap:wrap}
.verdict{display:flex;gap:16px;align-items:flex-start;flex-wrap:wrap}
.vbadge{font-weight:700;font-size:18px;padding:10px 14px;border-radius:10px;min-width:230px}
.vbadge.pos{background:var(--posbg);color:var(--pos)} .vbadge.neg{background:var(--negbg);color:var(--neg)} .vbadge.mid{background:var(--warnbg);color:var(--warn)}
.vtext{flex:1;min-width:280px}
.vtext ul{margin:6px 0 0 18px;padding:0}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin-top:12px}
.kpi{border:1px solid var(--line);border-radius:10px;padding:10px 12px}
.kpi .v{font-size:20px;font-weight:700;font-variant-numeric:tabular-nums}
.kpi .l{font-size:12px;color:var(--mut)}
.kpi .s{font-size:11.5px;color:var(--mut);margin-top:2px}
.pos{color:var(--pos)} .neg{color:var(--neg)}
.grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:14px}
table{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums}
th,td{padding:5px 8px;text-align:right;border-bottom:1px solid var(--line);white-space:nowrap}
th:first-child,td:first-child{text-align:left}
th{font-size:12px;color:var(--mut);font-weight:600;cursor:default}
th.s{cursor:pointer}
.scroll{overflow-x:auto}
.bar{display:inline-block;height:9px;border-radius:3px;vertical-align:middle}
.small{opacity:.55}
.note{background:var(--warnbg);color:var(--warn);border-radius:8px;padding:8px 10px;font-size:12.5px;margin-top:8px}
.heat td{text-align:center;padding:0}
.heat .cell{padding:7px 4px;cursor:pointer;font-size:12px;line-height:1.25;border:2px solid transparent}
.heat .cell b{display:block;font-size:13px}
.heat .cell.sel{border-color:var(--ink)}
.heat .cell.best{outline:2px dashed var(--acc);outline-offset:-3px}
.legend{font-size:12px;color:var(--mut);margin-top:6px}
svg text{fill:var(--mut);font-size:11px}
.tag-alvo{color:var(--pos);font-weight:600} .tag-stop{color:var(--neg);font-weight:600} .tag-mm{color:var(--warn);font-weight:600}
details summary{cursor:pointer;font-weight:600}
details p,details li{color:var(--mut)}
.drop{border:2px dashed var(--line);border-radius:10px;padding:10px;text-align:center;color:var(--mut)}
.drop.over{border-color:var(--acc);color:var(--acc)}
@media (max-width:560px){.vbadge{min-width:100%}}
</style>
</head>
<body>
<div class="wrap">
  <div class="row" style="justify-content:space-between;align-items:flex-start">
    <div>
      <h1>Dashboard scalp4 · Renko</h1>
      <div class="sub" id="subtitulo"></div>
    </div>
    <div class="row">
      <label>Semana<select id="selSemana"></select></label>
      <label>Tema<select id="selTema"><option value="auto">Automático</option><option value="light">Claro</option><option value="dark">Escuro</option></select></label>
    </div>
  </div>

  <div class="row" style="margin:6px 0 2px">
    <button id="abaScalp" class="on">Sinais do scalp4</button>
    <button id="abaToques">Retorno à média (toques)</button>
  </div>

  <div id="viewScalp">
  <div class="card">
    <div class="row">
      <label>Stop (tijolos)<select id="selS"></select></label>
      <label>Gain (tijolos)<select id="selT"></select></label>
      <label>Valor do ponto (R$/contrato)<input type="number" id="inRs" value="0.2" step="0.05" min="0"></label>
      <label>Contratos<input type="number" id="inCtr" value="1" step="1" min="1"></label>
      <label>Custo por trade (R$)<input type="number" id="inCusto" value="0" step="0.5" min="0"></label>
      <label>Filtro de entrada
        <select id="selFiltro">
          <option value="nenhum">Sem filtro (todos os sinais)</option>
          <option value="A">A · só 1º e 2º sinal do episódio</option>
          <option value="B">B · atravessa 2 ou 3 médias</option>
          <option value="C">C · A + B</option>
          <option value="D">D · C + depois das 10h (operacional proposto)</option>
          <option value="E">E · C + |MACD| entre 150 e 300</option>
          <option value="F">F · só |MACD| entre 150 e 300</option>
          <option value="G">G · D + 42R a favor (preço abaixo das 2 médias na venda, acima na compra)</option>
          <option value="H">H · só 42R a favor</option>
          <option value="I">I · 42R a favor ou entre as médias (sem ir contra)</option>
        </select>
      </label>
      <label>Lado
        <span class="chips" id="chLado"><button data-v="VC" class="on">Compra+Venda</button><button data-v="V">Só venda ▼</button><button data-v="C">Só compra ▲</button></span>
      </label>
    </div>
    <div class="row" style="margin-top:10px">
      <label>Dias
        <span class="chips" id="chDias"></span>
      </label>
      <label>Horário
        <span class="chips" id="chHora"><button data-v="9-14" class="on">9h–14h</button><button data-v="9-10">9h–10h</button><button data-v="10-12">10h–12h</button><button data-v="12-14">12h–14h</button></span>
      </label>
    </div>
    <div class="sub" id="payoffTxt" style="margin-top:8px"></div>
  </div>

  <div class="card" id="cardVeredito"></div>

  <div class="card" id="cardOper">
    <h2>Operacional proposto (D)</h2>
    <div class="sub">Regra montada olhando a semana 23–27/11 (WINZ26, Renko 23R). Foi escolhida depois de ver os dados, então precisa ser confirmada em semanas novas: este dashboard recalcula tudo com o mesmo filtro quando você carregar a próxima.</div>
    <ul style="margin:8px 0 8px 18px;padding:0">
      <li><b>Só o 1º e o 2º sinal</b> do episódio (tijolos de sinal seguidos no mesmo lado). Do 3º em diante o desempenho foi péssimo.</li>
      <li><b>O fechamento do tijolo atravessa 2 ou 3 médias</b> das 5 (17, 25, 29, 42, 55). Atravessar só 1 ou 4–5 perdeu.</li>
      <li><b>Somente depois das 10:00</b> (a primeira hora teve 14% de acerto).</li>
      <li>Stop de 2 tijolos (230 pts) e gain de 5 tijolos (575 pts), como você opera.</li>
      <li><b>Contexto do 42R (15 min, médias azuis 27 e 55) — versão G:</b> preferir quando o preço está do lado a favor das duas médias (abaixo na venda, acima na compra). Entre as duas médias foi o pior caso da semana. Poucos trades: confirme em semanas novas.</li>
    </ul>
    <div class="row"><button id="btnOper" class="on">Aplicar operacional D (stop 2 / gain 5)</button>
      <button id="btnOperG" class="on">Aplicar D + 42R a favor (G)</button>
      <span class="sub" id="operResumo"></span></div>
    <div style="margin-top:10px"><img id="imgComo" alt="Print do Profit anotado mostrando como cada sinal é analisado" style="max-width:100%;border-radius:8px;border:1px solid var(--line)" src="https://raw.githubusercontent.com/PedroMateus1991/analise2026/main/imagens/como_analiso_2026-11-23.png" onerror="this.style.display='none'"></div>
  </div>

  <div class="grid2">
    <div class="card" style="margin-top:14px">
      <h2>Curva de resultado (pontos acumulados)</h2>
      <div class="sub">Cada trade em ordem cronológica. A linha tracejada é o que a base (tijolos sem sinal) teria feito com a mesma quantidade de trades.</div>
      <div id="chartEquity"></div>
    </div>
    <div class="card" style="margin-top:14px">
      <h2>Qual o melhor payoff? (stop × gain)</h2>
      <div class="sub">Expectativa por trade em pontos. Clique numa célula para usar aquele payoff.
        <select id="selConj" style="margin-left:6px"><option value="sinais">Sinais</option><option value="base">Base (sem sinal)</option><option value="dif">Sinais − Base</option></select></div>
      <div class="scroll"><table class="heat" id="heat"></table></div>
      <div class="legend" id="heatLeg"></div>
    </div>
  </div>

  <div class="card">
    <h2>Quando entrar? Resultado por situação</h2>
    <div class="sub">Mesmo payoff escolhido acima. Linhas esmaecidas têm menos de 10 trades (não confie).</div>
    <div class="grid2" id="breakdowns" style="margin-top:8px"></div>
  </div>

  <div class="card">
    <h2>Quanto o preço anda a favor e contra?</h2>
    <div class="sub">A partir do fechamento do tijolo do sinal, em pontos. Ajuda a escolher o stop e o gain.</div>
    <div class="grid2" style="margin-top:8px">
      <div class="scroll"><table id="tabExc"></table></div>
      <div class="scroll"><table id="tabPerc"></table></div>
    </div>
  </div>

  <div class="card">
    <h2>Todos os sinais</h2>
    <div class="row"><label>Filtrar<input type="search" id="inBusca" placeholder="dia, hora, lado…"></label></div>
    <div class="scroll" style="max-height:460px;overflow-y:auto;margin-top:8px"><table id="tabSinais"></table></div>
  </div>

  <div class="card">
    <h2>Semanas no GitHub</h2>
    <div class="sub">Busca todos os <code>semanas/semana_*.csv</code> do repositório e atualiza o dashboard. Se o repositório for privado, cole um token de leitura (fica só neste navegador).</div>
    <div class="row" style="margin-top:8px">
      <label>Repositório<input type="search" id="ghRepo" value="PedroMateus1991/analise2026" style="min-width:260px"></label>
      <label>Token (opcional se público)<input type="password" id="ghToken" placeholder="github_pat_…" autocomplete="off" style="min-width:260px"></label>
      <label style="flex-direction:row;align-items:center;gap:6px"><input type="checkbox" id="ghLembrar"> lembrar neste navegador</label>
      <button id="ghBtn">Atualizar do GitHub</button>
    </div>
    <div class="sub" id="ghStatus" style="margin-top:6px"></div>
    <details style="margin-top:6px"><summary>Como criar o token (só leitura)</summary>
      <ul><li>GitHub → Settings → Developer settings → Personal access tokens → <b>Fine-grained tokens</b> → Generate new token.</li>
      <li>Repository access: <b>Only select repositories</b> → analise2026.</li>
      <li>Permissions → Repository permissions → <b>Contents: Read-only</b>. Gere e cole acima.</li>
      <li>O token nunca vai para outro lugar além de api.github.com.</li></ul></details>
  </div>

  <div class="card">
    <details>
      <summary>Capturas do Profit anotadas (23 a 27/11) — setas vistas × sinais calculados</summary>
      <p class="sub">Cada imagem é uma janela do gráfico 23R no seu Profit, com as setas encontradas circuladas e a lista dos sinais calculados no mesmo trecho. Parte das setas pode ficar abaixo da área visível do gráfico, então a contagem do print costuma ser menor ou igual à calculada. Carregam do GitHub (precisa de internet).</p>
      <div id="galeria" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:10px"></div>
    </details>
  </div>

  <div class="card">
    <h2>Carregar outra semana</h2>
    <div class="drop" id="drop">Arraste aqui um ou mais arquivos <b>semana_*.csv</b> ou <label style="display:inline;color:var(--acc);cursor:pointer">escolha no computador<input type="file" id="inFile" accept=".csv" multiple hidden></label></div>
  </div>

  <div class="card">
    <details>
      <summary>Como ler este dashboard</summary>
      <ul>
        <li><b>Sinal</b>: tijolo em que o indicador <code>___scalp4_Pedro_2026_</code> desenhou ▼ (venda) ou ▲ (compra). A entrada é o fechamento desse tijolo.</li>
        <li><b>Stop/gain em tijolos</b>: 23R = 115 pts por tijolo, então stop de 2 tijolos = 230 pts e gain de 5 tijolos = 575 pts. Em R$ (WIN, R$ 0,20 por ponto): stop R$ 46 e gain R$ 115 por contrato.</li>
        <li><b>Taxa de alvo</b>: % dos trades que bateram o gain antes do stop. Se nenhum dos dois foi atingido até 14h, o trade é encerrado a mercado (“mm”).</li>
        <li><b>Taxa de equilíbrio</b>: taxa de alvo mínima para não perder dinheiro = stop ÷ (stop + gain). Com 230/575 é 28,6%.</li>
        <li><b>Expectativa</b>: resultado médio por trade. Só vale a pena se for positiva depois de custos e se o intervalo de confiança da taxa de alvo ficar acima do equilíbrio.</li>
        <li><b>Base</b>: todos os tijolos de alta (como venda) e de baixa (como compra) sem sinal, na mesma janela. Se o sinal não bate a base, o padrão não adiciona vantagem.</li>
        <li><b>IC 95%</b>: faixa em que a taxa de alvo verdadeira provavelmente está (Wilson). Com poucos trades ela é larga.</li>
        <li><b>Atenção</b>: a grade de payoffs tem 32 combinações; o “melhor” delas em uma semana costuma ser sorte. Só confie em um payoff que se repita em várias semanas.</li>
        <li>Resultado calculado tick a tick, de 09:00 às 14:00. Os sinais seguem a lógica literal do indicador e foram conferidos com as setas do Profit na segunda 23/11 (candles 24, 28 e 29). O histograma do MACD difere ~47 pts do Profit; sinais com histograma perto de ±60 podem divergir. Em 27/11 o Profit mostrou uma seta a mais (candle 369) que este cálculo não reproduz.</li>
        <li><b>Filtros de entrada</b> (A a F) são candidatos montados depois de olhar os dados da semana: use-os como hipótese e confirme em semanas novas.</li>
      </ul>
    </details>
  </div>
  </div><!-- /viewScalp -->

  <div id="viewToques" hidden>
    <div class="card">
      <h2>Retorno à média: vale entrar no toque ou na virada de box?</h2>
      <div class="sub" id="tqSub"></div>
      <div class="row" style="margin-top:8px">
        <label>Entrada
          <select id="tqEntrada"><option value="a">No toque (ordem limite na média)</option><option value="b">Na virada de box (1º tijolo a favor depois do toque)</option></select></label>
        <label>Média<select id="tqMedia"></select></label>
        <label>Lado<select id="tqLado"><option value="">Compra + venda</option><option value="V">Venda ▼ (toque vindo de baixo)</option><option value="C">Compra ▲ (toque vindo de cima)</option></select></label>
        <label>Horário<select id="tqHora"></select></label>
        <label>Stop (tijolos)<select id="tqS"></select></label>
        <label>Gain (tijolos)<select id="tqT"></select></label>
      </div>
      <div class="row" style="margin-top:10px;gap:14px">
        <label style="flex-direction:row;align-items:center;gap:6px"><input type="checkbox" id="tqPrim" checked> só o 1º toque de cada movimento</label>
        <label style="flex-direction:row;align-items:center;gap:6px"><input type="checkbox" id="tqMacd"> MACD alinhado</label>
        <label style="flex-direction:row;align-items:center;gap:6px"><input type="checkbox" id="tqVwap"> nível a favor da VWAP diária</label>
        <label style="flex-direction:row;align-items:center;gap:6px"><input type="checkbox" id="tqC42"> preço a favor das médias do 42R</label>
        <label style="flex-direction:row;align-items:center;gap:6px"><input type="checkbox" id="tqIncl"> média inclinada a favor</label>
        <label style="flex-direction:row;align-items:center;gap:6px"><input type="checkbox" id="tqProx"> 2+ médias juntas (≤ 60 pts)</label>
      </div>
      <div class="sub" id="tqPayoff" style="margin-top:8px"></div>
    </div>

    <div class="card" id="tqVeredito"></div>

    <div class="card">
      <h2>Ranking: qual média segura mais o preço?</h2>
      <div class="sub">Usa os filtros acima (menos a média). “Rejeição” = quando a média cai na máxima–mínima de um tijolo só no pavio, % de vezes em que o próximo tijolo não fecha além dela. Clique numa linha para filtrar a média.</div>
      <div class="scroll"><table id="tqRank"></table></div>
    </div>

    <div class="grid2">
      <div class="card" style="margin-top:14px"><h2>Horário (blocos de 30 min)</h2><div class="scroll"><table id="tqHorarios"></table></div></div>
      <div class="card" style="margin-top:14px"><h2>Quem está por baixo de quem</h2>
        <div class="sub">Escolha uma média acima. Venda tende a funcionar com a média tocada <b>abaixo</b> da outra; compra com ela <b>acima</b>.</div>
        <div class="scroll"><table id="tqRel"></table></div></div>
    </div>

    <div class="card"><h2>Alinhamentos e confluências</h2><div class="grid2" id="tqGrupos" style="margin-top:8px"></div></div>

    <div class="card"><h2>Trades (clique em “gráfico” para conferir)</h2>
      <div class="scroll" style="max-height:460px;overflow-y:auto"><table id="tqTrades"></table></div></div>

    <div id="tqModal" hidden style="position:fixed;inset:0;background:rgba(0,0,0,.55);z-index:50;overflow:auto;padding:16px">
      <div class="card" style="max-width:1000px;margin:20px auto">
        <div class="row" style="justify-content:space-between"><h2 id="tqModalTit" style="margin:0"></h2><button id="tqFechar">Fechar ✕</button></div>
        <div id="tqGraf"></div>
        <div class="sub" id="tqGrafNota"></div>
        <div id="tqPrint" style="margin-top:10px"></div>
      </div>
    </div>
  </div><!-- /viewToques -->
</div>

<script id="toquesEmbutidos" type="application/json">/*__TOQUES__*/</script>
<script id="janelasEmbutidas" type="application/json">/*__JANELAS__*/</script>
<script id="dadosEmbutidos" type="application/json">/*__DADOS__*/</script>
<script>
"use strict";
const TEXT = new Set(["semana","ativo","dia","hora","lado","sinal"]);
const STOPS=[1,2,3,4], ALVOS=[1,2,3,4,5,6,8,10];
const fmt0=n=>isFinite(n)?Math.round(n).toLocaleString("pt-BR"):"—";
const fmt1=n=>isFinite(n)?n.toLocaleString("pt-BR",{minimumFractionDigits:1,maximumFractionDigits:1}):"—";
const fmtR=n=>isFinite(n)?n.toLocaleString("pt-BR",{style:"currency",currency:"BRL"}):"—";
const pct=n=>isFinite(n)?(n*100).toLocaleString("pt-BR",{minimumFractionDigits:1,maximumFractionDigits:1})+"%":"—";
const sgn=n=>n>0?"pos":(n<0?"neg":"");
const ctxTxt=v=>!isFinite(v)?"—":(v===1?"a favor":(v===0?"entre":"contra"));
const $=id=>document.getElementById(id);
const DOW=["dom","seg","ter","qua","qui","sex","sáb"];

function parseCSV(text){
  const lines=text.replace(/^﻿/,"").trim().split(/\r?\n/);
  const head=lines[0].split(";");
  const out=[];
  for(let i=1;i<lines.length;i++){
    const p=lines[i].split(";"); const o={};
    for(let j=0;j<head.length;j++){
      const k=head[j], v=p[j]===undefined?"":p[j];
      o[k]=TEXT.has(k)?v:(v===""?NaN:parseFloat(v.replace(",",".")));
    }
    out.push(o);
  }
  return out;
}

// ---------------------------------------------------------------- estado
const FILTROS={
  nenhum:r=>true,
  A:r=>r.seq<=2,
  B:r=>r.n_emas>=2&&r.n_emas<=3,
  C:r=>r.seq<=2&&r.n_emas>=2&&r.n_emas<=3,
  D:r=>r.seq<=2&&r.n_emas>=2&&r.n_emas<=3&&parseInt(r.hora.slice(0,2),10)>=10,
  E:r=>r.seq<=2&&r.n_emas>=2&&r.n_emas<=3&&Math.abs(r.hist)>=150&&Math.abs(r.hist)<300,
  F:r=>Math.abs(r.hist)>=150&&Math.abs(r.hist)<300,
  // contexto do Renko de 15 min (42R, medias azuis): +1 = preço do lado a favor das duas medias 27 e 55
  G:r=>r.seq<=2&&r.n_emas>=2&&r.n_emas<=3&&parseInt(r.hora.slice(0,2),10)>=10&&r.alin_pos42===1,
  H:r=>r.alin_pos42===1,
  I:r=>r.alin_pos42>=0,
};
const S0={weeks:{}, semana:null, lado:"VC", dias:null, hora:"9-14", filtro:"nenhum", S:2, T:5, rs:0.2, ctr:1, custo:0, conj:"sinais", busca:"", sort:{k:"dia",d:1}};
const st=S0;

function addWeek(name,rows){
  const key=name;
  st.weeks[key]=rows;
}
function loadEmbedded(){
  try{
    const d=JSON.parse($("dadosEmbutidos").textContent.replace(/^\/\*.*?\*\//,"")||"{}");
    for(const k of Object.keys(d)) addWeek(k,parseCSV(d[k]));
  }catch(e){ /* sem dados embutidos */ }
}

// ---------------------------------------------------------------- filtros
function baseRows(){
  let rows=[];
  if(st.semana==="__todas__"){ for(const k of Object.keys(st.weeks)) rows=rows.concat(st.weeks[k]); }
  else rows=st.weeks[st.semana]||[];
  return rows;
}
function filtered(rows){
  const [h0,h1]=st.hora.split("-").map(Number);
  return rows.filter(r=>{
    if(st.dias && !st.dias.has(r.dia)) return false;
    if(st.lado!=="VC" && r.lado!==st.lado) return false;
    if(!FILTROS[st.filtro](r)) return false;
    const h=parseInt(r.hora.slice(0,2),10);
    return h>=h0 && h<h1;
  });
}
function res(r,S,T){ return r[`r_S${S}_T${T}`]; }
function tag(r,S,T){ const x=res(r,S,T), z=r.tijolo_pts; if(Math.abs(x-T*z)<0.5) return "alvo"; if(Math.abs(x+S*z)<0.5) return "stop"; return "mm"; }
function sortChron(a){ return a.slice().sort((x,y)=> (x.dia+x.hora).localeCompare(y.dia+y.hora)); }

function wilson(w,n,z=1.96){
  if(!n) return [NaN,NaN];
  const p=w/n, d=1+z*z/n, c=p+z*z/(2*n), m=z*Math.sqrt(p*(1-p)/n+z*z/(4*n*n));
  return [(c-m)/d,(c+m)/d];
}
function stats(rows,S,T){
  const n=rows.length;
  if(!n) return {n:0};
  let w=0,l=0,mm=0,sum=0,gp=0,gl=0,cum=0,peak=0,dd=0,streak=0,maxStreak=0;
  const ch=sortChron(rows), series=[];
  for(const r of ch){
    const x=res(r,S,T), t=tag(r,S,T);
    if(t==="alvo")w++; else if(t==="stop")l++; else mm++;
    sum+=x; if(x>0)gp+=x; else gl-=x;
    cum+=x; series.push(cum); if(cum>peak)peak=cum; dd=Math.max(dd,peak-cum);
    if(x<0){streak++; maxStreak=Math.max(maxStreak,streak);} else streak=0;
  }
  const be=S/(S+T), [lo,hi]=wilson(w,n);
  const mins=rows.filter(r=>S===2&&T===5&&isFinite(r.min_padrao)).map(r=>r.min_padrao);
  return {n,w,l,mm,sum,exp:sum/n,pf:gl>0?gp/gl:Infinity,wr:w/n,be,lo,hi,series,dd,maxStreak,
          tmed:mins.length?mins.reduce((a,b)=>a+b,0)/mins.length:NaN, ch};
}
const money=(pts)=>pts*st.rs*st.ctr;
const median=a=>{if(!a.length)return NaN;const s=a.slice().sort((x,y)=>x-y),m=s.length>>1;return s.length%2?s[m]:(s[m-1]+s[m])/2;};
const mean=a=>a.length?a.reduce((x,y)=>x+y,0)/a.length:NaN;
const perc=(a,p)=>{if(!a.length)return NaN;const s=a.slice().sort((x,y)=>x-y);return s[Math.min(s.length-1,Math.floor(p*s.length))];};

// ---------------------------------------------------------------- render
function render(){
  const all=filtered(baseRows());
  const sig=all.filter(r=>r.sinal!==""), base=all.filter(r=>r.sinal==="");
  const S=st.S,T=st.T;
  const a=stats(sig,S,T), b=stats(base,S,T);
  const z=(all[0]||{}).tijolo_pts||115, ticks=(all[0]||{}).renko_ticks||23;
  $("subtitulo").textContent=`${(all[0]||{}).ativo||""} · Renko ${ticks}R (${z} pts por tijolo) · ${sig.length} sinais e ${base.length} tijolos de base`;
  $("payoffTxt").innerHTML=`Payoff: stop <b>${S*z} pts</b> (${fmtR(money(S*z))}) · gain <b>${T*z} pts</b> (${fmtR(money(T*z))}) · equilíbrio <b>${pct(S/(S+T))}</b> de acerto · relação ganho/perda <b>${fmt1(T/S)}:1</b>`;
  renderVeredito(a,b,S,T,z);
  renderEquity(a,b);
  renderHeat(sig,base,z);
  renderBreak(sig,S,T);
  renderExc(sig,base);
  renderTabela(sig,S,T);
}

function renderVeredito(a,b,S,T,z){
  const el=$("cardVeredito");
  if(!a.n){ el.innerHTML="<b>Sem sinais com estes filtros.</b>"; return; }
  const expR=money(a.exp)-st.custo, totR=money(a.sum)-st.custo*a.n;
  let cls,txt;
  if(expR>0 && a.lo>a.be){cls="pos";txt="COMPENSA (com evidência)";}
  else if(expR>0){cls="mid";txt="POSITIVO, MAS NÃO CONCLUSIVO";}
  else if(a.hi<a.be){cls="neg";txt="NÃO COMPENSA";}
  else {cls="neg";txt="NÃO COMPENSOU NESTA AMOSTRA";}
  const posthoc=st.filtro!=="nenhum";
  if(posthoc && cls==="pos"){cls="mid";txt="POSITIVO, MAS O FILTRO FOI ESCOLHIDO DEPOIS DE VER OS DADOS";}
  const edge=b.n?a.exp-b.exp:NaN;
  const pts=[];
  if(posthoc) pts.push("Filtro de entrada ativo: ele foi montado olhando estes mesmos dias, então o resultado tende a estar superestimado. Só vale como regra depois de repetir em semanas novas.");
  pts.push(`Taxa de alvo <b>${pct(a.wr)}</b> (IC 95%: ${pct(a.lo)} a ${pct(a.hi)}) contra equilíbrio de <b>${pct(a.be)}</b>.`);
  pts.push(`Expectativa de <b class="${sgn(expR)}">${fmt1(a.exp)} pts</b> por trade = <b class="${sgn(expR)}">${fmtR(expR)}</b> por trade com ${st.ctr} contrato(s) e custo de ${fmtR(st.custo)}.`);
  if(b.n) pts.push(`A base (tijolos sem sinal) fez <b>${fmt1(b.exp)} pts</b> por trade, então o sinal ${edge>0?"adiciona":"retira"} <b class="${sgn(edge)}">${fmt1(Math.abs(edge))} pts</b> por trade em relação a entrar sem o padrão.`);
  if(a.n<30) pts.push(`<b>Amostra pequena</b> (${a.n} trades): trate como indício, não como regra.`);
  if(!(a.lo>a.be) && expR>0) pts.push("O limite inferior do IC está abaixo do equilíbrio: pode ser sorte.");
  el.innerHTML=`<div class="verdict"><div class="vbadge ${cls}">${txt}</div><div class="vtext"><div><b>Vale entrar quando o padrão aparecer?</b> Considerando stop de ${S*z} pts e gain de ${T*z} pts:</div><ul>${pts.map(x=>`<li>${x}</li>`).join("")}</ul></div></div>
  <div class="kpis">
    ${kpi("Trades",fmt0(a.n),`${a.w} alvos · ${a.l} stops · ${a.mm} a mercado`)}
    ${kpi("Taxa de alvo",pct(a.wr),`equilíbrio ${pct(a.be)}`,a.wr>=a.be?"pos":"neg")}
    ${kpi("Expectativa (pts)",fmt1(a.exp),fmtR(money(a.exp)-st.custo)+" por trade",sgn(expR))}
    ${kpi("Resultado total",fmt0(a.sum)+" pts",fmtR(totR),sgn(totR))}
    ${kpi("Fator de lucro",isFinite(a.pf)?a.pf.toLocaleString("pt-BR",{maximumFractionDigits:2}):"∞","ganhos ÷ perdas",a.pf>=1?"pos":"neg")}
    ${kpi("Maior queda",fmt0(a.dd)+" pts",fmtR(money(a.dd)),"neg")}
    ${kpi("Stops seguidos",String(a.maxStreak),"sequência mais longa")}
    ${kpi("Tempo até resolver",isFinite(a.tmed)?fmt1(a.tmed)+" min":"—",S===2&&T===5?"média, só p/ stop 2 e gain 5":"disponível só para stop 2 / gain 5")}
  </div>`;
}
function kpi(l,v,s,c){return `<div class="kpi"><div class="l">${l}</div><div class="v ${c||""}">${v}</div><div class="s">${s||""}</div></div>`;}

function svgWrap(w,h,inner){return `<svg viewBox="0 0 ${w} ${h}" width="100%" role="img">${inner}</svg>`;}
function renderEquity(a,b){
  const el=$("chartEquity");
  if(!a.n){el.innerHTML="";return;}
  const W=560,H=250,pl=48,pr=10,pt=10,pb=26;
  const ys=a.series.slice(), bl=(b.n?b.exp:0);
  const ref=ys.map((_,i)=>bl*(i+1));
  const all=ys.concat(ref,[0]), mn=Math.min(...all), mx=Math.max(...all);
  const sx=i=>pl+(W-pl-pr)*(ys.length>1?i/(ys.length-1):0.5), sy=v=>pt+(H-pt-pb)*(1-(v-mn)/((mx-mn)||1));
  const path=ys.map((v,i)=>`${i?"L":"M"}${sx(i).toFixed(1)},${sy(v).toFixed(1)}`).join(" ");
  const pr_=ref.map((v,i)=>`${i?"L":"M"}${sx(i).toFixed(1)},${sy(v).toFixed(1)}`).join(" ");
  let grid="", ticks=5;
  for(let i=0;i<=ticks;i++){const v=mn+(mx-mn)*i/ticks;grid+=`<line x1="${pl}" x2="${W-pr}" y1="${sy(v)}" y2="${sy(v)}" stroke="var(--line)"/><text x="${pl-5}" y="${sy(v)+4}" text-anchor="end">${fmt0(v)}</text>`;}
  let seps="", prev=null;
  a.ch.forEach((r,i)=>{ if(prev!==null&&r.dia!==prev){seps+=`<line x1="${sx(i)}" x2="${sx(i)}" y1="${pt}" y2="${H-pb}" stroke="var(--line)" stroke-dasharray="2 3"/>`;}
    if(prev===null||r.dia!==prev){seps+=`<text x="${sx(i)+3}" y="${H-8}">${r.dia.slice(8)}/${r.dia.slice(5,7)}</text>`;} prev=r.dia; });
  const dots=a.ch.map((r,i)=>{const t=tag(r,st.S,st.T);const c=t==="alvo"?"var(--pos)":(t==="stop"?"var(--neg)":"var(--warn)");return `<circle cx="${sx(i)}" cy="${sy(ys[i])}" r="2.6" fill="${c}"><title>${r.dia} ${r.hora} ${r.lado} → ${t} (${fmt0(res(r,st.S,st.T))} pts)</title></circle>`;}).join("");
  el.innerHTML=svgWrap(W,H,`${grid}<line x1="${pl}" x2="${W-pr}" y1="${sy(0)}" y2="${sy(0)}" stroke="var(--mut)"/>${seps}<path d="${pr_}" fill="none" stroke="var(--mut)" stroke-dasharray="5 4" stroke-width="1.5"/><path d="${path}" fill="none" stroke="var(--acc)" stroke-width="2"/>${dots}`)+
   `<div class="legend"><span style="color:var(--pos)">●</span> alvo · <span style="color:var(--neg)">●</span> stop · <span style="color:var(--warn)">●</span> a mercado · linha azul = sinais · tracejada = base</div>`;
}

function color(v,maxAbs){
  if(!isFinite(v)) return "var(--heat0)";
  const k=Math.min(1,Math.abs(v)/(maxAbs||1));
  const c=v>=0?"21,127,74":"194,58,47";
  return `rgba(${c},${(0.12+0.55*k).toFixed(2)})`;
}
function renderHeat(sig,base,z){
  const tbl=$("heat"), conj=st.conj;
  const cells={}; let maxAbs=1, best=null;
  for(const S of STOPS)for(const T of ALVOS){
    const a=stats(sig,S,T), b=stats(base,S,T);
    let v=conj==="sinais"?a.exp:(conj==="base"?b.exp:(a.n&&b.n?a.exp-b.exp:NaN));
    const nn=conj==="base"?b.n:a.n, wr=conj==="base"?b.wr:a.wr;
    cells[`${S}_${T}`]={v,n:nn,wr,be:S/(S+T)};
    if(isFinite(v)) maxAbs=Math.max(maxAbs,Math.abs(v));
    if(isFinite(v)&&nn>=20&&(!best||v>best.v)) best={v,S,T};
  }
  let h=`<tr><th>stop \\ gain</th>${ALVOS.map(T=>`<th style="text-align:center">${T} tij<br>${T*z}</th>`).join("")}</tr>`;
  for(const S of STOPS){
    h+=`<tr><th style="text-align:left">${S} tij · ${S*z}</th>`;
    for(const T of ALVOS){
      const c=cells[`${S}_${T}`], cls=["cell"]; if(S===st.S&&T===st.T)cls.push("sel"); if(best&&best.S===S&&best.T===T)cls.push("best");
      h+=`<td><div class="${cls.join(" ")}" data-s="${S}" data-t="${T}" style="background:${color(c.v,maxAbs)}" title="acerto ${pct(c.wr)} · equilíbrio ${pct(c.be)} · n=${c.n}"><b class="${sgn(c.v)}">${isFinite(c.v)?fmt0(c.v):"—"}</b>${pct(c.wr)}</div></td>`;
    }
    h+="</tr>";
  }
  tbl.innerHTML=h;
  tbl.querySelectorAll(".cell").forEach(el=>el.onclick=()=>{st.S=+el.dataset.s;st.T=+el.dataset.t;$("selS").value=st.S;$("selT").value=st.T;render();});
  $("heatLeg").innerHTML=best?`Borda tracejada: melhor expectativa nesta amostra (≥ 20 trades): stop ${best.S*z} / gain ${best.T*z} = ${fmt1(best.v)} pts por trade. Com 32 combinações, o melhor de uma semana costuma ser sorte. Cada célula: expectativa em pts e taxa de acerto.`:`Cada célula: expectativa em pts e taxa de acerto. Menos de 20 trades: sem destaque.`;
}

function groupBy(rows,fn,order){
  const m=new Map();
  for(const r of rows){const k=fn(r); if(k===null)continue; if(!m.has(k))m.set(k,[]); m.get(k).push(r);}
  const keys=order?order.filter(k=>m.has(k)):[...m.keys()].sort();
  return keys.map(k=>[k,m.get(k)]);
}
function tabGrupo(titulo,grupos,S,T){
  let maxAbs=1; const L=grupos.map(([k,it])=>{const s=stats(it,S,T);maxAbs=Math.max(maxAbs,Math.abs(s.exp));return [k,s];});
  const rows=L.map(([k,s])=>`<tr class="${s.n<10?"small":""}"><td>${k}</td><td>${s.n}</td><td class="${s.wr>=s.be?"pos":"neg"}">${pct(s.wr)}</td><td class="${sgn(s.exp)}">${fmt0(s.exp)}</td><td style="text-align:left"><span class="bar" style="width:${Math.round(60*Math.abs(s.exp)/maxAbs)}px;background:${s.exp>=0?"var(--pos)":"var(--neg)"}"></span></td></tr>`).join("");
  return `<div class="scroll"><h2 style="font-size:13px">${titulo}</h2><table><tr><th></th><th>n</th><th>acerto</th><th>exp. pts</th><th></th></tr>${rows}</table></div>`;
}
function renderBreak(sig,S,T){
  const hb=r=>{const x=Math.abs(r.hist);return x<150?"|hist| < 150":(x<300?"|hist| 150–300":"|hist| ≥ 300");};
  const db=r=>{const x=Math.abs(r.dist_e55);return x<300?"< 300":(x<600?"300–600":(x<1000?"600–1000":"≥ 1000"));};
  const out=[
    tabGrupo("Por dia",groupBy(sig,r=>`${r.dia.slice(8)}/${r.dia.slice(5,7)} ${DOW[new Date(r.dia+"T12:00:00").getDay()]}`),S,T),
    tabGrupo("Por hora",groupBy(sig,r=>r.hora.slice(0,2)+"h"),S,T),
    tabGrupo("Ordem do sinal no episódio",groupBy(sig,r=>r.seq>=3?"3º ou mais":(r.seq===2?"2º sinal":"1º sinal"),["1º sinal","2º sinal","3º ou mais"]),S,T),
    tabGrupo("Força do MACD (histograma)",groupBy(sig,hb,["|hist| < 150","|hist| 150–300","|hist| ≥ 300"]),S,T),
    tabGrupo("Médias cruzadas no fechamento",groupBy(sig,r=>r.n_emas+" de 5"),S,T),
    tabGrupo("Tijolos seguidos na mesma direção",groupBy(sig,r=>r.run===1?"1 (reversão)":(r.run<=3?"2–3":"4 ou mais"),["1 (reversão)","2–3","4 ou mais"]),S,T),
    tabGrupo("Distância do fechamento à média 55",groupBy(sig,db,["< 300","300–600","600–1000","≥ 1000"]),S,T),
    tabGrupo("Lado",groupBy(sig,r=>r.lado==="V"?"Venda ▼":"Compra ▲",["Venda ▼","Compra ▲"]),S,T),
  ];
  // contexto de Renko maior (so aparece se o CSV da semana tiver as colunas)
  if(sig.length && isFinite(sig[0].alin_pos42)){
    const rot=v=>!isFinite(v)?null:(v===1?"a favor":(v===0?"entre as médias":"contra"));
    const ord=["a favor","entre as médias","contra"];
    const ordLado=["Venda · a favor","Venda · entre as médias","Venda · contra","Compra · a favor","Compra · entre as médias","Compra · contra"];
    for(const [n,nome] of [[42,"42R (15 min, azuis)"],[98,"98R (60 min)"]]){
      out.push(tabGrupo(`${nome}: preço × médias 27 e 55`,groupBy(sig,r=>rot(r["alin_pos"+n]),ord),S,T));
      out.push(tabGrupo(`${nome}: lado × posição do preço`,groupBy(sig,r=>{const x=rot(r["alin_pos"+n]);return x?((r.lado==="V"?"Venda":"Compra")+" · "+x):null;},ordLado),S,T));
      out.push(tabGrupo(`${nome}: inclinação da média 27`,groupBy(sig,r=>isFinite(r["alin_incl"+n])?(r["alin_incl"+n]===1?"a favor":"contra"):null,["a favor","contra"]),S,T));
      out.push(tabGrupo(`${nome}: tendência (27 × 55)`,groupBy(sig,r=>isFinite(r["alin_tend"+n])?(r["alin_tend"+n]===1?"a favor":"contra"):null,["a favor","contra"]),S,T));
    }
    out.push(tabGrupo("Qualidade da medida (42R): preço perto de uma média?",groupBy(sig,r=>isFinite(r.incerto42)?(r.incerto42===1?"a menos de 250 pts (incerto)":"longe das médias"):null,["longe das médias","a menos de 250 pts (incerto)"]),S,T));
  }
  $("breakdowns").innerHTML=out.join("");
}

function renderExc(sig,base){
  const H=[["10m","10 min"],["30m","30 min"],["60m","60 min"],["fim","até 14h"]];
  const mk=(rows,k)=>rows.map(r=>r[k]).filter(isFinite);
  let h=`<tr><th>Horizonte</th><th>a favor (sinal)</th><th>contra (sinal)</th><th>a favor (base)</th><th>contra (base)</th></tr>`;
  for(const [k,n] of H){
    h+=`<tr><td>${n}</td><td class="pos">${fmt0(mean(mk(sig,"mfe_"+k)))}</td><td class="neg">${fmt0(mean(mk(sig,"mae_"+k)))}</td><td>${fmt0(mean(mk(base,"mfe_"+k)))}</td><td>${fmt0(mean(mk(base,"mae_"+k)))}</td></tr>`;
  }
  $("tabExc").innerHTML=h+`<tr><td colspan="5" style="text-align:left;color:var(--mut);font-size:12px">Médias em pontos, máximo favorável e máximo adverso desde o fechamento do tijolo.</td></tr>`;
  let p=`<tr><th>Percentil do movimento contra</th><th>30 min</th><th>60 min</th><th>até 14h</th></tr>`;
  for(const q of [0.5,0.75,0.9]) p+=`<tr><td>${Math.round(q*100)}% dos sinais ficaram abaixo de</td>${["30m","60m","fim"].map(k=>`<td>${fmt0(perc(mk(sig,"mae_"+k),q))}</td>`).join("")}</tr>`;
  p+=`<tr><td>Mediana a favor</td>${["30m","60m","fim"].map(k=>`<td class="pos">${fmt0(median(mk(sig,"mfe_"+k)))}</td>`).join("")}</tr>`;
  $("tabPerc").innerHTML=p+`<tr><td colspan="4" style="text-align:left;color:var(--mut);font-size:12px">Um stop menor que o percentil de 75% será atingido em mais de 25% dos trades.</td></tr>`;
}

const COLS=[["dia","Dia"],["hora","Hora"],["lado","Lado"],["seq","Seq"],["entrada","Entrada"],["hist","Hist MACD"],["n_emas","Médias"],["run","Run"],["alin_pos42","42R"],["alin_pos98","98R"],["res","Resultado"],["pts","Pts"],["mfe_30m","Fav 30m"],["mae_30m","Contra 30m"],["mfe_fim","Fav 14h"],["mae_fim","Contra 14h"]];
function renderTabela(sig,S,T){
  let rows=sig.map(r=>Object.assign({},r,{res:tag(r,S,T),pts:res(r,S,T)}));
  const q=st.busca.trim().toLowerCase();
  if(q) rows=rows.filter(r=>`${r.dia} ${r.hora} ${r.lado==="V"?"venda":"compra"} ${r.res}`.toLowerCase().includes(q));
  const {k,d}=st.sort;
  rows.sort((x,y)=>{const a=x[k],b=y[k];return (typeof a==="string"?a.localeCompare(b):(a-b))*d;});
  const head=COLS.map(([c,n])=>`<th class="s" data-k="${c}">${n}${st.sort.k===c?(st.sort.d>0?" ▲":" ▼"):""}</th>`).join("");
  const body=rows.map(r=>`<tr><td>${r.dia.slice(5)}</td><td>${r.hora}</td><td>${r.lado==="V"?"▼":"▲"}</td><td>${r.seq}</td><td>${fmt0(r.entrada)}</td><td>${fmt0(r.hist)}</td><td>${r.n_emas}</td><td>${r.run}</td><td>${ctxTxt(r.alin_pos42)}</td><td>${ctxTxt(r.alin_pos98)}</td><td class="tag-${r.res}">${r.res}</td><td class="${sgn(r.pts)}">${fmt0(r.pts)}</td><td>${fmt0(r.mfe_30m)}</td><td>${fmt0(r.mae_30m)}</td><td>${fmt0(r.mfe_fim)}</td><td>${fmt0(r.mae_fim)}</td></tr>`).join("");
  $("tabSinais").innerHTML=`<tr>${head}</tr>${body}`;
  $("tabSinais").querySelectorAll("th.s").forEach(th=>th.onclick=()=>{const c=th.dataset.k;st.sort=st.sort.k===c?{k:c,d:-st.sort.d}:{k:c,d:1};render();});
}

// ---------------------------------------------------------------- controles
function fillControls(){
  $("selS").innerHTML=STOPS.map(s=>`<option value="${s}">${s} tijolo(s)</option>`).join("");
  $("selT").innerHTML=ALVOS.map(s=>`<option value="${s}">${s} tijolo(s)</option>`).join("");
  $("selS").value=st.S; $("selT").value=st.T;
  const ks=Object.keys(st.weeks);
  $("selSemana").innerHTML=ks.map(k=>`<option value="${k}">${k}</option>`).join("")+(ks.length>1?`<option value="__todas__">Todas as semanas</option>`:"");
  st.semana=ks[ks.length-1]||null; $("selSemana").value=st.semana;
  fillDias();
}
function fillDias(){
  const rows=baseRows(); const ds=[...new Set(rows.map(r=>r.dia))].sort();
  st.dias=new Set(ds);
  $("chDias").innerHTML=ds.map(d=>`<button data-v="${d}" class="on">${d.slice(8)}/${d.slice(5,7)} ${DOW[new Date(d+"T12:00:00").getDay()]}</button>`).join("");
  $("chDias").querySelectorAll("button").forEach(b=>b.onclick=()=>{const v=b.dataset.v; if(st.dias.has(v)){st.dias.delete(v);b.classList.remove("on");}else{st.dias.add(v);b.classList.add("on");} render();});
}
function chipGroup(id,key){
  $(id).querySelectorAll("button").forEach(b=>b.onclick=()=>{$(id).querySelectorAll("button").forEach(x=>x.classList.remove("on"));b.classList.add("on");st[key]=b.dataset.v;render();});
}
function bind(){
  $("selS").onchange=e=>{st.S=+e.target.value;render();};
  $("selT").onchange=e=>{st.T=+e.target.value;render();};
  $("inRs").oninput=e=>{st.rs=parseFloat(e.target.value)||0;render();};
  $("inCtr").oninput=e=>{st.ctr=Math.max(1,parseInt(e.target.value)||1);render();};
  $("inCusto").oninput=e=>{st.custo=parseFloat(e.target.value)||0;render();};
  $("selConj").onchange=e=>{st.conj=e.target.value;render();};
  $("selFiltro").onchange=e=>{st.filtro=e.target.value;render();};
  const aplicaOper=fl=>{
    st.filtro=fl; st.S=2; st.T=5; st.lado="VC"; st.hora="9-14";
    $("selFiltro").value=fl; $("selS").value=2; $("selT").value=5;
    $("chLado").querySelectorAll("button").forEach(x=>x.classList.toggle("on",x.dataset.v==="VC"));
    $("chHora").querySelectorAll("button").forEach(x=>x.classList.toggle("on",x.dataset.v==="9-14"));
    render(); $("cardVeredito").scrollIntoView({behavior:"smooth",block:"start"});
  };
  $("btnOper").onclick=()=>aplicaOper("D");
  $("btnOperG").onclick=()=>aplicaOper("G");
  $("selSemana").onchange=e=>{st.semana=e.target.value;fillDias();render();};
  $("inBusca").oninput=e=>{st.busca=e.target.value;renderTabela(filtered(baseRows()).filter(r=>r.sinal!==""),st.S,st.T);};
  $("selTema").onchange=e=>{const v=e.target.value; if(v==="auto")document.documentElement.removeAttribute("data-theme"); else document.documentElement.setAttribute("data-theme",v); render();};
  chipGroup("chLado","lado"); chipGroup("chHora","hora");
  const drop=$("drop");
  const handle=files=>{
    const list=[...files].filter(f=>/\.csv$/i.test(f.name));
    Promise.all(list.map(f=>f.text().then(t=>[f.name,t]))).then(arr=>{
      for(const [n,t] of arr){ const rows=parseCSV(t); if(rows.length){ addWeek(rows[0].semana+" · "+rows[0].renko_ticks+"R",rows);} }
      fillControls(); render();
    });
  };
  $("inFile").onchange=e=>handle(e.target.files);
  ["dragenter","dragover"].forEach(ev=>drop.addEventListener(ev,e=>{e.preventDefault();drop.classList.add("over");}));
  ["dragleave","drop"].forEach(ev=>drop.addEventListener(ev,e=>{e.preventDefault();drop.classList.remove("over");}));
  drop.addEventListener("drop",e=>handle(e.dataTransfer.files));
}

// ---------------------------------------------------------------- GitHub
function lsGet(k){try{return localStorage.getItem(k)||"";}catch(e){return "";}}
function lsSet(k,v){try{if(v)localStorage.setItem(k,v);else localStorage.removeItem(k);}catch(e){}}
async function ghLoad(silencioso){
  const repo=$("ghRepo").value.trim(), token=$("ghToken").value.trim(), out=$("ghStatus");
  if(!/^[\w.-]+\/[\w.-]+$/.test(repo)){out.textContent="Informe o repositório no formato dono/nome.";return;}
  lsSet("ghRepo",repo); lsSet("ghToken",$("ghLembrar").checked?token:"");
  const H=t=>Object.assign({"Accept":t},token?{"Authorization":"Bearer "+token,"X-GitHub-Api-Version":"2022-11-28"}:{});
  out.textContent="Buscando semanas…";
  try{
    const r=await fetch(`https://api.github.com/repos/${repo}/contents/semanas`,{headers:H("application/vnd.github+json")});
    if(r.status===404){out.textContent=token?"Repositório ou pasta semanas/ não encontrados (confira o token e o nome).":"Repositório privado ou inexistente: cole um token de leitura e tente de novo.";return;}
    if(r.status===401||r.status===403){out.textContent="GitHub recusou o acesso (token inválido, sem permissão de leitura ou limite de requisições).";return;}
    if(!r.ok){out.textContent="Erro "+r.status+" ao consultar o GitHub.";return;}
    const lista=(await r.json()).filter(x=>/^semana_.*\.csv$/i.test(x.name));
    if(!lista.length){out.textContent="Nenhum semana_*.csv encontrado em semanas/.";return;}
    let n=0;
    for(const it of lista){
      const rr=await fetch(it.url,{headers:H("application/vnd.github.raw+json")});
      if(!rr.ok) continue;
      const rows=parseCSV(await rr.text());
      if(rows.length){ addWeek(rows[0].semana+" · "+rows[0].renko_ticks+"R",rows); n++; }
    }
    fillControls(); render();
    out.textContent=`${n} semana(s) carregada(s) do GitHub às ${new Date().toLocaleTimeString("pt-BR")}.`;
  }catch(e){
    out.textContent="Não consegui falar com o GitHub (sem internet ou bloqueio do navegador). Os dados embutidos continuam disponíveis.";
  }
}

loadEmbedded();
(function galeria(){
  const ids=["23-11_a","23-11_b","24-11_a","24-11_b","25-11_a","25-11_b","26-11_a","26-11_b","27-11_a","27-11_b","27-11_c","27-11_d","27-11_e","27-11_f"];
  const base="https://raw.githubusercontent.com/PedroMateus1991/analise2026/main/imagens/prints/";
  $("galeria").innerHTML=ids.map(i=>`<a href="${base}${i}.png" target="_blank" rel="noopener"><img loading="lazy" src="${base}${i}.png" alt="Captura anotada ${i}" style="width:100%;border-radius:8px;border:1px solid var(--line)" onerror="this.parentNode.style.display='none'"></a>`).join("");
})();
$("ghRepo").value=lsGet("ghRepo")||$("ghRepo").value;
$("ghToken").value=lsGet("ghToken"); $("ghLembrar").checked=!!lsGet("ghToken");
$("ghBtn").onclick=()=>ghLoad(false);
fillControls(); bind();
if($("ghToken").value) ghLoad(true);
if(Object.keys(st.weeks).length) render(); else $("cardVeredito").innerHTML="<b>Sem dados embutidos.</b> Carregue um arquivo semana_*.csv na seção abaixo.";
</script>
<script>
"use strict";
// ================================================================= Retorno à média (toques)
(function(){
const MEDIAS=["E9","E17","E25","E29","E42","E55","R20_20","R20_72","R42_27","R42_55","R98_27","R98_55","VWAP_D","VWAP_S"];
const NOME={E9:"MME 9 (23R)",E17:"MME 17 (23R)",E25:"MME 25 (23R)",E29:"MME 29 (23R)",E42:"MME 42 (23R)",E55:"MME 55 (23R)",
  R20_20:"MME 20 do 20R",R20_72:"MME 72 do 20R (fúcsia/verde)",R42_27:"MME 27 do 42R (azul claro)",R42_55:"MME 55 do 42R (azul claro)",
  R98_27:"MME 27 do 98R",R98_55:"MME 55 do 98R",VWAP_D:"VWAP diária",VWAP_S:"VWAP semanal"};
const COR={E9:"#f472b6",E17:"#fb923c",E25:"#facc15",E29:"#a3e635",E42:"#34d399",E55:"#22d3ee",R20_20:"#818cf8",R20_72:"#e879f9",
  R42_27:"#60a5fa",R42_55:"#38bdf8",R98_27:"#c084fc",R98_55:"#a78bfa",VWAP_D:"#f43f5e",VWAP_S:"#94a3b8"};
const Z=115, TEXT=new Set(["dia","hora","media","lado","hora_b","cluster","tipo"]);
const tq={weeks:{},semana:null,entrada:"a",media:"",lado:"",hora:"",S:2,T:5,prim:true,macd:false,vwap:false,c42:false,incl:false,prox:false};
let JAN=[], lista=[];
const RAW="https://raw.githubusercontent.com/PedroMateus1991/analise2026/main/imagens/prints/";
function parse(text){
  const L=(text||"").replace(/^﻿/,"").trim().split(/\r?\n/); if(L.length<2) return [];
  const h=L[0].split(";"), out=[];
  for(let i=1;i<L.length;i++){const p=L[i].split(";"),o={};
    for(let j=0;j<h.length;j++){const k=h[j],v=p[j]===undefined?"":p[j];o[k]=TEXT.has(k)?v:(v===""?NaN:parseFloat(v.replace(",",".")));}
    out.push(o);}
  return out;
}
const strip=t=>(t||"").replace(/^\/\*.*?\*\//,"")||"{}";
try{
  const d=JSON.parse(strip(document.getElementById("toquesEmbutidos").textContent));
  for(const k of Object.keys(d)){
    const ev=parse(d[k].csv); for(const r of ev){r.m30=r.hora.slice(0,2)+(parseInt(r.hora.slice(3,5),10)<30?":00":":30");}
    tq.weeks[k]={ev,graf:d[k].graf,rej:parse(d[k].rej)};
  }
}catch(e){}
try{JAN=JSON.parse(strip(document.getElementById("janelasEmbutidas").textContent)); if(!Array.isArray(JAN)) JAN=[];}catch(e){JAN=[];}
const semanas=Object.keys(tq.weeks); tq.semana=semanas[semanas.length-1]||null;
if(!tq.semana){document.getElementById("abaToques").style.display="none";return;}
const $q=id=>document.getElementById(id);

function base(sem){
  const w=tq.weeks[tq.semana]; if(!w) return [];
  return w.ev.filter(r=>{
    if(tq.prim && r.cl_ordem!==1 && !(tq.entrada==="b" && r.b_ok===1 && false)) return false;
    if(sem!=="media" && tq.media && r.media!==tq.media) return false;
    if(tq.lado && r.lado!==tq.lado) return false;
    if(sem!=="hora" && tq.hora && r.m30!==tq.hora) return false;
    if(tq.macd && r.hist_alin!==1) return false;
    if(tq.vwap && r.vwap_d_alin!==1) return false;
    if(tq.c42 && r.ctx42!==1) return false;
    if(tq.incl && r.incl_alin!==1) return false;
    if(tq.prox && !(r.prox60>=2)) return false;
    if(tq.entrada==="b" && r.b_ok!==1) return false;
    return true;
  });
}
const key=()=>`${tq.entrada}_S${tq.S}_T${tq.T}`;
const res=r=>r[key()];
function tag(r){const x=res(r);return x===tq.T*Z?"alvo":(x===-tq.S*Z?"stop":"mm");}
function ts(rows){
  const n=rows.length; if(!n) return {n:0};
  const ch=rows.slice().sort((a,b)=>(a.dia+a.hora).localeCompare(b.dia+b.hora));
  const T=tq.T*Z,S=tq.S*Z; let w=0,l=0,mm=0,sum=0,gp=0,gl=0,cum=0,peak=0,dd=0,run=0,mx=0; const dias={};
  for(const r of ch){const x=res(r); sum+=x; if(x===T)w++; else if(x===-S)l++; else mm++; if(x>0)gp+=x; else gl-=x;
    cum+=x; peak=Math.max(peak,cum); dd=Math.max(dd,peak-cum); if(x<0){run++;mx=Math.max(mx,run);}else run=0; dias[r.dia]=(dias[r.dia]||0)+x;}
  const be=tq.S/(tq.S+tq.T), ci=wilson(w,n);
  return {n,w,l,mm,sum,exp:sum/n,pf:gl>0?gp/gl:Infinity,wr:w/n,be,lo:ci[0],hi:ci[1],dd,mx,pos:Object.values(dias).filter(v=>v>0).length,nd:Object.keys(dias).length,ch};
}
const kp=(l,v,s,c)=>`<div class="kpi"><div class="l">${l}</div><div class="v ${c||""}">${v}</div><div class="s">${s||""}</div></div>`;

function veredito(rows,a){
  const el=$q("tqVeredito");
  if(!a.n){el.innerHTML="<b>Sem trades com estes filtros.</b>";return;}
  const expR=money(a.exp)-st.custo, indep=new Set(rows.map(r=>r.cluster)).size;
  const posthoc=!!(tq.media||tq.lado||tq.hora||tq.macd||tq.vwap||tq.c42||tq.incl||tq.prox);
  let cls,txt;
  if(expR>0&&a.lo>a.be){cls="pos";txt="COMPENSA (com evidência)";}
  else if(expR>0){cls="mid";txt="POSITIVO, MAS NÃO CONCLUSIVO";}
  else if(a.hi<a.be){cls="neg";txt="NÃO COMPENSA";}
  else{cls="neg";txt="NÃO COMPENSOU NESTA AMOSTRA";}
  if(posthoc&&cls==="pos"){cls="mid";txt="POSITIVO, MAS O FILTRO FOI ESCOLHIDO DEPOIS DE VER OS DADOS";}
  const pts=[];
  pts.push(`Entrada <b>${tq.entrada==="a"?"no toque":"na virada de box"}</b> · stop ${tq.S*Z} pts / gain ${tq.T*Z} pts · equilíbrio <b>${pct(a.be)}</b>.`);
  pts.push(`Taxa de alvo <b>${pct(a.wr)}</b> (IC 95%: ${pct(a.lo)} a ${pct(a.hi)}); expectativa <b class="${sgn(expR)}">${fmt1(a.exp)} pts</b> = <b class="${sgn(expR)}">${fmtR(expR)}</b> por trade.`);
  pts.push(`<b>${a.n}</b> trade(s) em <b>${indep}</b> movimento(s) independente(s). ${tq.prim?"Contando só o 1º toque de cada movimento.":"<b>Atenção:</b> sem a opção “só o 1º toque”, o mesmo movimento é contado várias vezes e os números ficam inflados."}`);
  if(a.n<30) pts.push(`<b>Amostra pequena</b> (${a.n} trades).`);
  if(posthoc) pts.push("Há filtros ativos escolhidos depois de olhar esta semana: trate como hipótese e confirme em semanas novas.");
  el.innerHTML=`<div class="verdict"><div class="vbadge ${cls}">${txt}</div><div class="vtext"><ul>${pts.map(x=>`<li>${x}</li>`).join("")}</ul></div></div>
  <div class="kpis">${kp("Trades",a.n,`${a.w} alvos · ${a.l} stops · ${a.mm} a mercado`)}${kp("Taxa de alvo",pct(a.wr),"equilíbrio "+pct(a.be),a.wr>=a.be?"pos":"neg")}
  ${kp("Expectativa (pts)",fmt1(a.exp),fmtR(expR)+" por trade",sgn(expR))}${kp("Resultado total",fmt0(a.sum)+" pts",fmtR(money(a.sum)-st.custo*a.n),sgn(a.sum))}
  ${kp("Fator de lucro",isFinite(a.pf)?a.pf.toLocaleString("pt-BR",{maximumFractionDigits:2}):"∞","ganhos ÷ perdas",a.pf>=1?"pos":"neg")}
  ${kp("Maior queda",fmt0(a.dd)+" pts",fmtR(money(a.dd)),"neg")}${kp("Stops seguidos",a.mx,"sequência mais longa")}${kp("Dias positivos",a.pos+"/"+a.nd,"")}</div>`;
}

function barra(v,mx){return `<span class="bar" style="width:${Math.round(60*Math.abs(v)/(mx||1))}px;background:${v>=0?"var(--pos)":"var(--neg)"}"></span>`;}
function rank(){
  const rows=base("media"), w=tq.weeks[tq.semana], rej={};
  for(const r of w.rej){const a=rej[r.media]||(rej[r.media]={pav:0,ok:0,alem:0}); if(r.tipo!=="corpo"){a.pav++; if(!isNaN(r.fecha_alem)){a.ok++;a.alem+=r.fecha_alem;}}}
  const L=MEDIAS.map(m=>{const it=rows.filter(r=>r.media===m);const s=ts(it);
    const h1=it.length?it.reduce((x,r)=>x+r.held1,0)/it.length:NaN,h2=it.length?it.reduce((x,r)=>x+r.held2,0)/it.length:NaN;
    const rj=rej[m]&&rej[m].ok?1-rej[m].alem/rej[m].ok:NaN;return {m,s,h1,h2,rj,nrj:rej[m]?rej[m].ok:0};});
  L.sort((a,b)=>(b.s.n?b.s.exp:-1e9)-(a.s.n?a.s.exp:-1e9));
  const mx=Math.max(1,...L.map(x=>x.s.n?Math.abs(x.s.exp):0));
  $q("tqRank").innerHTML=`<tr><th>Média</th><th>n</th><th>acerto</th><th>exp. pts</th><th></th><th>dias+</th><th>1 tij a favor antes de 1 contra</th><th>2 a favor antes de 1 contra</th><th>rejeição no pavio</th></tr>`+
   L.map(x=>`<tr class="${x.s.n<8?"small":""}" data-m="${x.m}" style="cursor:pointer${tq.media===x.m?";background:var(--posbg)":""}"><td>${NOME[x.m]}</td><td>${x.s.n||0}</td><td class="${x.s.n&&x.s.wr>=x.s.be?"pos":"neg"}">${x.s.n?pct(x.s.wr):"—"}</td><td class="${sgn(x.s.exp)}">${x.s.n?fmt0(x.s.exp):"—"}</td><td style="text-align:left">${x.s.n?barra(x.s.exp,mx):""}</td><td>${x.s.n?x.s.pos+"/"+x.s.nd:"—"}</td><td>${isNaN(x.h1)?"—":pct(x.h1)}</td><td>${isNaN(x.h2)?"—":pct(x.h2)}</td><td>${isNaN(x.rj)?"—":pct(x.rj)+` <span class="sub">(n=${x.nrj})</span>`}</td></tr>`).join("");
  $q("tqRank").querySelectorAll("tr[data-m]").forEach(tr=>tr.onclick=()=>{tq.media=tq.media===tr.dataset.m?"":tr.dataset.m;$q("tqMedia").value=tq.media;renderTq();});
}
function horarios(){
  const rows=base("hora"), bs=[...new Set(tq.weeks[tq.semana].ev.map(r=>r.m30))].sort();
  const L=bs.map(b=>({b,s:ts(rows.filter(r=>r.m30===b))})); const mx=Math.max(1,...L.map(x=>x.s.n?Math.abs(x.s.exp):0));
  $q("tqHorarios").innerHTML=`<tr><th>Bloco</th><th>n</th><th>acerto</th><th>exp. pts</th><th></th><th>dias+</th></tr>`+L.map(x=>`<tr class="${x.s.n<8?"small":""}" data-b="${x.b}" style="cursor:pointer${tq.hora===x.b?";background:var(--posbg)":""}"><td>${x.b}–${(()=>{const h=parseInt(x.b.slice(0,2),10),m=x.b.slice(3)==="00"?"30":"00";return String(m==="00"?h+1:h).padStart(2,"0")+":"+m;})()}</td><td>${x.s.n||0}</td><td class="${x.s.n&&x.s.wr>=x.s.be?"pos":"neg"}">${x.s.n?pct(x.s.wr):"—"}</td><td class="${sgn(x.s.exp)}">${x.s.n?fmt0(x.s.exp):"—"}</td><td style="text-align:left">${x.s.n?barra(x.s.exp,mx):""}</td><td>${x.s.n?x.s.pos+"/"+x.s.nd:"—"}</td></tr>`).join("");
  $q("tqHorarios").querySelectorAll("tr[data-b]").forEach(tr=>tr.onclick=()=>{tq.hora=tq.hora===tr.dataset.b?"":tr.dataset.b;$q("tqHora").value=tq.hora;renderTq();});
}
function relacao(){
  const el=$q("tqRel");
  if(!tq.media){el.innerHTML=`<tr><td style="text-align:left;color:var(--mut)">Escolha uma média no filtro acima (ou clique numa linha do ranking).</td></tr>`;return;}
  const rows=base(null);
  const L=MEDIAS.filter(y=>y!==tq.media).map(y=>({y,b:ts(rows.filter(r=>r["rel_"+y]===-1)),c:ts(rows.filter(r=>r["rel_"+y]===1))}));
  const cel=s=>s.n?`<td>${s.n}</td><td class="${s.wr>=s.be?"pos":"neg"}">${pct(s.wr)}</td><td class="${sgn(s.exp)}">${fmt0(s.exp)}</td>`:`<td>0</td><td>—</td><td>—</td>`;
  el.innerHTML=`<tr><th>Outra média (Y)</th><th colspan="3">${NOME[tq.media]} ABAIXO de Y</th><th colspan="3">… ACIMA de Y</th></tr><tr><th></th><th>n</th><th>acerto</th><th>exp.</th><th>n</th><th>acerto</th><th>exp.</th></tr>`+L.map(x=>`<tr class="${x.b.n+x.c.n<10?"small":""}"><td>${NOME[x.y]}</td>${cel(x.b)}${cel(x.c)}</tr>`).join("");
}
function grupos(){
  const rows=base(null), G=[];
  const g=(tit,fn,ord)=>{const m=new Map();for(const r of rows){const k=fn(r);if(k===null||k===undefined)continue;if(!m.has(k))m.set(k,[]);m.get(k).push(r);}
    const keys=ord?ord.filter(k=>m.has(k)):[...m.keys()].sort();const L=keys.map(k=>[k,ts(m.get(k))]);const mx=Math.max(1,...L.map(([k,s])=>Math.abs(s.exp)));
    G.push(`<div class="scroll"><h2 style="font-size:13px">${tit}</h2><table><tr><th></th><th>n</th><th>acerto</th><th>exp. pts</th><th></th></tr>${L.map(([k,s])=>`<tr class="${s.n<10?"small":""}"><td>${k}</td><td>${s.n}</td><td class="${s.wr>=s.be?"pos":"neg"}">${pct(s.wr)}</td><td class="${sgn(s.exp)}">${fmt0(s.exp)}</td><td style="text-align:left">${barra(s.exp,mx)}</td></tr>`).join("")}</table></div>`);};
  const sn=v=>v===1?"sim":(v===0?"não":null), tri=v=>v===1?"a favor":(v===0?"entre as médias":"contra");
  g("MACD alinhado (hist<0 na venda, >0 na compra)",r=>sn(r.hist_alin),["sim","não"]);
  g("MACD crescendo a favor",r=>sn(r.hist_cresce),["sim","não"]);
  g("Média tocada inclinada a favor",r=>sn(r.incl_alin),["sim","não"]);
  g("Nível a favor da VWAP diária",r=>isNaN(r.vwap_d_alin)?null:sn(r.vwap_d_alin),["sim","não"]);
  g("VWAP diária junto do nível (≤ 60 pts)",r=>isNaN(r.vwap_d_dist)?null:(Math.abs(r.vwap_d_dist)<=60?"junto":"longe"),["junto","longe"]);
  g("Nível a favor da VWAP semanal",r=>isNaN(r.vwap_s_alin)?null:sn(r.vwap_s_alin),["sim","não"]);
  g("42R (azul claro): preço × médias 27 e 55",r=>tri(r.ctx42),["a favor","entre as médias","contra"]);
  g("98R: preço × médias 27 e 55",r=>tri(r.ctx98),["a favor","entre as médias","contra"]);
  g("Scalp4 do mesmo lado nos últimos 5 tijolos",r=>r.scalp4===1?"sim":"não",["sim","não"]);
  g("Operacional D recente",r=>r.scalpD===1?"sim":"não",["sim","não"]);
  g("Outras médias/VWAP a ≤ 60 pts (confluência)",r=>r.prox60===0?"nenhuma":(r.prox60===1?"1":(r.prox60<=3?"2-3":"4 ou mais")),["nenhuma","1","2-3","4 ou mais"]);
  g("Médias tocadas no mesmo movimento",r=>r.cluster_n===1?"1":(r.cluster_n<=3?"2-3":(r.cluster_n<=6?"4-6":"7 ou mais")),["1","2-3","4-6","7 ou mais"]);
  g("Distância percorrida antes do toque",r=>r.dist_antes<230?"115–230":(r.dist_antes<460?"230–460":"460 ou mais"),["115–230","230–460","460 ou mais"]);
  g("Lado",r=>r.lado==="V"?"Venda ▼ (resistência)":"Compra ▲ (suporte)",["Venda ▼ (resistência)","Compra ▲ (suporte)"]);
  $q("tqGrupos").innerHTML=G.join("");
}
function trades(){
  const rows=base(null).slice().sort((a,b)=>(a.dia+a.hora).localeCompare(b.dia+b.hora)); lista=rows;
  $q("tqTrades").innerHTML=`<tr><th>Dia</th><th>Hora</th><th>Média</th><th>Lado</th><th>Nível</th><th>Resultado</th><th>Pts</th><th>Juntas</th><th>MACD</th><th>VWAP D</th><th>42R</th><th></th></tr>`+
   rows.map((r,i)=>{const t=tag(r),x=res(r);return `<tr><td>${r.dia.slice(5)}</td><td>${r.hora}</td><td>${NOME[r.media]}</td><td>${r.lado==="V"?"▼":"▲"}</td><td>${fmt0(r.nivel)}</td><td class="tag-${t}">${t}</td><td class="${sgn(x)}">${fmt0(x)}</td><td>${r.prox60}</td><td>${r.hist_alin===1?"sim":"não"}</td><td>${isNaN(r.vwap_d_alin)?"—":(r.vwap_d_alin===1?"a favor":"contra")}</td><td>${r.ctx42===1?"a favor":(r.ctx42===0?"entre":"contra")}</td><td><button data-i="${i}">gráfico</button></td></tr>`;}).join("");
  $q("tqTrades").querySelectorAll("button[data-i]").forEach(b=>b.onclick=()=>abrir(lista[+b.dataset.i]));
}
const secOf=h=>{const p=h.split(":");return (+p[0])*3600+(+p[1])*60+(+p[2]);};
const hms=s=>String(Math.floor(s/3600)).padStart(2,"0")+":"+String(Math.floor(s%3600/60)).padStart(2,"0")+":"+String(s%60).padStart(2,"0");
function abrir(r){
  const g=tq.weeks[tq.semana].graf[r.dia]; if(!g) return;
  const k=r.idx-1, n=g.t.length, k0=Math.max(0,k-28), k1=Math.min(n-1,k+48);
  const entB=tq.entrada==="b"&&r.entrada_b!==""&&!isNaN(r.entrada_b), e=entB?r.entrada_b:r.nivel;
  const stopL=r.lado==="V"?e+tq.S*Z:e-tq.S*Z, gainL=r.lado==="V"?e-tq.T*Z:e+tq.T*Z;
  const nomes=[r.media].concat(["VWAP_D","E9","E25","E55","R42_27","R42_55"].filter(x=>x!==r.media));
  let mn=1e12,mx=-1e12;
  for(let i=k0;i<=k1;i++){mn=Math.min(mn,g.l[i]);mx=Math.max(mx,g.h[i]);}
  const span0=mx-mn;
  for(const nm of nomes){for(let i=k0;i<=k1;i++){const v=g.med[nm][i];if(v!=null&&v>mn-span0&&v<mx+span0){mn=Math.min(mn,v);mx=Math.max(mx,v);}}}
  mn=Math.min(mn,stopL,gainL,r.nivel);mx=Math.max(mx,stopL,gainL,r.nivel);
  const W=960,H=430,pl=62,pr=14,pt=12,pb=28,dx=(W-pl-pr)/(k1-k0+1),X=i=>pl+(i-k0)*dx+dx/2,Y=v=>pt+(H-pt-pb)*(1-(v-mn)/((mx-mn)||1));
  let s=`<svg viewBox="0 0 ${W} ${H}" width="100%" role="img">`;
  for(let t=0;t<=5;t++){const v=mn+(mx-mn)*t/5;s+=`<line x1="${pl}" x2="${W-pr}" y1="${Y(v)}" y2="${Y(v)}" stroke="var(--line)"/><text x="${pl-5}" y="${Y(v)+4}" text-anchor="end">${fmt0(v)}</text>`;}
  for(let i=k0;i<=k1;i+=Math.ceil((k1-k0)/9))s+=`<text x="${X(i)}" y="${H-8}" text-anchor="middle">${hms(g.t[i]).slice(0,5)}</text>`;
  for(const nm of nomes){let d="",pen=false;for(let i=k0;i<=k1;i++){const v=g.med[nm][i];if(v==null||v<mn-1||v>mx+1){pen=false;continue;}d+=(pen?"L":"M")+X(i).toFixed(1)+","+Y(v).toFixed(1)+" ";pen=true;}
    s+=`<path d="${d}" fill="none" stroke="${COR[nm]}" stroke-width="${nm===r.media?3:1.4}" ${nm.startsWith("VWAP")?'stroke-dasharray="6 4"':""} opacity="${nm===r.media?1:.8}"/>`;}
  for(let i=k0;i<=k1;i++){const up=g.c[i]>g.o[i],c=up?"#3b82f6":"#d4a72c",x=X(i),bt=Y(Math.max(g.o[i],g.c[i])),bb=Y(Math.min(g.o[i],g.c[i]));
    s+=`<g opacity="${g.gap[i]?.4:1}"><line x1="${x}" x2="${x}" y1="${Y(g.h[i])}" y2="${Y(g.l[i])}" stroke="${c}"/><rect x="${x-dx*.32}" y="${bt}" width="${dx*.64}" height="${Math.max(1.5,bb-bt)}" fill="${c}"><title>${hms(g.t[i])} abre ${g.o[i]} fecha ${g.c[i]}</title></rect></g>`;}
  const xk=X(k), corE=r.lado==="V"?"#ef4444":"#22c55e";
  s+=`<line x1="${xk}" x2="${xk}" y1="${pt}" y2="${H-pb}" stroke="var(--mut)" stroke-dasharray="3 3"/>`;
  s+=`<circle cx="${xk}" cy="${Y(r.nivel)}" r="6" fill="none" stroke="${corE}" stroke-width="2.5"/><text x="${xk+9}" y="${Y(r.nivel)-8}" style="fill:${corE};font-weight:700">toque ${r.hora}</text>`;
  if(entB){const kb=g.t.findIndex(t=>t>=secOf(r.hora_b));if(kb>=k0&&kb<=k1){s+=`<circle cx="${X(kb)}" cy="${Y(e)}" r="6" fill="${corE}"/><text x="${X(kb)+9}" y="${Y(e)+16}" style="fill:${corE};font-weight:700">virada ${r.hora_b}</text>`;}}
  const xs=entB?xk:xk;
  s+=`<line x1="${xs}" x2="${W-pr}" y1="${Y(stopL)}" y2="${Y(stopL)}" stroke="#ef4444" stroke-dasharray="5 4"/><text x="${W-pr-4}" y="${Y(stopL)-4}" text-anchor="end" style="fill:#ef4444">stop ${tq.S*Z} pts (${fmt0(stopL)})</text>`;
  s+=`<line x1="${xs}" x2="${W-pr}" y1="${Y(gainL)}" y2="${Y(gainL)}" stroke="#22c55e" stroke-dasharray="5 4"/><text x="${W-pr-4}" y="${Y(gainL)-4}" text-anchor="end" style="fill:#22c55e">gain ${tq.T*Z} pts (${fmt0(gainL)})</text></svg>`;
  $q("tqModalTit").textContent=`${r.dia.slice(8)}/${r.dia.slice(5,7)} ${r.hora} · ${NOME[r.media]} · ${r.lado==="V"?"venda":"compra"} · ${tag(r)} (${fmt0(res(r))} pts)`;
  $q("tqGraf").innerHTML=s+`<div class="legend">`+nomes.map(nm=>`<span style="color:${COR[nm]}">━</span> ${NOME[nm]} (${g.med[nm][k]==null?"—":fmt0(g.med[nm][k])})`).join(" &nbsp; ")+`</div>`;
  $q("tqGrafNota").innerHTML=`Tijolos de 115 pts (azul = alta, amarelo = baixa, esmaecido = tijolo de gap de abertura). As linhas são as médias no nível em que estavam quando o tijolo se formou. Entrada ${entB?"na virada":"no toque (ordem limite no nível da média)"}; stop e gain medidos a partir dela. Tijolo nº ${r.idx} do dia. Confira no seu Profit pelo horário.`;
  const hh=r.hora.slice(0,5), j=JAN.find(w=>w.trechos.some(t=>t.dia===r.dia&&t.t0<=hh&&hh<=t.t1));
  $q("tqPrint").innerHTML=j?`<div class="sub">Captura do Profit que cobre este horário (${j.titulo}). Procure o toque às <b>${r.hora}</b> (tijolo nº ${r.idx}):</div><a href="${RAW}${j.id}.png" target="_blank" rel="noopener"><img loading="lazy" src="${RAW}${j.id}.png" alt="Captura do Profit ${j.id}" style="max-width:100%;border-radius:8px;border:1px solid var(--line)" onerror="this.parentNode.style.display='none'"></a>`:`<div class="sub">Sem captura do Profit para este horário.</div>`;
  $q("tqModal").hidden=false;
}
function renderTq(){
  const rows=base(null), a=ts(rows);
  const w=tq.weeks[tq.semana], nev=w.ev.length, ncl=new Set(w.ev.map(r=>r.cluster)).size;
  $q("tqSub").textContent=`${semanas.join(" · ")} · ${nev} toques detectados = ${ncl} movimentos independentes · janela 09:00–14:00 · 14 médias (23R, 20R, 42R, 98R e VWAP)`;
  $q("tqPayoff").innerHTML=`Stop <b>${tq.S*Z} pts</b> (${fmtR(money(tq.S*Z))}) · gain <b>${tq.T*Z} pts</b> (${fmtR(money(tq.T*Z))}) · equilíbrio <b>${pct(tq.S/(tq.S+tq.T))}</b>. Valor do ponto, contratos e custo vêm da aba “Sinais do scalp4”.`;
  veredito(rows,a); rank(); horarios(); relacao(); grupos(); trades();
}
function init(){
  $q("tqMedia").innerHTML=`<option value="">Todas</option>`+MEDIAS.map(m=>`<option value="${m}">${NOME[m]}</option>`).join("");
  const bs=[...new Set(tq.weeks[tq.semana].ev.map(r=>r.m30))].sort();
  $q("tqHora").innerHTML=`<option value="">9h às 14h</option>`+bs.map(b=>`<option value="${b}">${b}</option>`).join("");
  $q("tqS").innerHTML=[1,2,3,4].map(v=>`<option value="${v}">${v} tijolo(s)</option>`).join(""); $q("tqS").value=2;
  $q("tqT").innerHTML=[1,2,3,4,5,6,8,10].map(v=>`<option value="${v}">${v} tijolo(s)</option>`).join(""); $q("tqT").value=5;
  const sel=(id,k,num)=>{$q(id).onchange=e=>{tq[k]=num?+e.target.value:e.target.value;renderTq();};};
  sel("tqEntrada","entrada"); sel("tqMedia","media"); sel("tqLado","lado"); sel("tqHora","hora"); sel("tqS","S",true); sel("tqT","T",true);
  for(const [id,k] of [["tqPrim","prim"],["tqMacd","macd"],["tqVwap","vwap"],["tqC42","c42"],["tqIncl","incl"],["tqProx","prox"]]) $q(id).onchange=e=>{tq[k]=e.target.checked;renderTq();};
  $q("tqFechar").onclick=()=>{$q("tqModal").hidden=true;};
  $q("tqModal").onclick=e=>{if(e.target===$q("tqModal"))$q("tqModal").hidden=true;};
  document.addEventListener("keydown",e=>{if(e.key==="Escape")$q("tqModal").hidden=true;});
  const show=t=>{$q("viewScalp").hidden=t;$q("viewToques").hidden=!t;$q("abaScalp").classList.toggle("on",!t);$q("abaToques").classList.toggle("on",t);if(t)renderTq();};
  $q("abaScalp").onclick=()=>show(false); $q("abaToques").onclick=()=>show(true);
}
init();
})();
</script>
</body>
</html>
