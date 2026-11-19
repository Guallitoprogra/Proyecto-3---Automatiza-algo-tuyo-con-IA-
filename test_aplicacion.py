import json
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request,urlopen
from unittest.mock import patch
import servidor as s

class AppTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.base=Path(self.temp.name)
        self.patches=[patch.object(s,'DATOS',self.base),patch.object(s,'CSV',self.base/'movimientos.csv'),patch.object(s,'PREF',self.base/'preferencias.json')]
        for p in self.patches:p.start()
        s.iniciar_datos()
    def tearDown(self):
        for p in reversed(self.patches):p.stop()
        self.temp.cleanup()
    def test_tres_meses_y_sin_datos_personales(self):
        rs=s.leer(); self.assertEqual({r['fecha'][:7] for r in rs},{'2026-09','2026-10','2026-11'})
        self.assertTrue(all(r['origen']=='ficticio_demostracion' for r in rs))
        self.assertEqual(len({r['id'] for r in rs}),len(rs))
    def test_montos(self):
        for n in ['NaN','Infinity','-1','0','1.123','100000001','hola']:
            with self.assertRaises(ValueError):s.monto(n)
        self.assertEqual(s.monto('10.50'),'10.50')
    def test_no_recrea_datos(self):
        antes=s.CSV.read_bytes(); s.iniciar_datos(); self.assertEqual(antes,s.CSV.read_bytes())
    def test_modelo(self):
        rs=s.leer()
        self.assertEqual(s.clasificar(rs,'Pedidos Campus comida a domicilio')['categoria'],'Pedidos de comida')
        self.assertEqual(s.clasificar(rs,'Parqueo Campus estacionamiento')['categoria'],'Transporte')
        self.assertFalse(s.clasificar(rs,'zzzxxyy')['reconocido'])
    def test_aprende_correccion(self):
        rs=s.leer(); objetivos=[r for r in rs if r['comercio']=='Streaming']
        for r in objetivos:s.editar({'id':r['id'],'categoria':'Otros'})
        self.assertEqual(s.clasificar(s.leer(),'Streaming suscripción mensual')['categoria'],'Otros')
    def nuevo(self):
        return dict(fecha='2026-11-17',comercio='Ensayo ficticio',descripcion='Ensayo de compra',monto='12.50',tarjeta='debito',categoria='Otros',tipo='compra',naturaleza='opcional',confirmada=True)
    def test_alta_y_duplicados(self):
        n=len(s.leer()); r=s.editar(self.nuevo()); self.assertEqual(len(s.leer()),n+1)
        self.assertEqual(s.leer()[-1]['id'],r['id'])
        with self.assertRaises(ValueError):s.editar(self.nuevo())
    def test_validaciones(self):
        for campo,valor in [('fecha','2026-02-30'),('tarjeta','no'),('categoria','no'),('naturaleza','no'),('tipo','no')]:
            body=self.nuevo(); body[campo]=valor
            with self.assertRaises(ValueError):s.editar(body)
    def test_pagos_no_son_compras(self):
        rs=[r for r in s.leer() if r['fecha'].startswith('2026-11')]
        self.assertEqual(sum(1 for r in rs if r['tipo']=='pago_tarjeta'),1)
        self.assertEqual(sum(1 for r in rs if r['tipo']=='transferencia'),1)
        self.assertNotEqual(sum(float(r['monto']) for r in rs),sum(float(r['monto']) for r in rs if r['tipo']=='compra'))
    def test_http_y_proteccion_mutaciones(self):
        server=s.ThreadingHTTPServer(('127.0.0.1',0),s.Handler); t=threading.Thread(target=server.serve_forever,daemon=True);t.start()
        url=f'http://127.0.0.1:{server.server_port}'
        try:
            with urlopen(url+'/api/datos') as r:o=json.load(r)
            self.assertEqual(o['app'],'mi-bolsillo-universitario')
            req=Request(url+'/api/movimiento',data=json.dumps(self.nuevo()).encode(),headers={'Content-Type':'application/json'},method='POST')
            with self.assertRaises(HTTPError) as e:urlopen(req)
            self.assertEqual(e.exception.code,403)
            e.exception.close()
            req.add_header('X-App-Token',o['token'])
            with urlopen(req) as r:self.assertEqual(json.load(r)['monto'],'12.50')
            with urlopen(url+'/') as r:self.assertIn(b'Mi bolsillo',r.read())
        finally:server.shutdown();server.server_close();t.join()

if __name__=='__main__':unittest.main(verbosity=2)
