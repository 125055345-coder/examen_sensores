# Informe — Aplicación al caso de Big Data

**Examen práctico:** Manejo Masivo de Datos — Primer parcial
**Nombre:** Christopher Ian Martínez Olmedo
**Carrera:** Ingeniería en Datos e Inteligencia Artificial
**Grupo:** IDIA222

> Los datos de `sensores_industriales.csv` son **simulados** y el umbral de 85 °C es una regla didáctica del examen. Todos los valores citados provienen de la ejecución de `analisis.py` (secciones 1 a 8 de su salida).

## Resultados del análisis que se usan en este informe

| Dato | Valor |
|---|---|
| Registros / sensores distintos | 100,000 / 40 (10 sensores por planta) |
| Periodo | 01/09/26 00:00 a 02/09/26 17:39 (una lectura por minuto por sensor) |
| Tamaño del archivo | 4.40 MiB |
| Temperatura promedio Planta_1 / 2 / 3 / 4 | 66.62 / 66.53 / 66.77 / 66.67 °C |
| Temperatura máxima | 104.99 °C (4 lecturas empatadas: S023, S019, S014, S030) |
| Lecturas con alerta (> 85 °C) | 6,954 (6.95 % del total) |
| Alertas por planta | Planta_3: 1,777 · Planta_1: 1,737 · Planta_4: 1,732 · Planta_2: 1,708 |
| Valores nulos / `id_registro` duplicados | 0 / 0 |
| Racha máxima de alertas consecutivas en un sensor | 3 lecturas |
| Alertas aisladas (la lectura anterior no fue alerta) | 6,482 de 6,954 (93.2 %) |

---

## 5. Las 5 V aplicadas al proyecto

| V | Relación con el sistema de sensores | Ejemplo concreto | ¿CSV actual o ampliación? |
|---|---|---|---|
| **Volumen** | Cantidad de datos que generan los sensores. El CSV tiene 100,000 registros (4.40 MiB), muy pequeño para un sistema industrial; el volumen crece con el número de sensores y la frecuencia de lectura. | Si se instalaran 5,000 sensores (supuesto) con una lectura por segundo, serían 432 millones de lecturas al día. Con unos 46 bytes por fila, como en el CSV, equivale a unos 20 GB diarios y unos 7 TB al año. | **Futura ampliación.** El CSV solo sirve como referencia de tamaño actual. |
| **Velocidad** | Ritmo al que llegan los datos y tiempo en que deben procesarse. Hoy hay 1 lectura por minuto por sensor; la empresa planea 1 por segundo (60 veces más rápido). | Emitir una alerta a los pocos segundos de recibir una lectura mayor que 85 °C, en lugar de esperar a analizar un archivo. | **Futura ampliación.** El CSV es un histórico ya almacenado; solo se observa en `fecha_hora` que había una lectura por minuto. |
| **Variedad** | Diversidad de formatos y tipos de datos. El CSV tiene un solo formato tabular de 6 columnas. | Fotografías de las máquinas, mensajes JSON de los sensores y reportes de mantenimiento en texto libre, combinados con las lecturas numéricas. | **Futura ampliación.** El CSV no contiene imágenes, JSON ni texto libre. |
| **Veracidad** | Confiabilidad y calidad de los datos: que las lecturas reflejen la realidad. | Una lectura nula, repetida o fuera del rango físico posible por una falla de calibración o de comunicación del sensor, que podría producir una falsa alerta o esconder una real. | **Futura ampliación.** En el CSV no aparecen nulos ni duplicados (0 y 0) y la temperatura va de 45.00 a 104.99 °C, pero al ser datos simulados esto no demuestra que los sensores reales sean confiables. El archivo tampoco incluye una columna con el estado del sensor. |
| **Valor** | Utilidad de los datos para tomar decisiones. | Con 6,954 lecturas en alerta (6.95 %) y Planta_3 como la planta con más alertas (1,777), la empresa puede priorizar qué plantas y sensores revisar primero. El sensor S027 acumula 211 alertas y S028 solo 140. | **CSV actual.** Se obtiene directamente del análisis. Su valor real aumentaría al cruzarlo con fallas y mantenimientos, que no están en el archivo. |

---

## 6. Tipos de datos y procesamiento tradicional

### Clasificación

| Elemento | Tipo | Justificación |
|---|---|---|
| El CSV de sensores | **Estructurado** | Tiene filas y columnas fijas (`id_registro`, `fecha_hora`, `id_sensor`, `planta`, `temperatura_c`, `vibracion_mm_s`), cada columna con un tipo definido, y se puede consultar directamente como tabla. |
| Un mensaje JSON enviado por un sensor | **Semiestructurado** | Tiene etiquetas y campos que lo describen (clave–valor), pero no sigue un esquema tabular rígido: los campos pueden variar o anidarse entre mensajes. |
| Una fotografía de una máquina | **No estructurado** | Es una matriz de píxeles sin campos ni esquema; para extraer información (por ejemplo, detectar una fuga) hace falta visión por computadora. |
| El texto libre de un reporte de mantenimiento | **No estructurado** | Es lenguaje natural sin formato fijo; para analizarlo se requiere procesamiento de lenguaje natural. |

### ¿Por qué 100,000 registros no convierten al archivo en Big Data?

Big Data no depende solo de cuántas filas hay. Se refiere a datos cuyo volumen, velocidad o variedad **superan lo que las herramientas tradicionales pueden manejar con un solo equipo**. El CSV pesa 4.40 MiB, cabe completo en la memoria de una laptop y `analisis.py` lo procesa en segundos con pandas. Además es un único formato estructurado y es un archivo estático, así que no hay velocidad ni variedad que lo vuelvan complejo. Es un conjunto de datos pequeño aunque tenga muchas filas.

### Limitaciones al aumentar la escala

- **Memoria:** `pandas` carga el archivo completo en RAM. Con cientos de millones de lecturas diarias ya no cabría en un solo equipo.
- **Almacenamiento y archivos:** un CSV crece sin compresión ni índices, y no admite escrituras simultáneas de miles de sensores. Además, GitHub rechaza archivos de más de 100 MB, por lo que este esquema de repositorio dejaría de ser viable.
- **Tiempo de procesamiento:** un script secuencial en una sola máquina tardaría horas o días, y habría que releer todo el archivo cada vez que se quiera un resultado nuevo.
- **Latencia:** analizar un archivo ya guardado no permite alertar a los pocos segundos de una lectura peligrosa.
- **Variedad:** un CSV no puede contener fotografías ni texto libre; harían falta otros tipos de almacenamiento y técnicas de análisis.
- **Calidad y tolerancia a fallas:** con datos reales habría que detectar errores, duplicados y pérdidas de datos, y un solo equipo es un punto único de falla.

---

## 7. Batch y Streaming

**Tipo de procesamiento que realicé: batch (por lotes).** `analisis.py` lee un archivo finito que ya está guardado, lo procesa completo en una sola ejecución y entrega los resultados al final. Los datos no se procesan conforme se generan, y no importa cuánto pasó entre la lectura del sensor y el análisis. Por eso el resultado es útil como análisis histórico, pero no sirve para reaccionar en el momento.

**Alerta pocos segundos después de una lectura > 85 °C: streaming (procesamiento en flujo).** Cada lectura se evaluaría como un evento en cuanto llega, con la regla `temperatura_c > 85`, sin esperar a juntar un archivo. Los sensores publicarían sus mensajes en un sistema de mensajería (por ejemplo Kafka o MQTT) y un motor de flujo (por ejemplo Spark Structured Streaming o Flink) aplicaría la regla y enviaría la notificación al instante. Se justifica porque el valor de la alerta se pierde con el tiempo: avisar horas después ya no permite intervenir a tiempo.

**Resumen al terminar el día: batch programado.** Al cierre de la jornada se procesarían todas las lecturas del día (el mismo tipo de análisis que hace `analisis.py`) con una tarea programada (por ejemplo cron o Airflow). Aquí no se necesita inmediatez: el resumen se lee una vez al día. Procesar el conjunto completo permite calcular promedios, conteos y rankings con mayor eficiencia y sencillez que hacerlo lectura por lectura.

**Relación con el tiempo en que se necesita cada resultado:**

| Resultado | Tiempo necesario | Enfoque |
|---|---|---|
| Alerta por lectura > 85 °C | Segundos | Streaming |
| Resumen diario (promedios, conteo de alertas, planta con más alertas) | Horas (al cierre del día) | Batch |
| Análisis histórico como el de este examen | Sin urgencia | Batch |

Además, en el CSV las alertas son frecuentes (6.95 % de las lecturas) y casi todas aisladas (93.2 %; la racha más larga fue de 3 lecturas). En un sistema en flujo convendría decidir si alertar por cada lectura o solo cuando varias seguidas superen el umbral, para evitar saturar con avisos.

---

## 8. Lambda y Kappa

### Escenario A: arquitectura Lambda

**Elección: Lambda.** La empresa quiere dos rutas distintas: una que recalcule todo el historial por lotes y otra que procese rápidamente las mediciones recientes. Eso es justamente Lambda: una **capa batch** que produce resultados completos y precisos sobre el historial, una **capa de velocidad** que da resultados inmediatos aunque aproximados sobre lo reciente, y una **capa de servicio** que une ambas vistas para las consultas. La capa batch corrige periódicamente lo que la capa de velocidad haya calculado de forma rápida.

```
                    +--------------------------------+
               +--> | Capa batch                     | --+
               |    | (recalcula todo el historial)  |   |
+-----------+  |    +--------------------------------+   |    +------------------+    +----------------+
| Sensores  |--+                                         +--> | Capa de servicio | -> | Consultas,     |
| (lecturas)|  |    +--------------------------------+   |    | (une resultados) |    | alertas y      |
+-----------+  +--> | Capa de velocidad              | --+    +------------------+    | tableros       |
                    | (mediciones recientes, rápido) |                                +----------------+
                    +--------------------------------+
```

**Costo de esta elección:** se mantienen dos rutas de código que deben dar resultados coherentes.

### Escenario B: arquitectura Kappa

**Elección: Kappa.** La empresa quiere **una sola lógica** de procesamiento de eventos y **conservar las mediciones** para volver a procesarlas. Kappa trata todo como un flujo de eventos: los datos se guardan en un registro inmutable y ordenado, una única canalización de streaming los procesa, y para recalcular (por ejemplo, tras cambiar una regla) simplemente se vuelve a leer el registro desde el inicio con la nueva lógica. Así se evita duplicar el código en dos rutas, como exige Lambda.

```
+-----------+    +-----------------------------+    +----------------------------+    +----------------+
| Sensores  | -> | Registro de eventos         | -> | Procesamiento en flujo     | -> | Salidas:       |
| (lecturas)|    | (inmutable, se conserva)    |    | (una sola lógica)          |    | alertas y      |
+-----------+    +-----------------------------+    +----------------------------+    | resúmenes      |
                        ^                                         |                   +----------------+
                        |                                         |
                        +---- se relee desde el inicio <----------+
                              para reprocesar con la lógica nueva
```

**Costo de esta elección:** el registro de eventos debe conservar mucho historial y el reprocesamiento completo puede ser costoso.

---

## 9. Analítica descriptiva, predictiva y prescriptiva

### Descriptiva: ¿qué pasó?

1. **Planta_3 fue la planta con más alertas de temperatura:** 1,777 de las 6,954 alertas (25.6 %), es decir, 7.11 % de sus 25,000 lecturas. Sin embargo, la diferencia con las demás es pequeña: Planta_2 tuvo 1,708 (6.83 %), solo 69 alertas menos. Los promedios de temperatura también son casi iguales (66.53 a 66.77 °C), así que el análisis no muestra que Planta_3 sea claramente más problemática.
2. **La temperatura máxima fue de 104.99 °C y se registró en 4 lecturas:** S023 (Planta_3, 01/09/26 22:23), S019 (Planta_2, 02/09/26 13:11), S014 (Planta_2, 02/09/26 15:23) y S030 (Planta_3, 02/09/26 16:02). Hubo 6,954 lecturas por encima de 85 °C (6.95 % del total).

### Predictiva: ¿qué podría ocurrir?

**Pregunta:** ¿Qué máquinas tienen mayor probabilidad de sobrecalentarse de forma sostenida o de fallar en los próximos 7 días?

**Datos adicionales necesarios**, porque el CSV no los contiene:

- Registro de **fallas y paros** (fecha, tipo y máquina afectada), que serían la variable a predecir. El CSV no tiene ninguna.
- La relación entre `id_sensor` y la **máquina** que monitorea, pues el CSV solo identifica sensores.
- **Historial de mantenimiento** (reparaciones, cambios de piezas) y datos de la máquina (modelo, antigüedad).
- **Condiciones de operación:** carga de trabajo, horas de uso y temperatura ambiente.
- Un periodo **mucho más largo** que los dos días del CSV, para que existan suficientes fallas con las cuales entrenar y validar un modelo.

Con los datos actuales no sería válido afirmar que una máquina va a fallar. En el CSV, además, la vibración casi no varía con la temperatura (correlación de 0.001), por lo que por sí sola no aporta pistas.

### Prescriptiva: ¿qué hacer?

**Acción propuesta:** si un modelo o una regla prevé riesgo de sobrecalentamiento en una máquina, **programar una inspección preventiva en la siguiente ventana de mantenimiento** (o reducir su carga temporalmente) en lugar de detenerla de inmediato.

**Información que revisaría antes de decidir:**

- **Persistencia de la alerta:** si fue una lectura aislada o varias consecutivas. En el CSV, el 93.2 % de las alertas fueron aisladas y la racha máxima fue de 3 lecturas, así que un solo valor alto no basta para actuar.
- **Estado del sensor:** descartar una falla de calibración o una lectura errónea antes de intervenir la máquina.
- **Otras variables de la máquina:** vibración, carga de trabajo y temperatura ambiente.
- **Historial de mantenimiento y fallas previas** de esa máquina.
- **Criticidad:** qué tanto afecta a la producción que esa máquina se detenga.
- **Costo y disponibilidad:** comparar el costo de un paro no planeado contra el de la inspección, y verificar que haya técnicos y refacciones disponibles.

> Una lectura por encima de 85 °C es una alerta del ejercicio; por sí sola no demuestra que una máquina vaya a fallar.
