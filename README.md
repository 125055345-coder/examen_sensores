# Análisis de sensores industriales

Análisis en Python de 100,000 mediciones de temperatura y vibración de sensores instalados en cuatro plantas industriales. Proyecto del examen práctico de **Manejo Masivo de Datos** (primer parcial).

> **Los datos son simulados.** El archivo `data/sensores_industriales.csv` no contiene mediciones reales de ninguna empresa. Se generó con fines didácticos.

## Objetivo

Leer el archivo CSV con Python y calcular, a partir de los datos (sin valores escritos en el código):

- Cantidad de registros y de sensores distintos.
- Temperatura promedio de cada planta.
- Temperatura máxima, con su sensor y fecha (se muestran todos los empates).
- Número de lecturas con **alerta de temperatura** (mayor que 85 °C).
- Planta con más alertas (se muestran todos los empates).
- Exportación de las lecturas en alerta a `resultados/alertas.csv`, conservando las columnas originales.

Además, el programa genera gráficas complementarias en `resultados/graficas/`.

> El umbral de 85 °C es una regla didáctica del examen. Una lectura por encima del umbral es una alerta del ejercicio; por sí sola no demuestra que una máquina vaya a fallar.

## Descripción de los datos

Archivo: `data/sensores_industriales.csv` — 100,000 filas, 40 sensores, 4 plantas, una lectura por minuto por sensor (del 01/09/26 00:00 al 02/09/26 17:39).

| Columna | Significado |
|---|---|
| `id_registro` | Identificador de la medición |
| `fecha_hora` | Fecha y hora de la lectura (formato `dd/mm/aa h:mm`) |
| `id_sensor` | Identificador del sensor |
| `planta` | Planta donde está instalado |
| `temperatura_c` | Temperatura en grados Celsius |
| `vibracion_mm_s` | Vibración en milímetros por segundo |

## Estructura del proyecto

```
.
├── analisis.py              # Programa principal
├── data/
│   └── sensores_industriales.csv
├── resultados/
│   ├── alertas.csv          # Lecturas con temperatura > 85 °C
│   └── graficas/            # Gráficas en PNG
├── evidencias/              # Captura de reproducibilidad
├── informe.md               # Respuestas de la Parte II
├── requirements.txt
└── README.md
```

## Requisitos

- Python 3.11 o superior (probado con Python 3.12).
- Git.
- En Ubuntu/Debian, el paquete `python3-venv`:

```bash
sudo apt update
sudo apt install -y git python3 python3-venv python3-pip
```

## Instalación

```bash
git clone https://github.com/125055345-coder/examen_sensores.git
cd examen_sensores

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

Dependencias (con versiones fijas en `requirements.txt`): `pandas`, `matplotlib` y `seaborn`.

## Ejecución

Con el entorno virtual activado y desde la carpeta del proyecto:

```bash
python analisis.py
```

El programa imprime los resultados en la terminal y guarda:

- `resultados/alertas.csv`
- `resultados/graficas/*.png` (5 gráficas)

Para salir del entorno virtual: `deactivate`.

## Resultados

| Resultado | Valor |
|---|---|
| Registros / sensores distintos | 100,000 / 40 |
| Temperatura promedio Planta_1 / 2 / 3 / 4 | 66.62 / 66.53 / 66.77 / 66.67 °C |
| Temperatura máxima | 104.99 °C (4 lecturas empatadas) |
| Lecturas con alerta (> 85 °C) | 6,954 |
| Planta con más alertas | Planta_3 (1,777) |

Los detalles de cada empate y el análisis de los resultados están en `informe.md`.
