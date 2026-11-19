# Guion de exposición · 6 a 8 minutos

Este guion resume el informe entregado por Rodrigo Ramirez. Las notas de PowerPoint amplían cada diapositiva.

1. **Presentación (20 s).** “Mi proyecto se llama Mi bolsillo universitario. Automatiza el registro de gastos a partir de capturas y me permite revisar en qué estoy gastando.”
2. **Problema (35 s).** Explica que usabas dos tarjetas y varias aplicaciones, transcribías gastos y a veces redondeabas o perdías centavos.
3. **Exploración (45 s).** Probaste ChatGPT, Gemini y Claude con los mismos dos prompts: gastos con duplicados y tareas universitarias. El control de gastos era Q150 en cuatro movimientos únicos. Explica tu preferencia personal por ChatGPT y distingue la ayuda de Codex para construir el programa.
4. **Vista principal (30 s).** Señala resumen, movimientos y pruebas. Aclara que la captura muestra datos ficticios.
5. **Flujo (50 s).** Muestra imagen, fecha de captura y tarjeta. Explica que se revisan los campos antes de guardar; una sugerencia no es una confirmación automática.
6. **Componentes (45 s).** OCR de Windows lee texto; reglas extraen campos; Naive Bayes sugiere categorías; Python calcula y guarda en CSV. Una categoría confirmada puede incorporarse al entrenamiento posterior.
7. **Casos reales (50 s).** Pedidos: Q657.75; compras de tarjetas: Q4,062.49; cargos de pádel: Q588.02. Los créditos del club van separados. Son resultados del informe y las comprobaciones históricas, no movimientos recién importados durante la exposición.
8. **Tiempo (45 s).** Reportaste 5 minutos manuales y 1 minuto con revisión y guardado, más 2 minutos iniciales de configuración fuera de la comparación. Aclara que fue una sola medición y que el registro manual tenía diferencias de precisión. El 80% describe esas duraciones, sin demostrar un ahorro general.
9. **Errores (40 s).** Cuenta el ejemplo de comida clasificada como Estudios. Explica que revisas fechas, importes y tipo. Corregir aporta ejemplos pero no elimina todos los errores.
10. **Demostración y cierre (60 s).** Abre la demo, carga una captura de prueba, revisa campos y confirma. Una segunda carga permite mostrar detección de coincidencias. Cierra explicando que reduces transcripción y mantienes la responsabilidad por los datos.

## Preparar la demostración

Abre `Abrir mi bolsillo.cmd` antes de exponer. Usa datos ficticios y una captura de prueba. Si el OCR no está disponible en el equipo del aula, muestra las capturas de las diapositivas y explica la limitación; no presentes imágenes guardadas como una ejecución nueva.

## Preguntas posibles

- **¿Todo es IA?** No. OCR y clasificación son los componentes de reconocimiento y predicción; totales y gráficos usan cálculos y reglas.
- **¿Se conecta al banco?** No; trabaja con imágenes cargadas por la persona y archivos locales.
- **¿Aprende solo?** Utiliza ejemplos y categorías confirmadas; una predicción sin confirmar no se convierte automáticamente en entrenamiento.
- **¿Por qué no publicaste los gastos originales?** La versión pública permite probar el programa sin distribuir los CSV privados; el informe conserva la evidencia que se decidió entregar.
