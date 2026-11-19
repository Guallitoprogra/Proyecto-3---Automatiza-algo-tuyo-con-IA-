"""Aplicación local Python + CSV. Datos de demostración completamente ficticios."""
import csv
import json
import math
import re
import secrets
import threading
import unicodedata
import webbrowser
from collections import Counter, defaultdict
from datetime import date
from decimal import Decimal, InvalidOperation
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

BASE = Path(__file__).resolve().parent
DATOS = BASE / 'datos'
CSV = DATOS / 'movimientos.csv'
PREF = DATOS / 'preferencias.json'
REAL = False
DEMO_CSV = CSV
LOCK = threading.RLock()
TOKEN = secrets.token_urlsafe(32)
CARDS = [dict(id='universidad',nombre='Universidad',ultimos='1042',tipo='Crédito',color='navy'),
         dict(id='personal',nombre='Personal',ultimos='2086',tipo='Crédito',color='green'),
         dict(id='debito',nombre='Débito diario',ultimos='3091',tipo='Débito',color='lavender'),
         dict(id='efectivo',nombre='Efectivo',ultimos='',tipo='Efectivo',color='sand')]
CATS = ['Alimentación','Pedidos de comida','Transporte','Estudios','Deporte','Compras','Entretenimiento','Salud','Otros']
TIPOS = ['compra','pago_tarjeta','transferencia','devolucion','consumo_creditos','devolucion_creditos','pendiente']
CAMPOS = ['id','fecha','comercio','descripcion','monto','tarjeta','categoria','tipo','naturaleza','confirmada','origen']

def monto(v):
    try:n = Decimal(str(v))
    except InvalidOperation:raise ValueError('Escribe un monto válido, por ejemplo 25.50.')
    if not n.is_finite() or n <= 0 or n > Decimal('100000000') or n != n.quantize(Decimal('.01')):
        raise ValueError('El monto debe ser positivo, con máximo dos decimales y menor a Q100,000,000.')
    return f'{n:.2f}'

def guardar(rows):
    DATOS.mkdir(exist_ok=True)
    tmp=CSV.with_suffix('.tmp')
    with tmp.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=CAMPOS); w.writeheader(); w.writerows(rows)
    tmp.replace(CSV)

def leer():
    with CSV.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

def preferencias():
    return json.loads(PREF.read_text(encoding='utf-8'))

def guardar_pref(p):
    tmp=PREF.with_suffix('.tmp'); tmp.write_text(json.dumps(p,ensure_ascii=False,indent=2),encoding='utf-8'); tmp.replace(PREF)

def iniciar_datos():
    DATOS.mkdir(exist_ok=True)
    if not CSV.exists():
        rows=[]
        def add(fecha,comercio,desc,total,card,cat,naturaleza='opcional',tipo='compra'):
            rows.append(dict(id=f'D{len(rows)+1:04}',fecha=fecha,comercio=comercio,descripcion=desc,
                monto=monto(total),tarjeta=card,categoria=cat,tipo=tipo,naturaleza=naturaleza,
                confirmada='si',origen='ficticio_demostracion'))
        for mes in (9,10,11):
            def f(d):return f'2026-{mes:02}-{d:02}'
            add(f(1),'Universidad','Cuota de materiales',220,'universidad','Estudios','necesario')
            add(f(2),'Librería Campus','Cuadernos y lapiceros',65,'universidad','Estudios','necesario')
            add(f(3),'Farmacia','Medicamento',85,'debito','Salud','necesario')
            add(f(4),'Streaming','Suscripción mensual',59,'personal','Entretenimiento')
            add(f(5),'Supermercado','Compras para almuerzos',180 if mes!=11 else 210,'debito','Alimentación','necesario')
            for dia in (2,5,8,11,14):
                add(f(dia),'Café del Campus','Café y desayuno',18+mes-9,'universidad','Alimentación')
                add(f(dia),'Parqueo Campus','Estacionamiento universitario',12,'efectivo','Transporte','necesario')
            for dia in (3,7,10,15):
                add(f(dia),'Comedor universitario','Almuerzo',32,'debito','Alimentación','necesario')
            for dia in (4,9,13):
                add(f(dia),'Club Pádel','Reserva cancha',80,'personal','Deporte')
            for dia in ((6,12) if mes==9 else (3,6,10,12) if mes==10 else (2,4,6,8,10,12,14,16)):
                add(f(dia),'Pedidos Campus','Pedido comida a domicilio',65 if mes<11 else 72,'personal','Pedidos de comida')
            add(f(6),'Transporte urbano','Viaje a la universidad',35,'debito','Transporte','necesario')
            add(f(11),'Cine','Entrada y snack',85,'personal','Entretenimiento')
            add(f(15),'Banco','Pago de tarjeta',900,'universidad','Otros','no_aplica','pago_tarjeta')
            add(f(16),'Cuenta propia','Transferencia entre cuentas',300,'debito','Otros','no_aplica','transferencia')
            if mes==11:
                add(f(16),'Tienda Pádel','Paletero nuevo',850,'personal','Compras','excepcional')
                add(f(10),'Papelería','Material devuelto',20,'universidad','Estudios','no_aplica','devolucion')
        guardar(rows)
    if not PREF.exists():
        guardar_pref(dict(limites={'2026-09':{'Pedidos de comida':250},'2026-10':{'Pedidos de comida':250},'2026-11':{'Pedidos de comida':400,'Entretenimiento':200}},
                          nota='Límites ficticios de demostración, editables. No son recomendaciones financieras.'))

def palabras(s):
    s=''.join(c for c in unicodedata.normalize('NFKD',s.casefold()) if not unicodedata.combining(c))
    return re.findall('[a-z0-9]+',s)

def clasificar(rows,texto):
    docs=Counter(); words=defaultdict(Counter); vocab=set()
    for r in rows:
        if r['tipo']!='compra' or r['confirmada']!='si':continue
        ts=palabras(r['comercio']+' '+r['descripcion']); cat=r['categoria']
        docs[cat]+=1; words[cat].update(ts); vocab.update(ts)
    ts=[t for t in palabras(texto) if t in vocab]
    if len(docs)<2 or not ts:return dict(categoria='Otros',reconocido=False,explicacion='No reconozco esta descripción. Elige una categoría para enseñarme.')
    scores={c:math.log(n/sum(docs.values()))+sum(math.log((words[c][t]+1)/(sum(words[c].values())+len(vocab))) for t in ts) for c,n in docs.items()}
    orden=sorted(scores,key=scores.get,reverse=True)
    if len(orden)>1 and abs(scores[orden[0]]-scores[orden[1]])<1e-9:
        return dict(categoria='Otros',reconocido=False,explicacion='Hay empate entre categorías. Revisa la clasificación.')
    return dict(categoria=orden[0],reconocido=True,explicacion='Sugerencia basada en descripciones etiquetadas. Puedes corregirla; no es una certeza.')

def datos_publicos():
    ultimo=BASE/'evidencias'/'casos_reales'/'ultima_ejecucion.json'
    return dict(app='mi-bolsillo-universitario',movimientos=leer(),tarjetas=CARDS,categorias=CATS,tipos=TIPOS,preferencias=preferencias(),token=TOKEN,
                alumno='Tus gastos reales' if REAL else 'Alex · Estudiante universitario',fecha_corte='2026-11-17',ficticio=not REAL,
                ejemplos_arranque=len(ejemplos_arranque()),modo='real' if REAL else 'demo',
                casos_ultima=json.loads(ultimo.read_text(encoding='utf-8')) if REAL and ultimo.exists() else None)

def ejemplos_arranque():
    if not REAL or not DEMO_CSV.exists():return []
    with DEMO_CSV.open(encoding='utf-8-sig',newline='') as f:
        return [r for r in csv.DictReader(f) if r['origen'].startswith('ficticio')]

def configurar_reales():
    global REAL,DATOS,CSV,PREF,CARDS,CATS
    REAL=True; DATOS=BASE/'datos_reales'; CSV=DATOS/'movimientos.csv'; PREF=DATOS/'preferencias.json'
    CARDS=[dict(id='tarjeta_a',nombre='Tarjeta A · captura 8',ultimos='',tipo='Tipo sin confirmar',color='navy'),
           dict(id='tarjeta_b',nombre='Tarjeta B · captura 9',ultimos='',tipo='Tipo sin confirmar',color='green'),
           dict(id='sin_identificar',nombre='Medio sin identificar',ultimos='',tipo='Pendiente',color='lavender'),
           dict(id='efectivo',nombre='Efectivo',ultimos='',tipo='Efectivo',color='sand'),
           dict(id='creditos_club',nombre='Créditos del club',ultimos='',tipo='Créditos',color='green')]
    CATS=CATS+['Por revisar']
    if not CSV.exists():
        from importar_reales import importar,FUENTE
        if FUENTE.exists():
            importar(DATOS,CAMPOS)
        else:
            guardar([])
    if not PREF.exists():guardar_pref({'limites':{},'nota':'Sin límites personales definidos. No se inventan presupuestos.'})

def editar(body,rows=None,guardar_cambios=True):
    if rows is None:rows=leer()
    id_=str(body.get('id','')); encontrado=next((r for r in rows if r['id']==id_),None)
    if id_ and not encontrado:raise ValueError('Movimiento no encontrado.')
    if encontrado:
        r=encontrado.copy()
        for key in ['categoria','naturaleza','tipo']:
            if key in body:r[key]=str(body[key])
        r['confirmada']='si'
    else:
        fecha=date.fromisoformat(str(body.get('fecha',''))).isoformat()
        if not str(body.get('comercio','')).strip() or not str(body.get('descripcion','')).strip():raise ValueError('Escribe comercio y descripción.')
        r=dict(id=f"D{max((int(x['id'][1:]) for x in rows),default=0)+1:04}",fecha=fecha,
            comercio=str(body['comercio']).strip()[:120],descripcion=str(body['descripcion']).strip()[:300],
            monto=monto(body.get('monto','')),tarjeta=str(body.get('tarjeta','')),
            categoria=str(body.get('categoria','Otros')),tipo=str(body.get('tipo','compra')),
            naturaleza=str(body.get('naturaleza','sin_confirmar' if REAL else 'opcional')),confirmada='si' if body.get('confirmada') else 'no',origen='real_agregado' if REAL else 'ficticio_agregado')
        if any(all(x[k]==r[k] for k in ['fecha','comercio','descripcion','monto','tarjeta','tipo']) for x in rows):raise ValueError('Ya existe un movimiento idéntico.')
    if r['categoria'] not in CATS:raise ValueError('Categoría inválida.')
    if r['naturaleza'] not in ('necesario','opcional','excepcional','no_aplica','sin_confirmar'):raise ValueError('Naturaleza inválida.')
    if r['tipo'] not in TIPOS or r['tarjeta'] not in [c['id'] for c in CARDS]:raise ValueError('Tarjeta o tipo inválido.')
    if encontrado:rows[rows.index(encontrado)]=r
    else:rows.append(r)
    if guardar_cambios:guardar(rows)
    return r

def repetido(candidato,rows):
    from lectura_capturas import normal
    def comercio(t):return ''.join(c for c in normal(t) if c.isalnum())
    return next((r['id'] for r in rows if r['fecha']==candidato['fecha'] and comercio(r['comercio'])==comercio(candidato['comercio'])
                 and monto(r['monto'])==monto(candidato['monto']) and (r['tipo']==candidato['tipo'] or 'reversal' in normal(candidato.get('descripcion','')))),None)

def importar_lote(body):
    import hashlib
    from datetime import datetime,timezone
    filas=body.get('filas',[])
    if not isinstance(filas,list) or not 1<=len(filas)<=80:raise ValueError('Selecciona entre 1 y 80 movimientos.')
    rows=leer(); guardados=[];omitidos=[]
    for f in filas:
        if not isinstance(f,dict):raise ValueError('Movimiento inválido.')
        copia=dict(f);copia.pop('id',None)
        dup=repetido(copia,rows)
        if dup:omitidos.append(dict(comercio=copia.get('comercio',''),coincide_con=dup));continue
        r=editar(copia,rows,False)
        r['origen']='real_captura_ocr' if REAL else 'ficticio_captura_ocr'
        guardados.append(r.copy())
    # Una fila inválida no produce una importación parcial: escribir solo tras validar todas.
    if guardados:guardar(rows)
    destino=BASE/'evidencias'/'importaciones';destino.mkdir(parents=True,exist_ok=True)
    evidencia=dict(fecha_utc=datetime.now(timezone.utc).isoformat(),modo='real' if REAL else 'demo',
        sha256_imagen=str(body.get('sha256',''))[:64],guardados=guardados,omitidos=omitidos,
        nota='Importación revisada y confirmada mediante la interfaz. No contiene tiempos manuales ni reflexión personal.')
    nombre=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'.json'
    (destino/nombre).write_text(json.dumps(evidencia,ensure_ascii=False,indent=2),encoding='utf-8')
    return dict(guardados=len(guardados),omitidos=len(omitidos),ids=[r['id'] for r in guardados])

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def responder(self,obj,status=200):
        raw=json.dumps(obj,ensure_ascii=False).encode(); self.send_response(status)
        self.send_header('Content-Type','application/json; charset=utf-8'); self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff'); self.end_headers(); self.wfile.write(raw)
    def valido(self):
        return self.headers.get('Host') in (f'127.0.0.1:{self.server.server_port}',f'localhost:{self.server.server_port}')
    def do_GET(self):
        if not self.valido():return self.responder({'error':'Host inválido'},403)
        path=urlparse(self.path).path
        if path=='/api/datos':
            with LOCK:return self.responder(datos_publicos())
        if path=='/api/exportar':
            raw=CSV.read_bytes(); self.send_response(200); self.send_header('Content-Type','text/csv; charset=utf-8')
            self.send_header('Content-Disposition','attachment; filename="'+('gastos_reales.csv' if REAL else 'gastos_ficticios.csv')+'"'); self.end_headers(); self.wfile.write(raw); return
        files={'/':'index.html','/app.js':'app.js','/reales.js':'reales.js','/simple.js':'simple.js','/capturas.js':'capturas.js','/estilos.css':'estilos.css'}
        if path not in files:return self.responder({'error':'No encontrado'},404)
        raw=(BASE/'web'/files[path]).read_bytes(); self.send_response(200)
        self.send_header('Content-Type','text/javascript; charset=utf-8' if path.endswith('.js') else {'/':'text/html; charset=utf-8','/estilos.css':'text/css; charset=utf-8'}[path])
        self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'")
        self.send_header('X-Content-Type-Options','nosniff'); self.end_headers(); self.wfile.write(raw)
    def do_POST(self):
        if not self.valido() or self.headers.get('X-App-Token')!=TOKEN:return self.responder({'error':'Solicitud no autorizada'},403)
        try:
            size=int(self.headers.get('Content-Length','0'))
            if size<0 or size>(12*1024*1024 if self.path=='/api/leer-captura' else 200000):raise ValueError('Solicitud demasiado grande.')
            body=json.loads(self.rfile.read(size))
            if not isinstance(body,dict):raise ValueError('Datos inválidos.')
            if self.path=='/api/leer-captura':
                from lectura_capturas import leer_base64
                salida=leer_base64(body)
                with LOCK:
                    actuales=leer();entrenamiento=ejemplos_arranque()+actuales
                    for f in salida['filas']:
                        sugerencia=clasificar(entrenamiento,f['comercio']+' '+f['descripcion'])
                        f['categoria']=sugerencia['categoria'];f['categoria_reconocida']=sugerencia['reconocido']
                        f['posible_duplicado']=repetido(f,actuales) if f['fecha'] else None
                return self.responder(salida)
            with LOCK:
                if self.path=='/api/cerrar':
                    self.responder({'ok':True}); threading.Thread(target=self.server.shutdown,daemon=True).start(); return
                if self.path=='/api/movimiento':return self.responder(editar(body))
                if self.path=='/api/importar-captura':return self.responder(importar_lote(body))
                if self.path=='/api/clasificar':return self.responder(clasificar(ejemplos_arranque()+leer(),str(body.get('texto',''))[:1000]))
                if self.path=='/api/casos':
                    if not REAL:raise ValueError('Abre el modo de casos reales para ejecutar estas pruebas.')
                    from casos_reales import ejecutar
                    return self.responder(ejecutar(leer(),ejemplos_arranque(),clasificar,BASE/'evidencias'/'casos_reales'))
                if self.path=='/api/limite':
                    mes=str(body.get('mes','')); date.fromisoformat(mes+'-01'); cat=body.get('categoria')
                    if cat not in CATS:raise ValueError('Categoría inválida.')
                    p=preferencias(); lim=p['limites'].setdefault(mes,{})
                    if body.get('eliminar'):lim.pop(cat,None)
                    else:lim[cat]=float(monto(body.get('monto','')))
                    guardar_pref(p); return self.responder({'ok':True})
                return self.responder({'error':'Ruta no encontrada'},404)
        except (ValueError,KeyError,TypeError,InvalidOperation) as e:return self.responder({'error':str(e)},400)
        except OSError:return self.responder({'error':'No se pudo guardar. Cierra el CSV si está abierto en otra aplicación.'},500)
        except __import__('subprocess').TimeoutExpired:return self.responder({'error':'La lectura tardó demasiado. Usa una captura más pequeña.'},408)

def main():
    import argparse
    p=argparse.ArgumentParser(); p.add_argument('--port',type=int,default=8768); p.add_argument('--abrir',action='store_true'); p.add_argument('--reales',action='store_true'); args=p.parse_args()
    if args.reales:configurar_reales()
    else:iniciar_datos()
    try:server=ThreadingHTTPServer(('127.0.0.1',args.port),Handler)
    except OSError:
        # No iniciar procesos duplicados; el lanzador comprueba la identidad antes de abrir.
        raise SystemExit('El puerto está ocupado. Usa el acceso directo o elige otro --port.')
    if args.abrir:threading.Timer(.5,lambda:webbrowser.open(f'http://127.0.0.1:{args.port}')).start()
    print(f'Mi bolsillo universitario: http://127.0.0.1:{args.port}',flush=True)
    server.serve_forever()
    server.server_close()

if __name__=='__main__':main()
