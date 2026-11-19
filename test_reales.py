import csv
import tempfile
import unittest
from pathlib import Path
from decimal import Decimal
from importar_reales import importar,FUENTE
from casos_reales import ejecutar
import servidor as s

@unittest.skipUnless(FUENTE.exists(), 'Requiere el registro privado original, excluido de la publicación')
class CasosRealesTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.destino=Path(self.tmp.name)
        self.rows=importar(self.destino,s.CAMPOS)
    def tearDown(self):self.tmp.cleanup()
    def test_no_inventa_tarjetas_ni_preferencias(self):
        self.assertEqual(len(self.rows),47)
        self.assertEqual({r['tarjeta'] for r in self.rows if r['origen']=='real_captura_8'},{'tarjeta_a'})
        self.assertEqual({r['tarjeta'] for r in self.rows if r['origen']=='real_captura_9'},{'tarjeta_b'})
        self.assertTrue(all(r['naturaleza']=='sin_confirmar' for r in self.rows if r['tipo']=='compra'))
        self.assertFalse(any(r['origen']=='real_captura_2' for r in self.rows))
    def test_fechas_y_creditos(self):
        self.assertEqual(next(r for r in self.rows if r['id']=='M039')['fecha'],'2026-11-16')
        credits=[r for r in self.rows if r['tipo']=='devolucion_creditos']
        self.assertEqual(sum((Decimal(r['monto']) for r in credits),Decimal(0)),Decimal('760.02'))
        self.assertTrue(all(r['tarjeta']=='creditos_club' for r in credits))
    def test_casos_numericos_y_evidencia(self):
        antes=FUENTE.read_bytes();e=ejecutar(self.rows,[],s.clasificar,self.destino/'evidencia')
        self.assertEqual(len(e['resultados']),3)
        self.assertTrue(all(c['calculos_correctos'] for c in e['resultados']))
        self.assertTrue((self.destino/'evidencia'/'ultima_ejecucion.json').exists())
        self.assertEqual(antes,FUENTE.read_bytes())
        self.assertTrue(all(c['tiempo_manual_segundos'] is None for c in e['resultados']))
    def test_caso_evaluado_no_entra_al_entrenamiento(self):
        consultas=[]
        def clasificador(rows,texto):
            consultas.append({r['id'] for r in rows})
            return dict(categoria='Otros',reconocido=False,explicacion='Ensayo')
        e=ejecutar(self.rows,[],clasificador,self.destino/'evidencia')
        offset=0
        for c in e['resultados']:
            for entrenamiento in consultas[offset:offset+len(c['predicciones'])]:
                self.assertFalse(set(c['ids'])&entrenamiento)
            offset+=len(c['predicciones'])
    def test_no_sobrescribe_correcciones(self):
        with self.assertRaises(ValueError):importar(self.destino,s.CAMPOS)
    def test_marca_diferencias_si_se_cambia_un_importe(self):
        next(r for r in self.rows if r['id']=='M021')['monto']='1.00'
        e=ejecutar(self.rows,[],s.clasificar,self.destino/'evidencia')
        self.assertFalse(e['resultados'][0]['calculos_correctos'])

if __name__=='__main__':unittest.main(verbosity=2)
