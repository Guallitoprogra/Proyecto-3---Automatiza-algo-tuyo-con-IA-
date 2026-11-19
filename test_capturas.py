import base64
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from decimal import Decimal
from datetime import date
import servidor as s
from lectura_capturas import extraer,fecha_de,leer_base64

class CapturaTests(unittest.TestCase):
    def test_fechas(self):
        r=date(2026,11,17)
        self.assertEqual(fecha_de('Ayer',r),'2026-11-16')
        self.assertEqual(fecha_de('Viernes',r),'2026-11-13')
        self.assertEqual(fecha_de('Tue, Nov 03',r),'2026-11-03')
        self.assertEqual(fecha_de('02-nov',r),'2026-11-02')
        self.assertEqual(fecha_de('sin fecha',r),'')
    def test_no_acepta_otros_archivos(self):
        with self.assertRaises(ValueError):leer_base64({'imagen':base64.b64encode(b'no soy imagen').decode()})
    @unittest.skipUnless((s.BASE/'evidencias'/'ocr'/'pedidos_ocr.json').exists(), 'Requiere las lecturas OCR privadas originales')
    def test_lecturas_capturas_reales(self):
        for caso,n,total in [('pedidos',7,'657.75'),('tarjeta',10,'436.04'),('padel',4,'388.02')]:
            with self.subTest(caso=caso):
                o=json.loads((s.BASE/'evidencias'/'ocr'/(caso+'_ocr.json')).read_text(encoding='utf-8'))
                r,avisos=extraer(o,'2026-11-17')
                self.assertEqual(len(r),n)
                self.assertEqual(sum(Decimal(x['monto']) for x in r),Decimal(total))
                if caso=='padel':
                    self.assertEqual(r[2]['tipo'],'pendiente')
                    self.assertTrue(avisos) # Registro cortado de Q80 no se inventa.
    def test_repetido_ignora_descripcion_ocr(self):
        r=dict(fecha='2026-11-17',comercio='Café Campus',monto='10.00',tipo='compra',descripcion='Texto original',id='D001')
        c=dict(r,comercio='Cafe Campus',descripcion='Texto OCR')
        self.assertEqual(s.repetido(c,[r]),'D001')
    def test_importacion_atomica_y_repetidos(self):
        with tempfile.TemporaryDirectory() as tmp,patch.object(s,'DATOS',Path(tmp)),patch.object(s,'CSV',Path(tmp)/'m.csv'),patch.object(s,'BASE',Path(tmp)):
            s.guardar([])
            row=dict(fecha='2026-11-17',comercio='Ensayo OCR',descripcion='Gasto ficticio',monto='10.00',tarjeta='debito',categoria='Otros',tipo='compra',naturaleza='opcional',confirmada=True)
            bad=dict(row,monto='-1',comercio='Inválido')
            with self.assertRaises(ValueError):s.importar_lote({'filas':[row,bad]})
            self.assertEqual(s.leer(),[])
            result=s.importar_lote({'filas':[row]});self.assertEqual(result['guardados'],1)
            result=s.importar_lote({'filas':[row]});self.assertEqual(result['guardados'],0);self.assertEqual(result['omitidos'],1)

if __name__=='__main__':unittest.main(verbosity=2)
