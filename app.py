import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt

# --- Página general ---
st.set_page_config(page_title="Dashboard CPK Optimizado", layout="wide")
st.title("Dashboard CPK TDR")
st.subheader("DataStorm")

# --- Cargar datos completos solo una vez ---
df_eficiencia_completa = pd.read_csv("data/eficiencia_completa_por_tracto.csv")
df_cluster = pd.read_csv("data/df_maestra_cluster.csv")
df_rutas = pd.read_csv("data/tabla_rutas_unidad.csv")
df_gastos = pd.read_csv("data/df_gastos_unidad.csv")
df_unidadesxruta = pd.read_csv("data/tabla_unidades_por_ruta.csv")
df_viajesunidadruta = pd.read_csv("data/viajes_unidad_ruta.csv")
df_toprutasmes = pd.read_csv("data/top_rutas_mes.csv")
top10rutaseficientes = pd.read_csv("data/top10_rutas_eficientes.csv")
top10rutasmeneeficientes = pd.read_csv("data/top10_rutas_menos_eficientes.csv")
# --- Paleta de colores personalizada ---
PALETTE = ["#f4bc34", "#04345c", "#c0c04c", "#407c4c", "#44344c"]
COLOR_MAP = {
    "Mayor": PALETTE[0],
    "Promedio": PALETTE[1],
    "Menor": PALETTE[2],
    "Top 10": PALETTE[3],
    "Bottom 10": PALETTE[4],
}


# --- Filtrar datos para top y bottom 10 rutas ---

top10_cpk = df_gastos.copy()
bottom10_cpk = df_gastos.copy()
subset_df = pd.concat([top10_cpk, bottom10_cpk])

# --- Métricas generales ---
st.markdown("### CPK Promedio General")

st.metric("CPK Promedio", f"{df_cluster['CPK'].mean():.2f}")

# Renombrar columnas y limpiar datos
df_eficiencia = df_eficiencia_completa.rename(
    columns={
        "Tracto": "Unidad",
        "Eficiencia Min (km/l)": "Menor",
        "Eficiencia Media (km/l)": "Promedio",
        "Eficiencia Max (km/l)": "Mayor",
    }
)

# Seleccionar top 10 por eficiencia máxima
top10 = df_eficiencia.nlargest(10, "Mayor").copy()

# Convertir a formato largo
ef_stats_long = top10.melt(
    id_vars="Unidad",
    value_vars=["Mayor", "Promedio", "Menor"],
    var_name="Tipo",
    value_name="Eficiencia",
)

# Limpiar y asegurar tipos válidos
ef_stats_long["Eficiencia"] = pd.to_numeric(
    ef_stats_long["Eficiencia"], errors="coerce"
)
ef_stats_long = ef_stats_long[ef_stats_long["Eficiencia"] > 0]

# Crear gráfica con Plotly usando COLOR_MAP
fig = px.bar(
    ef_stats_long,
    x="Tipo",
    y="Eficiencia",
    color="Tipo",
    facet_col="Unidad",
    barmode="group",
    category_orders={"Tipo": ["Menor", "Promedio", "Mayor"]},
    color_discrete_map=COLOR_MAP,
    title="Eficiencia de combustible por Unidad (km/L)",
    labels={"Eficiencia": "km por litro"},
)

# Ajustar el layout para mejor legibilidad
fig.update_layout(
    height=500,
    margin=dict(t=50, l=10, r=10, b=50),
    showlegend=(len(ef_stats_long["Unidad"].unique()) <= 10),
)

# Mostrar en Streamlit
st.plotly_chart(fig, use_container_width=True)

# --- Gráfico de barras para top/bottom 10 ---
st.markdown("### Comparativa de Top y Bottom 10 Unidades")
fig_bar = px.bar(
    subset_df.sort_values("CPK", ascending=False),
    x="Unidad",
    y=["CPK", "Litros", "Kms Totales"],
    barmode="group",
    labels={"value": "Valor", "variable": "Indicador"},
    title="CPK, Litros y Kilómetros Totales - Top vs Bottom 10",
    color_discrete_sequence=PALETTE,
)
st.plotly_chart(fig_bar, use_container_width=True)

# --- Filtros limitados solo a top/bottom 10 ---
st.markdown("### Tabla de Unidades")
unidad_opciones = sorted(subset_df["Unidad"].unique())
unidad_sel = st.selectbox("Selecciona una unidad", ["Todas"] + unidad_opciones)

# Agrupa por Unidad y calcula métricas agregadas
df_tabla = (
    subset_df.groupby("Unidad")
    .agg(
        CPK=("CPK", "mean"),
        Kms_Totales=("Kms Totales", "sum"),
        Litros=("Litros", "sum"),
        Eficiencia_km_l=("Eficiencia (km/l)", "mean"),
        Gasto_Combustible=("Gasto Combustible", "sum"),
        Gasto_Mantenimiento=("Gasto Mantenimiento", "sum"),
    )
    .reset_index()
)

if unidad_sel != "Todas":
    df_tabla = df_tabla[df_tabla["Unidad"] == unidad_sel]
df_tabla = df_tabla.sort_values(by="CPK", ascending=False).reset_index(drop=True)
df_tabla.insert(0, "#", df_tabla.index + 1)  # Agrega columna de conteo

st.dataframe(
    df_tabla[
        [
            "#",
            "Unidad",
            "CPK",
            "Kms_Totales",
            "Litros",
            "Eficiencia_km_l",
            "Gasto_Combustible",
            "Gasto_Mantenimiento",
        ]
    ],
    use_container_width=True,
    hide_index=True,
)
# --- Tabla top y bottom 10 rutas ---
st.markdown("### Tabla de Rutas")
ruta_opciones = sorted(df_rutas["Ruta"].unique())
ruta_sel = st.selectbox("Selecciona una ruta", ["Todas"] + ruta_opciones)

df_rutas_tabla = (
    df_rutas.groupby("Ruta")
    .agg(
        CPK_Ruta=("CPK_Ruta", "mean"),
        Cantidad_de_viajes=("Cantidad de viajes", "sum"),
        Litros=("Litros", "sum"),
        Kms_Totales=("kmstotales", "sum"),
    )
    .reset_index()
)
if ruta_sel != "Todas":
    df_rutas_tabla = df_rutas_tabla[df_rutas_tabla["Ruta"] == ruta_sel]
df_rutas_tabla.insert(0, "#", df_rutas_tabla.index + 1)  # Agrega columna de conteo
# Verifica que las columnas existan antes de mostrar
cols_to_show = [
    col
    for col in ["#", "Ruta", "CPK_Ruta", "Cantidad de viajes", "Litros", "Kms_Totales"]
    if col in df_rutas_tabla.columns
]
st.dataframe(
    df_rutas_tabla[cols_to_show],
    use_container_width=True,
    hide_index=True,
)

# --- Top y Bottom 10 rutas por CPK ---

st.markdown("### Top y Bottom 10 Rutas por CPK")
# Filtrar solo rutas cuyo CPK_Ruta es mayor que 0
df_rutas_filtrado = df_rutas[df_rutas["CPK_Ruta"] > 0]

df_top10_rutas = (
    df_rutas_filtrado.groupby("Ruta")["CPK_Ruta"].mean().nlargest(10).reset_index()
)
df_bottom10_rutas = (
    df_rutas_filtrado.groupby("Ruta")["CPK_Ruta"].mean().nsmallest(10).reset_index()
)
rutas_cpk = pd.concat(
    [df_top10_rutas.assign(Tipo="Top 10"), df_bottom10_rutas.assign(Tipo="Bottom 10")]
)

fig_rutas = px.bar(
    rutas_cpk,
    x="Ruta",
    y="CPK_Ruta",
    color="Tipo",
    barmode="group",
    title="Top y Bottom 10 Rutas por CPK",
    color_discrete_map={
        "Top 10": COLOR_MAP["Top 10"],
        "Bottom 10": COLOR_MAP["Bottom 10"],
    },
)
st.plotly_chart(fig_rutas, use_container_width=True)

st.subheader("Top de Rutas por Mes")
st.dataframe(df_toprutasmes, use_container_width=True)

# Asegurar que las columnas clave existen
if "Mes" in df_toprutasmes.columns and "Cantidad de viajes" in df_toprutasmes.columns:

    # Eliminar filas vacías
    df_toprutasmes = df_toprutasmes.dropna(subset=["Mes", "Ruta", "Cantidad de viajes"])
    df_toprutasmes["Mes"] = df_toprutasmes["Mes"].astype(int)

    # Top 3 rutas por mes
    top3_rutas = (
        df_toprutasmes.sort_values(
            ["Mes", "Cantidad de viajes"], ascending=[True, False]
        )
        .groupby("Mes")
        .head(3)
    )

    # Mapeo de nombre de mes
    meses_es = [
        "Enero",
        "Febrero",
        "Marzo",
        "Abril",
        "Mayo",
        "Junio",
        "Julio",
        "Agosto",
        "Septiembre",
        "Octubre",
        "Noviembre",
        "Diciembre",
    ]
    top3_rutas["MesNombre"] = top3_rutas["Mes"].apply(
        lambda x: meses_es[x - 1] if 1 <= x <= 12 else str(x)
    )

    # Asegurar todos los meses existan, aunque con 0 viajes
    todos_meses = pd.DataFrame({"Mes": list(range(1, 13)), "MesNombre": meses_es})
    top3_rutas = todos_meses.merge(top3_rutas, on=["Mes", "MesNombre"], how="left")

    # Gráfico apilado
    fig_top3 = px.bar(
        top3_rutas,
        x="MesNombre",
        y="Cantidad de viajes",
        color="Ruta",
        title="Top 3 Rutas con Más Viajes por Mes",
        labels={"Cantidad de viajes": "Cantidad de Viajes", "MesNombre": "Mes"},
        color_discrete_sequence=PALETTE,
    )

    st.plotly_chart(fig_top3, use_container_width=True)
else:
    st.info(
        "No se encontraron las columnas 'Mes' y 'Cantidad de viajes' en el dataframe."
    )

st.subheader("Viajes por Unidad y Ruta")
st.dataframe(df_viajesunidadruta, use_container_width=True)

# Top 10 combinaciones con más viajes
viajes_top10 = (
    df_viajesunidadruta.groupby("Ruta")["TotalViajesUnidad"]
    .sum()
    .reset_index()
    .sort_values("TotalViajesUnidad", ascending=False)
    .head(10)
)

fig_hist = px.bar(
    viajes_top10,
    x="Ruta",
    y="TotalViajesUnidad",
    title="Top 10 Rutas con Más Viajes por Unidad",
    labels={"Ruta": "Ruta", "TotalViajesUnidad": "Total de Viajes Unidad"},
    color_discrete_sequence=PALETTE,
)

st.plotly_chart(fig_hist, use_container_width=True)

st.subheader("Unidades por Ruta")
st.dataframe(df_unidadesxruta, use_container_width=True)

st.dataframe(top10rutaseficientes, use_container_width=True)
st.dataframe(top10rutasmeneeficientes, use_container_width=True)



st.markdown("## Calculadora de CPK")

# Supón que tienes estas columnas en df_gastos o df_cluster:
# 'Proyecto', 'Tipo de Ruta', 'Tipo de Unidad', 'CPK'

# Selección de filtros
proyectos = sorted(df_cluster["Proyecto"].dropna().unique()) if "Proyecto" in df_cluster.columns else []
tipos_ruta = sorted(df_cluster["TipoRuta"].dropna().unique()) if "TipoRuta" in df_cluster.columns else []
tipos_unidad = sorted(df_cluster["TipoUnidad"].dropna().unique()) if "TipoUnidad" in df_cluster.columns else []

col1, col2, col3 = st.columns(3)
with col1:
    proyecto_sel = st.selectbox("Proyecto", ["Todos"] + proyectos)
with col2:
    tipo_ruta_sel = st.selectbox("Tipo de Ruta", ["Todos"] + tipos_ruta)
with col3:
    tipo_unidad_sel = st.selectbox("Tipo de Unidad", ["Todos"] + tipos_unidad)

# Filtrado dinámico
df_sim = df_cluster.copy()
if proyecto_sel != "Todos":
    df_sim = df_sim[df_sim["Proyecto"] == proyecto_sel]
if tipo_ruta_sel != "Todos":
    df_sim = df_sim[df_sim["TipoRuta"] == tipo_ruta_sel]
if tipo_unidad_sel != "Todos":
    df_sim = df_sim[df_sim["TipoUnidad"] == tipo_unidad_sel]

if not df_sim.empty and "CPK" in df_sim.columns:
    cpk_prom = df_sim["CPK"].mean()
    st.success(f"CPK estimado para la combinación seleccionada: **{cpk_prom:.2f}**")
    st.dataframe(df_sim[["Proyecto", "TipoRuta", "TipoUnidad", "CPK"]], use_container_width=True)
else:
    st.warning("No hay datos para la combinación seleccionada.")