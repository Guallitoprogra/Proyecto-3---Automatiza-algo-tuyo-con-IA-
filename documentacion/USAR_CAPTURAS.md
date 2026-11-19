# Registrar gastos desde capturas

1. Abre Mi bolsillo. Para tus compras personales usa el modo de datos reales.
2. Pulsa **Cargar captura**. Elige una imagen PNG o JPG de hasta 8 MB.
3. Indica la fecha en que tomaste la captura y el medio de pago. Esa fecha interpreta expresiones como ayer, viernes o fechas sin año.
4. Pulsa **Leer movimientos**. Windows reconoce el texto localmente; el programa extrae movimientos y el clasificador propone categorías.
5. Revisa la vista previa contra la imagen: fecha, comercio, descripción, monto, categoría y tipo. Puedes editar o desmarcar cada fila. Confirma especialmente Reversal: puede significar devolución de dinero o créditos.
6. Marca que revisaste los datos y pulsa **Guardar seleccionados**. Los movimientos se escriben en CSV y aparecen en Resumen y Movimientos.

Las coincidencias por fecha, comercio normalizado, monto y tipo se consideran posibles repetidos: aparecen desmarcadas y se omiten si coinciden al guardar. No es una deduplicación bancaria perfecta: dos compras distintas de igual importe en un comercio el mismo día pueden coincidir. En ese caso revisa el registro antes de ingresar una compra manualmente. También puede haber repetidos no detectados si el OCR cambia el nombre, el monto o la fecha.

La captura no se conserva como archivo de imagen: se usa un archivo temporal durante la lectura. El texto y los campos de la vista previa solo se guardan como movimientos después de confirmar. La evidencia de importación contiene el hash de la imagen y los movimientos guardados u omitidos en evidencias/importaciones, dentro de esta computadora.

Formatos probados: historial de pedidos, movimientos de tarjetas y el historial de pagos de pádel compartidos en el proyecto. Otros diseños pueden necesitar correcciones o no ser reconocidos. Los movimientos cortados sin comercio visible se omiten con un aviso; una fecha no detectada se deja vacía para que la completes. No se extraen ingresos ni saldos.

## Qué hace cada parte

- Windows OCR reconoce texto en la imagen. Referencia técnica: https://learn.microsoft.com/en-us/uwp/api/windows.media.ocr.ocrengine.recognizeasync
- Las reglas de extracción organizan los textos, fechas, montos y tipos de movimiento.
- Naive Bayes sugiere categorías usando ejemplos etiquetados. Puede equivocarse con comercios desconocidos.
- Tu revisión confirma los datos y las categorías que se incorporan al registro y al aprendizaje.

## Para terminar las pruebas del curso

Repite el flujo completo con tres capturas reales, conservando las correcciones y errores que observes. El registro real ya contiene tus capturas iniciales: volver a cargarlas debe advertir posibles duplicados. Para medir primera importación usa una copia de prueba del programa con el registro vacío; no elimines tus registros reales para ensayar.

Cronometra por separado la tarea manual, la carga automática con revisión y la configuración. Los tiempos de OCR no representan por sí solos ahorro de tiempo. El informe y la reflexión los escribes tú.
