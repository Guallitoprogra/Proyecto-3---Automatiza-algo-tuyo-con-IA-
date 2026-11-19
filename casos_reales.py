"""Ejecución y evidencia técnica de tres conjuntos reales. No redacta el informe."""
import csv
import hashlib
import json
from datetime import datetime,timezone
from decimal import Decimal
from time import perf_counter

def total(rs):return sum((Decimal(r['monto']) for r in rs),Decimal(0))

def ejecutar(rows,semillas,clasificar,destino):
    inicio=perf_counter(); resultados=[]
    definitions=[
        ('pedidos','Siete pedidos reales de comida',[f'M{i:03}' for i in range(21,28)],
         {'cantidad':7,'compras':'657.75'},'Captura 7. Comparar cada importe y fecha con el historial de pedidos.'),
        ('tarjetas','Dos tarjetas identificadas por su captura',[f'M{i:03}' for i in range(28,48)],
         {'cantidad':20,'tarjeta_a':'436.04','tarjeta_b':'3626.45','compras':'4062.49'},'Capturas 8 y 9. A y B son alias; banco y tipo no confirmados.'),
        ('padel','Pádel: cargos y devoluciones a créditos',[f'M{i:03}' for i in range(1,21)],
         {'cantidad':20,'compras':'588.02','consumo_creditos':'646.67','devolucion_creditos':'760.02','pendiente':'20.00'},
         'Capturas 1, 3, 4, 5 y 6. Captura 2 duplicada excluida. Las devoluciones son créditos del club, confirmado por usuario.')]
    for caso,nombre,ids,esperado,fuente in definitions:
        start=perf_counter(); selected=[r for r in rows if r['id'] in ids]
        observado={'cantidad':len(selected),'compras':f"{total([r for r in selected if r['tipo']=='compra']):.2f}"}
        if caso=='tarjetas':
            for card in ('tarjeta_a','tarjeta_b'):observado[card]=f"{total([r for r in selected if r['tarjeta']==card and r['tipo']=='compra']):.2f}"
        if caso=='padel':
            for tipo in ('consumo_creditos','devolucion_creditos','pendiente'):
                observado[tipo]=f"{total([r for r in selected if r['tipo']==tipo]):.2f}"
        verificaciones=[dict(campo=k,esperado=v,observado=observado.get(k),coincide=observado.get(k)==v) for k,v in esperado.items()]
        # Excluir TODOS los movimientos del caso al evaluar clasificación, evitando evaluar el propio entrenamiento.
        entrenamiento=semillas+[r for r in rows if r['id'] not in ids]
        predicciones=[]
        for r in selected:
            if r['tipo']!='compra':continue
            p=clasificar(entrenamiento,r['comercio']+' '+r['descripcion'])
            predicciones.append(dict(id=r['id'],comercio=r['comercio'],descripcion=r['descripcion'],
                categoria_sugerida=p['categoria'],reconocido=p['reconocido'],explicacion=p['explicacion'],
                categoria_importada=r['categoria'],etiqueta_confirmada=r['confirmada']=='si',
                coincide_con_categoria_importada=p['categoria']==r['categoria'],
                observacion_usuario=''))
        resultados.append(dict(id=caso,nombre=nombre,fuente=fuente,ids=ids,
             verificaciones=verificaciones,calculos_correctos=all(v['coincide'] for v in verificaciones),
             predicciones=predicciones,tiempo_maquina_segundos=round(perf_counter()-start,6),
             tiempo_manual_segundos=None,tiempo_revision_segundos=None,observacion_usuario=''))
    evidencia=dict(fecha_utc=datetime.now(timezone.utc).isoformat(),
        sha256_entrada=hashlib.sha256(json.dumps(rows,sort_keys=True,ensure_ascii=False).encode()).hexdigest(),
        datos_reales=True,resultados=resultados,tiempo_maquina_total_segundos=round(perf_counter()-inicio,6),
        notas=['Son comprobaciones técnicas sobre gastos reales transcritos; contrasta las capturas antes de escribir tus observaciones.',
               'Los esperados numéricos fueron fijados antes de ejecutar. Las categorías importadas no confirmadas no son verdad de referencia.',
               'No se informa exactitud: las sugerencias deben ser revisadas por el usuario. Cada caso se excluyó del entrenamiento de su propia evaluación.',
               'La muestra de pádel no permite calcular saldo del club ni gasto neto conciliado. No se emparejan reversiones automáticamente.',
               'Los tiempos de máquina excluyen transcripción, configuración, revisión humana y tarea manual. No demuestran ahorro de tiempo.'])
    destino.mkdir(parents=True,exist_ok=True)
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    (destino/f'ejecucion_{stamp}.json').write_text(json.dumps(evidencia,ensure_ascii=False,indent=2),encoding='utf-8')
    (destino/'ultima_ejecucion.json').write_text(json.dumps(evidencia,ensure_ascii=False,indent=2),encoding='utf-8')
    campos=['caso','campo','esperado','observado','coincide']
    with (destino/'resultados_calculos.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=campos);w.writeheader()
        for r in resultados:
            for check in r['verificaciones']:w.writerow(dict(caso=r['id'],**check))
    if not (destino/'observaciones_usuario.csv').exists():
        with (destino/'observaciones_usuario.csv').open('w',newline='',encoding='utf-8-sig') as f:
            w=csv.DictWriter(f,fieldnames=['caso','observacion_propia','errores_observados','explicacion_propia','tiempo_manual_segundos','tiempo_revision_segundos','tiempo_configuracion_segundos'])
            w.writeheader()
            for r in resultados:w.writerow({'caso':r['id']})
    with (destino/'sugerencias_clasificador.csv').open('w',newline='',encoding='utf-8-sig') as f:
        fields=['caso','id','comercio','descripcion','categoria_sugerida','reconocido','categoria_importada','etiqueta_confirmada','coincide_con_categoria_importada','explicacion','observacion_usuario']
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for c in resultados:
            for p in c['predicciones']:w.writerow(dict(caso=c['id'],**p))
    return evidencia
