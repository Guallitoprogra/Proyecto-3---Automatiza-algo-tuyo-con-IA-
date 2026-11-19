"""OCR local y extracción revisable para historiales de pedidos, tarjetas y pádel."""
import base64
import hashlib
import json
import re
import subprocess
import tempfile
import unicodedata
from datetime import date,timedelta
from pathlib import Path
from time import perf_counter

BASE=Path(__file__).resolve().parent
PRECIO=re.compile(r'(?:GTQ|Q)\s*([0-9][0-9,]*(?:\.[0-9]{2}))(?![0-9])',re.I)
MESES={'ene':1,'jan':1,'feb':2,'mar':3,'abr':4,'apr':4,'may':5,'jun':6,'jul':7,'ago':8,'aug':8,'sep':9,'set':9,'oct':10,'nov':11,'dic':12,'dec':12}

def normal(s):return ''.join(c for c in unicodedata.normalize('NFKD',s.casefold()) if not unicodedata.combining(c))

def fecha_de(texto,referencia):
    t=normal(texto)
    m=re.search(r'\b(\d{1,2})/(\d{1,2})/(\d{2,4})\b',t)
    if m:
        d,mes,y=map(int,m.groups());return date(y+2000 if y<100 else y,mes,d).isoformat()
    m=re.search(r'\b(\d{1,2})[-\s]+('+'|'.join(MESES)+r')\b',t)
    if m:return date(referencia.year,MESES[m[2]],int(m[1])).isoformat()
    m=re.search(r'\b('+'|'.join(MESES)+r')\s+(\d{1,2})\b',t)
    if m:return date(referencia.year,MESES[m[1]],int(m[2])).isoformat()
    if re.search(r'\bayer\b',t):return (referencia-timedelta(days=1)).isoformat()
    if re.search(r'\bhoy\b',t):return referencia.isoformat()
    dias=['lunes','martes','miercoles','jueves','viernes','sabado','domingo']
    for i,dia in enumerate(dias):
        if re.search(r'\b'+dia+r'\b',t):return (referencia-timedelta(days=(referencia.weekday()-i)%7)).isoformat()
    return ''

def lineas_visuales(ocr):
    """Ordena por posición: Windows puede devolver las columnas fuera de secuencia."""
    words=[w for l in ocr.get('lines',[]) for w in l.get('words',[])]
    grupos=[]
    for w in sorted(words,key=lambda w:(w['y']+w['h']/2,w['x'])):
        centro=w['y']+w['h']/2
        grupo=next((g for g in reversed(grupos[-3:]) if abs(g['y']-centro)<max(7,min(w['h'],g['h'])*.55)),None)
        if grupo is None:grupos.append(dict(y=centro,h=w['h'],words=[w]))
        else:grupo['words'].append(w)
    return [dict(text=' '.join(w['text'] for w in sorted(g['words'],key=lambda w:w['x'])),y=g['y'],x=min(w['x'] for w in g['words']),words=g['words']) for g in grupos]

def limpio(t):
    return re.sub(r'\b(?:Volver a pedir|Ver negocio)\b','',t,flags=re.I).strip(' •·.-')

def extraer(ocr,fecha_captura):
    ref=date.fromisoformat(fecha_captura);ls=lineas_visuales(ocr);result=[];advertencias=[];prev=-1
    es_padel=any('historial de pagos' in normal(l['text']) for l in ls)
    es_pedido=any('pedidos anteriores' in normal(l['text']) for l in ls)
    for i,linea in enumerate(ls):
        match=PRECIO.search(linea['text'])
        if not match:continue
        bloque=ls[prev+1:i+1];prev=i
        precio=match[1].replace(',','');texto=linea['text'];merchant='';descripcion='';fecha='';tipo='compra';medio='';notas=[]
        if es_padel:
            txt='\n'.join(l['text'] for l in bloque)
            for l in bloque:
                t=l['text'];n=normal(t)
                if 'fecha de pago' in n:fecha=fecha_de(t,ref)
                if 'descripcion' in n:descripcion=re.split(r'descripci[oó]n',t,flags=re.I)[-1].strip()
                if 'metodo de pago' in n:medio=re.split(r'm[eé]todo de pago',t,flags=re.I)[-1].strip()
            candidatos=[limpio(l['text']) for l in bloque if not re.search(r'factura|descripci|m[eé]todo|fecha de pago|total|historial de pagos|\bBack\b',l['text'],re.I) and not PRECIO.search(l['text']) and not re.match(r'^NT[A-Za-z0-9]+$',l['text']) and l['y']>180]
            if candidatos:merchant=candidatos[0]
            if 'reversal' in normal(descripcion+' '+medio):
                tipo='pendiente';notas.append('Reversal: confirma si devuelve dinero o créditos. Por defecto queda pendiente.')
            elif 'club credits' in normal(medio):tipo='consumo_creditos'
            elif normal(descripcion)=='debit':tipo='pendiente';notas.append('Debit: falta confirmar si es compra, recarga o ajuste.')
        elif es_pedido:
            fecha=fecha_de(texto,ref)
            alineado=next((w['x'] for w in linea['words'] if re.match(r'\d{1,2}-[a-zA-Z]',w['text'])),linea['x'])
            # El comercio aparece sobre la fecha, alineado con ella; ignorar logotipos laterales.
            candidatos=[l for l in bloque[:-1] if abs(l['x']-alineado)<65 and l['y']>230 and not re.search(r'pedidos|articulos|volver|negocio',normal(l['text']))]
            if candidatos:merchant=' '.join(limpio(l['text']) for l in candidatos[-2:] if l['y']>=candidatos[-1]['y']-45)
            desc=[]
            for siguiente in ls[i+1:]:
                if PRECIO.search(siguiente['text']):break
                if siguiente['y']-linea['y']>85:break
                if abs(siguiente['x']-alineado)<65:desc.append(limpio(siguiente['text']))
            descripcion=' '.join(desc)
        else:
            merchant=limpio(texto[:match.start()])
            for siguiente in ls[i+1:]:
                if PRECIO.search(siguiente['text']):break
                if siguiente['y']-linea['y']>140:break
                fecha=fecha_de(siguiente['text'],ref)
                if fecha:break
            descripcion='Movimiento leído de captura de tarjeta'
        if not merchant:
            advertencias.append(f'Importe Q{precio} omitido: el comercio no se ve completo. Revisa el texto OCR.');continue
        if not fecha:notas.append('Fecha no detectada: complétala antes de guardar.')
        if not descripcion:descripcion='Movimiento leído de captura'
        result.append(dict(fecha=fecha,comercio=merchant,descripcion=descripcion,monto=precio,tipo=tipo,metodo_detectado=medio,notas=notas))
    if not result:advertencias.append('No se reconocieron movimientos completos. Prueba una captura más nítida con comercio, fecha e importe visibles.')
    return result,advertencias

def reconocer(path):
    p=subprocess.run(['powershell.exe','-NoProfile','-File',str(BASE/'ocr_windows.ps1'),'-ImagePath',str(Path(path).resolve())],
        capture_output=True,timeout=60,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    if p.returncode:raise ValueError('Windows no pudo leer la imagen. Usa una captura PNG o JPG nítida y de tamaño moderado.')
    try:return json.loads(p.stdout.decode('utf-8-sig'))
    except (ValueError,UnicodeError):raise ValueError('No se pudo interpretar el texto reconocido por Windows.')

def leer_base64(body):
    start=perf_counter()
    try:raw=base64.b64decode(str(body.get('imagen','')),validate=True)
    except ValueError:raise ValueError('Imagen inválida.')
    if not raw or len(raw)>8*1024*1024:raise ValueError('La captura debe pesar como máximo 8 MB.')
    ext='.png' if raw.startswith(b'\x89PNG\r\n\x1a\n') else '.jpg' if raw.startswith(b'\xff\xd8\xff') else ''
    if not ext:raise ValueError('Usa una captura PNG o JPG.')
    with tempfile.TemporaryDirectory(prefix='bolsillo_ocr_') as tmp:
        path=Path(tmp)/('captura'+ext);path.write_bytes(raw);ocr=reconocer(path)
    filas,notas=extraer(ocr,str(body.get('fecha_captura','')))
    return dict(filas=filas,advertencias=notas,texto_ocr=ocr.get('text',''),sha256=hashlib.sha256(raw).hexdigest(),
                motor='Windows OCR local',segundos=round(perf_counter()-start,4))
