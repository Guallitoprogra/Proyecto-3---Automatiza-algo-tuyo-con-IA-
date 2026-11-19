'use strict';
// Tres pantallas para el uso diario y la demostración del curso.
const simples=['inicio','movimientos','casos'].map(id=>pages.find(p=>p[0]===id));
pages.splice(0,pages.length,...simples);
pages[2][1]='Pruebas del proyecto';
titles.movimientos=['Tus movimientos','Busca, revisa o registra un gasto.','TU HISTORIAL'];
titles.casos=['Pruebas del proyecto','Los tres casos reales, en un solo lugar.','EVIDENCIA DEL CURSO'];

function metrics(){
 const rs=buys(),cats=groups(rs,'categoria');
 return `<div class="metrics simple-metrics">${[
 ['Gasto registrado',money(sum(rs)),`${rs.length} compras en la selección actual`],
 ['Categoría con más gasto',cats.length?esc(cats[0][0]):'Sin compras',cats.length?money(cats[0][1]):''],
 ['Medio seleccionado',card==='todas'?'Todos':esc(cardObj(card).nombre),'Puedes cambiarlo en el filtro de arriba']
 ].map(([label,value,note])=>`<div class="metric"><div class="metric-label">${label}</div><div class="metric-value" style="font-size:23px">${value}</div><div class="metric-note">${esc(note)}</div></div>`).join('')}</div>`;
}

function observacionesSimples(){
 const rs=buys(),cs=groups(rs,'categoria');let out='';
 if(cs.length)out+=insight('Tu categoría principal',`${cs[0][0]} suma ${money(cs[0][1])}. Revisa si corresponde a compras habituales o a una compra puntual.`);
 const rep=groups(rs,'comercio').find(([c])=>rs.filter(r=>r.comercio===c).length>=3);
 if(rep)out+=insight('Un gasto que se repite',`${rs.filter(r=>r.comercio===rep[0]).length} compras en ${rep[0]} suman ${money(rep[1])}. Si quieres ajustar tus gastos, puedes empezar revisando esta frecuencia.`);
 const sin=rs.filter(r=>r.confirmada!=='si').length;
 if(sin)out+=insight('Categorías por revisar',`${sin} compras tienen categorías propuestas. Usa Revisar en Movimientos para corregirlas y enseñarle al clasificador.`);
 return out||'<p class="subnote">Agrega compras para ver observaciones.</p>';
}

function overview(){
 const extra=rows().filter(r=>r.tipo!=='compra');
 return `${metrics()}${titlePanel('Gastos por tarjeta','Pulsa una tarjeta para ver sus movimientos.')}${bankCards()}
 <div class="columns"><div class="panel">${titlePanel('¿En qué gastaste?','Compras por categoría · filtro actual')}${donut()}</div><div class="panel">${titlePanel('Lo que puedes revisar','Observaciones sencillas basadas en tus registros.')}${observacionesSimples()}</div></div>
 ${extra.length?`<details class="panel wide-panel"><summary>Otros movimientos: pagos, transferencias o créditos (${extra.length})</summary><p class="subnote">Se muestran aparte; no se suman como nuevas compras.</p>${data.ficticio?'':libroCreditos()}${table(extra,false)}</details>`:''}
 <div class="panel transactions-panel">${titlePanel('Últimos movimientos','', '<button class="text-button" data-page="movimientos">Ver todos →</button>')}${table(recent().slice(0,5))}</div>`;
}

function resultadosCasos(o){
 return `<p class="subnote" style="margin-bottom:15px">Resultados guardados en evidencias/casos_reales. Los cálculos y las sugerencias de IA se revisan por separado.</p>`+o.resultados.map((c,i)=>`<div class="panel wide-panel"><div class="section-title"><h2>${i+1}. ${esc(c.nombre)}</h2><span class="pill">${c.calculos_correctos?'Cálculos coinciden':'Revisar diferencias'}</span></div>
 <div class="table-wrap"><table class="table"><thead><tr><th>Comprobación</th><th>Esperado</th><th>Resultado</th></tr></thead><tbody>${c.verificaciones.map(v=>`<tr><td>${esc(v.campo)}</td><td>${esc(v.esperado)}</td><td>${esc(v.observado)} ${v.coincide?'✓':'!'}</td></tr>`).join('')}</tbody></table></div>
 <details class="simple-details"><summary>Ver sugerencias de IA y posibles errores (${c.predicciones.length})</summary><p class="subnote">Contrasta estas sugerencias con tus capturas. Las categorías importadas que no confirmaste no son respuestas verificadas.</p><div class="table-wrap"><table class="table"><thead><tr><th>Movimiento</th><th>Sugiere la IA</th><th>Categoría importada</th></tr></thead><tbody>${c.predicciones.map(p=>`<tr><td>${esc(p.id)} · ${esc(p.comercio)}</td><td>${esc(p.categoria_sugerida)}${p.reconocido?'':' (por revisar)'}</td><td>${esc(p.categoria_importada)}</td></tr>`).join('')}</tbody></table></div></details>
 <p class="subnote">${esc(c.fuente)} Cómputo: ${c.tiempo_maquina_segundos.toFixed(6)} s; no incluye revisión humana.</p></div>`).join('');
}

window.addEventListener('DOMContentLoaded',()=>{
 // La naturaleza personal ya no es un campo que tengas que entender para registrar.
 const f=$('#expense-form');f.elements.naturaleza.closest('label').hidden=true;
 const tipoLabel=f.elements.tipo.closest('label');
 const advanced=document.createElement('details');advanced.className='simple-details wide';
 const summary=document.createElement('summary');summary.textContent='Otro tipo de movimiento (pago, transferencia o créditos)';
 advanced.append(summary);tipoLabel.before(advanced);advanced.append(tipoLabel);
 const check=f.elements.confirmada.closest('label');check.lastChild.textContent=' Usar esta categoría para aprender';
});
