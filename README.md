# Mi bolsillo universitario

**Rodrigo Ramirez · Carné 23993**  
Proyecto 3: Automatiza algo tuyo con IA

Aplicación local para registrar gastos desde capturas, revisar las sugerencias y consultar movimientos, totales y gráficas. Usa Python, HTML/CSS/JavaScript y archivos CSV. No necesita claves de API ni conexiones bancarias.

## Ejecutar en Windows o Visual Studio Code

Instala Python 3.10 o posterior. Abre esta carpeta en Visual Studio Code y, en **Terminal → Nueva terminal**, ejecuta:

```powershell
python lanzador.py
```

También puedes abrir **Abrir mi bolsillo.cmd**. El lanzador abre el navegador en http://127.0.0.1:8768 y reutiliza el servidor si ya está iniciado. En la primera ejecución se generan los datos ficticios de demostración.

Para un registro personal separado, inicialmente vacío:

```powershell
python lanzador.py --reales
```

Se abre http://127.0.0.1:8769. Los datos se guardan en `datos_reales`; el modo ficticio utiliza `datos`. Ambas carpetas están excluidas de Git. No se incluyen los CSV privados originales ni las lecturas OCR privadas. El importador histórico solo funciona si se aporta localmente el archivo original de `Proyecto-3-Gastos`; no es necesario para empezar un registro nuevo.

Para detener cada servidor:

```powershell
python lanzador.py --cerrar
python lanzador.py --reales --cerrar
```

Cerrar la pestaña no detiene el servidor. Si `python` no está disponible y usas el lanzador de Python de Windows, sustituye `python` por `py -3`.

## Flujo de uso

1. Selecciona **Cargar captura** y una imagen PNG/JPG.
2. Indica fecha de captura y medio de pago.
3. Lee los movimientos y revisa fechas, comercios, importes, categorías y tipos.
4. Confirma las filas y guarda. Las coincidencias detectadas se omiten.
5. Consulta el resumen o exporta el CSV.

La lectura de imágenes utiliza el OCR local de Windows y requiere sus componentes e idiomas OCR instalados. La aplicación y sus cálculos no requieren paquetes Python externos. La captura no se envía a un servicio de IA.

## IA y cálculos

El OCR reconoce texto; reglas extraen campos. Naive Bayes sugiere categorías usando ejemplos y compras confirmadas. Corregir aporta ejemplos para consultas posteriores, sin garantizar precisión. Los totales y gráficas son cálculos del programa. ChatGPT se usó en la exploración y Codex ayudó a desarrollar el código.

Los pagos de tarjeta, transferencias y devoluciones no se suman como compras. Los créditos del club se distinguen de dinero devuelto a una tarjeta. La aplicación no calcula saldos bancarios ni deudas conciliadas.

## Informe y exposición

- [Informe original del estudiante](documentacion/Informe_mi_bolsillo.pdf).
- [Presentación de 10 diapositivas](documentacion/Presentacion_mi_bolsillo.pptx), con notas para exponer.
- [Guion de exposición](documentacion/GUION_EXPOSICION.md), aproximadamente 6 a 8 minutos.
- [Uso sencillo](documentacion/USO_SENCILLO.md) y [uso de capturas](documentacion/USAR_CAPTURAS.md).
- [Resultados agregados del flujo por capturas](evidencias/verificacion_flujo_capturas.json).

El informe declara una comparación personal aproximada de 5 minutos manuales frente a 1 minuto con programa y revisión: 80% menos, sin los 2 minutos de configuración inicial. Solo se reportó un par de mediciones y hubo diferencias de precisión en el registro manual; no es una comparación controlada ni un resultado general.

## Pruebas

```powershell
python -m unittest -v test_aplicacion test_capturas test_reales
```

Las pruebas usan registros temporales. En una copia pública limpia se ejecutan 13 pruebas y se omiten 7 que necesitan el CSV o las lecturas OCR privadas originales. Esas omisiones no prueban el OCR real en otra computadora. Los resultados agregados guardados corresponden a ensayos anteriores, no a una nueva medición de tiempo humano.

## Archivos

`servidor.py`: API local, datos y clasificador. `lectura_capturas.py` y `ocr_windows.ps1`: OCR y extracción. `web/`: interfaz. `lanzador.py`: inicio y cierre. `casos_reales.py` e `importar_reales.py`: comprobaciones e importación históricas opcionales.
