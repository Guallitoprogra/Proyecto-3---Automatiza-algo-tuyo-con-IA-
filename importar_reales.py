"""Importación trazable del CSV revisado previamente. No cambia los datos ficticios."""
import csv
import hashlib
import json
from pathlib import Path

FUENTE=Path(__file__).resolve().parent.parent/'Proyecto-3-Gastos'/'datos'/'movimientos_noviembre_revision.csv'

def importar(destino,campos):
    destino=Path(destino); destino.mkdir(exist_ok=True)
    target=destino/'movimientos.csv'
    if target.exists():raise ValueError('El registro real ya existe; no se sobrescribe.')
    with FUENTE.open(encoding='utf-8-sig',newline='') as f:original=list(csv.DictReader(f))
    cats={'Alimentación':'Alimentación','Alimentación: pedidos':'Pedidos de comida',
          'Transporte: parqueo':'Transporte','Deporte: pádel':'Deporte',
          'Deporte: equipamiento':'Compras','Vehículo: lavado':'Otros','Por confirmar':'Por revisar'}
    tipos={'gasto':'compra','consumo_creditos':'consumo_creditos','devolucion_creditos':'devolucion_creditos','pendiente':'pendiente'}
    result=[]; audit=[]
    for r in original:
        tipo=tipos[r['tipo']]
        card=('tarjeta_a' if r['captura']=='8' else 'tarjeta_b' if r['captura']=='9' else
              'efectivo' if r['metodo']=='Cash' else 'creditos_club' if tipo in ('consumo_creditos','devolucion_creditos') else 'sin_identificar')
        # El comercio desconocido y la naturaleza personal no se adivinan.
        cat=cats.get(r['categoria_confirmada'] or r['categoria_propuesta'],'Por revisar')
        new=dict(id=r['id'],fecha=r['fecha_iso'],comercio=r['comercio'] or 'Comercio no visible',
                 descripcion=r['descripcion'],monto=r['monto_gtq'],tarjeta=card,categoria=cat,tipo=tipo,
                 naturaleza='sin_confirmar' if tipo=='compra' else 'no_aplica',
                 confirmada='si' if r['categoria_confirmada'] else 'no',origen='real_captura_'+r['captura'])
        result.append(new)
        audit.append(dict(id=r['id'],captura=r['captura'],fecha_original=r['fecha_original'],
                          nota=r['revision'],metodo_original=r['metodo'],
                          categoria_original=r['categoria_propuesta'],categoria_confirmada_original=r['categoria_confirmada'],
                          medio_identificado_por='captura' if r['captura'] in ('8','9') else 'método visible o pendiente'))
    assert len(result)==47 and len({r['id'] for r in result})==47
    with target.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=campos);w.writeheader();w.writerows(result)
    (destino/'procedencia.json').write_text(json.dumps(dict(fuente=str(FUENTE),sha256=hashlib.sha256(FUENTE.read_bytes()).hexdigest(),
        descripcion='47 registros transcritos de capturas reales; captura 2 repetida excluida. Categorías no confirmadas son propuestas.',
        movimientos=audit),ensure_ascii=False,indent=2),encoding='utf-8')
    return result
