'use strict';
let capturaLeida=null;
window.addEventListener('DOMContentLoaded',()=>{
 const button=document.createElement('button');button.className='primary';button.id='upload-capture';button.textContent='↑ Cargar captura';
 $('#new').className='secondary';$('#new').textContent='＋ Agregar a mano';$('#new').before(button);
 const modal=document.createElement('dialog');modal.id='capture-modal';modal.className='capture-modal';
 modal.innerHTML=`<div class="modal-head"><div><span class="eyebrow">DE LA CAPTURA AL REGISTRO</span><h2>Cargar captura de gastos</h2></div><button class="close" id="close-capture" aria-label="Cerrar captura">×</button></div>
 <p class="subnote" id="capture-mode"></p><form id="capture-read-form"><div class="capture-inputs"><label>Imagen PNG o JPG (máximo 8 MB)<input type="file" id="capture-file" accept="image/png,image/jpeg" required></label><label>Fecha en que tomaste la captura<input type="date" id="capture-date" value="2026-11-17" required></label><label>¿Con qué pagaste?<select id="capture-card"></select></label></div><p class="subnote">La fecha de captura permite interpretar “ayer” y los días de la semana. Si la imagen no muestra el año, se usa el año de esta fecha: revísalo.</p><button class="primary" id="read-capture" style="margin-top:15px">Leer movimientos</button></form>
 <p id="capture-error" class="form-error" role="alert"></p><div id="capture-preview"></div>`;
 document.body.append(modal);
 button.addEventListener('click',()=>{capturaLeida=null;$('#capture-preview').innerHTML='';$('#capture-error').textContent='';$('#capture-file').value='';$('#capture-date').value=data.fecha_corte;
  $('#capture-mode').textContent=data.ficticio?'Estás en DEMOSTRACIÓN. Lo que guardes quedará en sus datos de prueba. Para tus gastos personales abre el modo Casos reales.':'Estás en DATOS REALES. La imagen se lee localmente y los movimientos solo se guardan después de tu confirmación.';
  $('#capture-card').innerHTML=data.tarjetas.map(c=>option(c.id,c.nombre,c.id===(card==='todas'?(data.ficticio?'universidad':'sin_identificar'):card))).join('');modal.showModal()});
 $('#close-capture').addEventListener('click',()=>modal.close());
 $('#capture-read-form').addEventListener('submit',async e=>{e.preventDefault();const file=$('#capture-file').files[0];if(!file)return;
  if(file.size>8*1024*1024){$('#capture-error').textContent='La imagen supera los 8 MB.';return}
  const b=$('#read-capture');b.disabled=true;b.textContent='Leyendo la imagen…';$('#capture-error').textContent='';$('#capture-preview').innerHTML='';
  try{const encoded=await new Promise((resolve,reject)=>{const r=new FileReader();r.onload=()=>resolve(String(r.result).split(',')[1]);r.onerror=()=>reject(Error('No se pudo abrir el archivo.'));r.readAsDataURL(file)});
   capturaLeida=await api('/api/leer-captura',{imagen:encoded,fecha_captura:$('#capture-date').value});mostrarCaptura();
  }catch(err){$('#capture-error').textContent=err.message}finally{b.disabled=false;b.textContent='Leer movimientos'}
 });
});
function mostrarCaptura(){
 const o=capturaLeida;
 $('#capture-preview').innerHTML=`<h3 style="margin:24px 0 8px">${o.filas.length} movimientos detectados · revisa antes de guardar</h3>
 <p class="subnote">Total de importes detectados: <b>${money(sum(o.filas))}</b> (incluye otros tipos de movimiento, no es gasto neto). Compara con la imagen original. Puedes cambiar fecha, comercio, monto, categoría y tipo. Desmarca lo que no quieras guardar. Las sugerencias de IA pueden fallar.</p>
 ${o.advertencias.map(a=>`<p class="capture-warning">${esc(a)}</p>`).join('')}
 <div class="table-wrap"><table class="table capture-table"><thead><tr><th>Guardar</th><th>Fecha</th><th>Comercio y descripción</th><th>Monto Q</th><th>Categoría</th><th>Tipo</th></tr></thead><tbody>${o.filas.map((r,i)=>`<tr data-capture-row="${i}"><td><input type="checkbox" name="seleccionar" ${r.posible_duplicado?'':'checked'} aria-label="Seleccionar movimiento ${i+1}"></td><td><input type="date" name="fecha" value="${esc(r.fecha)}" aria-label="Fecha movimiento ${i+1}"></td><td><input name="comercio" value="${esc(r.comercio)}" aria-label="Comercio movimiento ${i+1}"><input name="descripcion" value="${esc(r.descripcion)}" aria-label="Descripción movimiento ${i+1}"><p class="subnote">${r.posible_duplicado?'Posible repetido: '+esc(r.posible_duplicado)+'. Se omitirá si coincide. ':''}${r.notas.map(esc).join(' ')}</p></td><td><input type="number" step=".01" min=".01" name="monto" value="${esc(r.monto)}" aria-label="Monto movimiento ${i+1}"></td><td><select name="categoria" aria-label="Categoría movimiento ${i+1}">${data.categorias.map(c=>option(c,c,c===r.categoria)).join('')}</select><small>${r.categoria_reconocida?'Sugerida por IA':'Revisión necesaria'}</small></td><td><select name="tipo" aria-label="Tipo movimiento ${i+1}">${data.tipos.map(t=>option(t,labels[t]||t,t===r.tipo)).join('')}</select></td></tr>`).join('')}</tbody></table></div>
 <details class="simple-details"><summary>Ver texto leído por Windows</summary><pre class="ocr-text">${esc(o.texto_ocr)}</pre></details>
 ${o.filas.length?'<label class="capture-confirm"><input type="checkbox" id="capture-reviewed"> Revisé fechas, montos, categorías y tipos de los movimientos seleccionados.</label><button class="primary" id="save-capture">Guardar seleccionados</button>':''}`;
 $('#save-capture')?.addEventListener('click',guardarCaptura);
}
async function guardarCaptura(){
 if(!$('#capture-reviewed').checked){$('#capture-error').textContent='Primero revisa la vista previa y marca la confirmación.';return}
 const filas=[];
 for(const tr of document.querySelectorAll('[data-capture-row]')){
  if(!tr.querySelector('[name=seleccionar]').checked)continue;
  const f={};for(const key of ['fecha','comercio','descripcion','monto','categoria','tipo'])f[key]=tr.querySelector(`[name=${key}]`).value;
  const original=capturaLeida.filas[Number(tr.dataset.captureRow)];
  f.tarjeta=$('#capture-card').value;
  if(original.metodo_detectado.toLowerCase()==='cash')f.tarjeta='efectivo';
  if(['consumo_creditos','devolucion_creditos'].includes(f.tipo)&&data.tarjetas.some(c=>c.id==='creditos_club'))f.tarjeta='creditos_club';
  f.confirmada=true;f.naturaleza=data.ficticio?'opcional':'sin_confirmar';
  if(!f.fecha||!f.comercio.trim()||!f.monto){$('#capture-error').textContent='Completa fecha, comercio y monto en todas las filas seleccionadas.';return}
  filas.push(f);
 }
 if(!filas.length){$('#capture-error').textContent='No hay movimientos seleccionados. Los repetidos aparecen desmarcados para evitar duplicarlos.';return}
 const b=$('#save-capture');b.disabled=true;
 try{const o=await api('/api/importar-captura',{filas,sha256:capturaLeida.sha256});await load();refreshMonths();render();$('#capture-modal').close();toast(`${o.guardados} movimientos guardados · ${o.omitidos} repetidos omitidos`)}
 catch(err){$('#capture-error').textContent=err.message}finally{b.disabled=false}
}
