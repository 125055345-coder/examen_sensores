"""Análisis de sensores industriales (datos simulados).

Lee data/sensores_industriales.csv y calcula, a partir del archivo,
los resultados solicitados en el examen. Exporta las lecturas con
alerta de temperatura a resultados/alertas.csv.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # sin ventana: solo guarda archivos PNG
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

UMBRAL_ALERTA_C = 85  # regla didáctica del examen

# Rutas relativas a la carpeta del proyecto (funcionan desde cualquier directorio)
BASE = Path(__file__).resolve().parent
RUTA_CSV = BASE / "data" / "sensores_industriales.csv"
RUTA_ALERTAS = BASE / "resultados" / "alertas.csv"
DIR_GRAFICAS = BASE / "resultados" / "graficas"


def guardar(fig, nombre):
    """Guarda una figura en resultados/graficas/ y la cierra."""
    fig.tight_layout()
    fig.savefig(DIR_GRAFICAS / nombre, dpi=150)
    plt.close(fig)
    print(f"  - {(DIR_GRAFICAS / nombre).relative_to(BASE)}")


def generar_graficas(df_num, alertas_num):
    """Genera las gráficas complementarias (no solicitadas por el examen)."""
    DIR_GRAFICAS.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid")
    orden = sorted(df_num["planta"].unique())

    # 1. Temperatura promedio por planta
    fig, ax = plt.subplots(figsize=(7, 4.5))
    prom = df_num.groupby("planta")["temperatura_c"].mean().reindex(orden)
    sns.barplot(x=prom.index, y=prom.values, ax=ax, color="#4C78A8")
    for i, v in enumerate(prom.values):
        ax.text(i, v + 0.3, f"{v:.2f}", ha="center")
    ax.set_title("Temperatura promedio por planta")
    ax.set_xlabel("Planta")
    ax.set_ylabel("Temperatura (°C)")
    ax.set_ylim(0, prom.max() * 1.15)
    guardar(fig, "01_temperatura_promedio_por_planta.png")

    # 2. Alertas por planta
    fig, ax = plt.subplots(figsize=(7, 4.5))
    cuenta = alertas_num["planta"].value_counts().reindex(orden, fill_value=0)
    sns.barplot(x=cuenta.index, y=cuenta.values, ax=ax, color="#E45756")
    for i, v in enumerate(cuenta.values):
        ax.text(i, v + cuenta.max() * 0.01, str(v), ha="center")
    ax.set_title(f"Alertas de temperatura (> {UMBRAL_ALERTA_C} °C) por planta")
    ax.set_xlabel("Planta")
    ax.set_ylabel("Número de alertas")
    ax.set_ylim(0, cuenta.max() * 1.12)
    guardar(fig, "02_alertas_por_planta.png")

    # 3. Distribución de la temperatura con el umbral
    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.histplot(df_num["temperatura_c"], bins=60, ax=ax, color="#4C78A8")
    ax.axvline(UMBRAL_ALERTA_C, color="#E45756", linestyle="--",
               label=f"Umbral de alerta ({UMBRAL_ALERTA_C} °C)")
    ax.set_title("Distribución de la temperatura")
    ax.set_xlabel("Temperatura (°C)")
    ax.set_ylabel("Número de lecturas")
    ax.legend()
    guardar(fig, "03_distribucion_temperatura.png")

    # 4. Top 10 sensores con más alertas
    fig, ax = plt.subplots(figsize=(8, 4.5))
    top = alertas_num["id_sensor"].value_counts().head(10)
    sns.barplot(x=top.values, y=top.index, ax=ax, color="#F58518")
    ax.set_title("Top 10 sensores con más alertas")
    ax.set_xlabel("Número de alertas")
    ax.set_ylabel("Sensor")
    guardar(fig, "04_top_sensores_con_alertas.png")

    # 5. Porcentaje de lecturas en alerta por hora y planta
    fig, ax = plt.subplots(figsize=(10, 4.5))
    t = df_num.assign(
        hora=pd.to_datetime(df_num["fecha_hora"], format="%d/%m/%y %H:%M")
        .dt.floor("h"),
        alerta=df_num["temperatura_c"] > UMBRAL_ALERTA_C,
    )
    pct = t.groupby(["hora", "planta"])["alerta"].mean().mul(100).reset_index()
    sns.lineplot(data=pct, x="hora", y="alerta", hue="planta",
                 hue_order=orden, ax=ax)
    ax.set_title("Porcentaje de lecturas en alerta por hora")
    ax.set_xlabel("Fecha y hora")
    ax.set_ylabel("% de lecturas con alerta")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m %H:%M"))
    sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1), title="Planta")
    fig.autofmt_xdate()
    guardar(fig, "05_alertas_por_hora.png")


def main():
    # Se lee todo como texto para exportar las alertas con las columnas
    # originales sin cambios de formato; la temperatura se convierte aparte.
    df = pd.read_csv(RUTA_CSV, dtype=str)
    temp = pd.to_numeric(df["temperatura_c"])
    df_num = df.assign(temperatura_c=temp)

    # 1. Registros y sensores distintos
    print("=== 1. Registros y sensores ===")
    print(f"Cantidad de registros: {len(df)}")
    print(f"Sensores distintos: {df['id_sensor'].nunique()}")

    # 2. Temperatura promedio por planta
    print("\n=== 2. Temperatura promedio por planta (°C) ===")
    promedios = df_num.groupby("planta")["temperatura_c"].mean().round(2)
    print(promedios.to_string())

    # 3. Temperatura máxima (se muestran todos los empates)
    print("\n=== 3. Temperatura máxima ===")
    maximo = temp.max()
    filas_max = df[temp == maximo]
    print(f"Temperatura máxima: {maximo} °C")
    for _, fila in filas_max.iterrows():
        print(f"  Sensor: {fila['id_sensor']} | Planta: {fila['planta']} "
              f"| Fecha y hora: {fila['fecha_hora']}")

    # 4. Lecturas con alerta (> 85 °C)
    alertas = df[temp > UMBRAL_ALERTA_C]
    print(f"\n=== 4. Lecturas con temperatura > {UMBRAL_ALERTA_C} °C ===")
    print(f"Total de alertas: {len(alertas)}")

    # 5. Planta con más alertas (se muestran todos los empates)
    print("\n=== 5. Planta con más alertas ===")
    por_planta = alertas["planta"].value_counts()
    print(por_planta.to_string())
    if por_planta.empty:
        print("No hay alertas.")
    else:
        top = por_planta[por_planta == por_planta.max()]
        print(f"Planta(s) con más alertas: {', '.join(top.index)} "
              f"({top.iloc[0]} alertas)")

    # 6. Exportar alertas con las columnas originales
    RUTA_ALERTAS.parent.mkdir(exist_ok=True)
    alertas.to_csv(RUTA_ALERTAS, index=False)
    print("\n=== 6. Exportación ===")
    print(f"{len(alertas)} lecturas guardadas en "
          f"{RUTA_ALERTAS.relative_to(BASE)}")

    # 7. Gráficas complementarias
    print("\n=== 7. Gráficas generadas ===")
    generar_graficas(df_num, df_num[temp > UMBRAL_ALERTA_C])


if __name__ == "__main__":
    main()
