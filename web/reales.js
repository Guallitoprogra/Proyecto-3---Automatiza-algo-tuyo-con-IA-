'use strict';
// Vista de pruebas reales. Los resultados llegan del backend y no se inventan en la interfaz.
pages.splice(pages.length-1,0,['casos','Casos reales','<path d="M5 3h14v18H5zM8 8h8M8 12h8M8 16h5"/>']);
titles.casos=['Tres casos, tus datos','Contrasta los resultados con tus capturas y registra tus propias observaciones.','PRUEBAS CON GASTOS REALES'];
let casoResultado=null;
function realHeader(){
 if(data.ficticio)return;
 if(!casoResultado&&data.casos_ultima)casoResultado=data.casos_ultima;
 document.querySelector('.demo').innerHTML='<i></i> DATOS REALES · MUESTRA PARCIAL';
 document.querySelector('.profile>div').innerHTML='Tus gastos reales<small>Medios identificados por captura</small>';
 document.querySelector('.profile .avatar').textContent='T';
 document.querySelector('footer').textContent='Muestra real parcial de noviembre. Categorías propuestas por revisar. Créditos del club separados; no es saldo bancario ni deuda.';
 document.querySelector('.period-note').textContent='Capturas del 17 nov 2026';
 const mode=document.querySelector('#mode-link');mode.href='http://127.0.0.1:8768/';mode.textContent='Ver demostración ↗';
 titles.inicio=['Tus gastos reales','Una muestra de tus capturas, con información pendiente claramente señalada.','TU PRUEBA PERSONAL'];
 $('#expense-form').elements.tipo.innerHTML=data.tipos.map(t=>option(t,labels[t]||t)).join('');
 const naturaleza=$('#expense-form').elements.naturaleza;
 if(![...naturaleza.options].some(o=>o.value==='sin_confirmar'))naturaleza.add(new Option('Sin confirmar','sin_confirmar'));
}
function casosView(){
 if(data.ficticio)return `<div class="panel guides"><h3>Los casos reales tienen su propio espacio</h3><p>Conservamos intactos los datos ficticios. Abre el modo real para ejecutar las tres pruebas con tus capturas.</p><a class="primary" style="display:inline-block;align-self:start" href="http://127.0.0.1:8769/#casos">Abrir casos reales →</a></div>`;
 return `<div class="overview-tip">Se usan los 47 movimientos de tus capturas anteriores, sin la captura repetida. Las categorías no confirmadas siguen siendo propuestas. Los límites personales y la naturaleza del gasto no se inventan.</div>
 <div class="analysis-grid">${[
 ['1','Pedidos de comida','7 pedidos · Q657.75','Revisa fechas, importes y sugerencias de categoría.'],
 ['2','Tarjetas A y B','20 movimientos · Q4,062.49','A = captura 8; B = captura 9. No se supone banco, tipo ni propietario adicional.'],
 ['3','Pagos y créditos de pádel','20 movimientos separados','Cargos Q588.02 · consumos de créditos Q646.67 · devoluciones a créditos Q760.02 · pendiente Q20.']
 ].map(([n,t,m,d])=>`<div class="analysis-item"><span class="big-icon">${n}</span><h3>${t}</h3><strong style="font-size:19px">${m}</strong><p>${d}</p></div>`).join('')}</div>
 <div class="panel wide-panel"><div class="section-title"><div><h2>Ejecuta y guarda la evidencia</h2><p class="subnote">Se guardan los resultados numéricos, las sugerencias de IA y el tiempo de máquina. Los datos del caso evaluado se excluyen de su entrenamiento.</p></div><button class="primary" id="run-cases">Ejecutar los tres casos</button></div><p class="subnote">No se evalúa exactitud usando categorías propuestas como si fueran verdad confirmada. Tu revisión, tiempo manual, tiempo de configuración y reflexión quedan pendientes de tu experiencia.</p></div>
 <div id="case-results">${casoResultado?resultadosCasos(casoResultado):'<div class="panel empty">Pulsa el botón para ejecutar las pruebas con el registro actual.</div>'}</div>`;
}
function resultadosCasos(o){return `<div class="overview-tip">Ejecución UTC: ${esc(o.fecha_utc)} · Resultados guardados en evidencias/casos_reales. El resultado de cálculos y la calidad de clasificación se revisan por separado.</div>`+o.resultados.map(c=>`<div class="panel wide-panel"><div class="section-title"><h2>${esc(c.nombre)}</h2><span class="pill ${c.calculos_correctos?'':'purple'}">${c.calculos_correctos?'Cálculos coinciden':'Hay diferencias que revisar'}</span></div><p class="subnote">${esc(c.fuente)}</p><div class="table-wrap"><table class="table"><thead><tr><th>Comprobación</th><th>Esperado</th><th>Observado</th><th>Coincide</th></tr></thead><tbody>${c.verificaciones.map(v=>`<tr><td>${esc(v.campo)}</td><td>${esc(v.esperado)}</td><td>${esc(v.observado)}</td><td>${v.coincide?'Sí':'No'}</td></tr>`).join('')}</tbody></table></div><h3 style="margin-top:22px">Sugerencias del modelo · revisión humana pendiente</h3><div class="table-wrap"><table class="table"><thead><tr><th>Movimiento</th><th>Sugerencia de IA</th><th>Categoría importada</th><th>Estado</th></tr></thead><tbody>${c.predicciones.map(p=>`<tr><td>${esc(p.id)} · ${esc(p.comercio)}</td><td>${esc(p.categoria_sugerida)}</td><td>${esc(p.categoria_importada)}</td><td>${p.reconocido?'Sugerencia por revisar':'Texto no reconocido / empate'}</td></tr>`).join('')}</tbody></table></div><p class="subnote">Cómputo: ${c.tiempo_maquina_segundos.toFixed(6)} s. No incluye transcripción, configuración ni revisión. Compara la sugerencia con la captura y decide tú si es correcta.</p></div>`).join('')}
function bindCasos(){
 $('#run-cases')?.addEventListener('click',async e=>{const b=e.currentTarget;b.disabled=true;b.textContent='Ejecutando…';try{casoResultado=await api('/api/casos',{});$('#case-results').innerHTML=resultadosCasos(casoResultado);toast('Evidencia de los tres casos guardada.')}catch(err){toast(err.message)}finally{b.disabled=false;b.textContent='Ejecutar los tres casos'}})
}

function libroCreditos(){
 if(data.ficticio)return '';
 return `<div class="panel wide-panel"><h3>Créditos del club y movimientos por aclarar</h3><div class="analysis-grid" style="margin:15px 0 0">${[
 ['Consumos de créditos','consumo_creditos'],['Devoluciones a créditos','devolucion_creditos'],['Importe pendiente','pendiente']
 ].map(([nombre,tipo])=>`<div><p class="subnote">${nombre}</p><strong style="font-size:22px">${money(sum(rows().filter(r=>r.tipo===tipo)))}</strong></div>`).join('')}</div><p class="subnote">No se agregan a las compras ni se restan de los cargos a tarjeta. Faltan saldo inicial y conciliación para calcular el saldo del club.</p></div>`;
}

function proyectoReal(){return `<div class="panel guides"><h3>La misma aplicación, con tus datos reales</h3><p>Hay 47 movimientos de las capturas que compartiste. La captura repetida se excluyó. Los alias A y B identifican las capturas de tarjetas; otros pagos quedan sin identificar cuando la fuente no lo permite.</p><h3>Tu exploración ya tiene evidencia</h3><p>Las seis capturas se guardaron identificadas por ti: ChatGPT 1 y 4, Gemini 2 y 5, Claude 3 y 6. Tú completas facilidad, plan utilizado y observaciones; las capturas no muestran todos esos datos.</p><h3>Pruebas reales</h3><p>En Casos reales puedes repetir las comprobaciones numéricas y ver las sugerencias de IA, incluidas las que requieren corrección. Se guardan en <code>evidencias/casos_reales</code>. Los cálculos y la clasificación se revisan por separado.</p><h3>Tu siguiente paso</h3><p>Contrasta los resultados con las capturas. Completa tus observaciones y mide el tiempo manual y el de revisión. Los tiempos de máquina no incluyen la configuración ni tu trabajo. El informe completo y la reflexión permanecen para tu propia redacción.</p><h3>Demostración conservada</h3><p>Los datos ficticios siguen en su propio espacio. El botón Ver demostración abre ese modo. Los registros reales se guardan en <code>datos_reales/movimientos.csv</code>; no se mezclan con los ficticios.</p></div>`}
