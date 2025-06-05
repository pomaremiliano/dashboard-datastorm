import streamlit as st
import pandas as pd
import plotly.express as px

# --- Cargar datos completos solo una vez ---
df_cluster = pd.read_csv("data/df_maestra_cluster.csv")
df_bottomrutas = pd.read_csv("data/bottom10_rutas_cpk.csv")
df_toprutas = pd.read_csv("data/top10_rutas_cpk.csv")

# --- Cargar sólo top y bottom 10 unidades en CPK ---
df_unidades = pd.read_csv("data/df_gastos_unidad.csv")

top10_cpk = df_unidades.nlargest(10, "CPK").copy()
bottom10_cpk = df_unidades.nsmallest(10, "CPK").copy()
subset_df = pd.concat([top10_cpk, bottom10_cpk])

# --- Página general ---
st.set_page_config(page_title="Dashboard CPK Optimizado", layout="wide")
st.title("Dashboard CPK TDR")
st.subheader("DataStorm")

# --- Métricas generales ---
st.markdown("### CPK Promedio General")
col1, col2 = st.columns(2)
with col1:
    st.metric("CPK Promedio (Cluster)", f"{df_cluster['CPK'].mean():.2f}")
with col2:
    st.metric("CPK Promedio (Top/Bottom 10 Unidades)", f"{subset_df['CPK'].mean():.2f}")


ef_stats = (
    df_unidades.groupby("Unidad")["Eficiencia (km/l)"]
    .agg(Mayor="max", Promedio="mean", Menor="min")
    .nlargest(10, "Promedio")  # Top 10 con mejor eficiencia promedio
    .reset_index()
)

df_long = ef_stats.melt(id_vars="Unidad", var_name="Tipo", value_name="Eficiencia")

fig = px.bar(
    df_long,
    x="Unidad",
    y="Eficiencia",
    color="Tipo",
    barmode="group",
    color_discrete_map={
        "Mayor": "#6CA0DC",  # Azul
        "Promedio": "#888888",  # Gris
        "Menor": "#EEEEEE",  # Blanco/ligero
    },
    title="Top 10 Unidades Más Eficientes (Mayor, Promedio y Menor)",
)

fig.update_layout(
    plot_bgcolor="black",
    paper_bgcolor="black",
    font_color="white",
    title_font_size=18,
    legend_title_text="Eficiencia",
)

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
)
st.plotly_chart(fig_bar, use_container_width=True)

# --- Filtros limitados solo a top/bottom 10 ---
st.markdown("### Tabla Interactiva (Top y Bottom 10 Unidades)")
unidad_opciones = sorted(subset_df["Unidad"].unique())
unidad_sel = st.selectbox("Selecciona una unidad", ["Todas"] + unidad_opciones)
orden = st.radio("Ordenar por CPK", ["Ascendente", "Descendente"], horizontal=True)

df_tabla = subset_df.copy()
if unidad_sel != "Todas":
    df_tabla = df_tabla[df_tabla["Unidad"] == unidad_sel]
df_tabla = df_tabla.sort_values(by="CPK", ascending=(orden == "Ascendente"))

st.dataframe(
    df_tabla[
        [
            "Unidad",
            "CPK",
            "Kms Totales",
            "Litros",
            "Eficiencia (km/l)",
            "Gasto Combustible",
            "Gasto Mantenimiento",
        ]
    ],
    use_container_width=True,
)

"""# --- Gráfico de CPK mensual en mantenimiento ---
if "Mes" in df_mantto.columns and "CPK" in df_mantto.columns:
    st.markdown("### CPK de Mantenimiento por Mes")
    df_cpk_mes = df_mantto[["Mes", "CPK"]].dropna()
    cpk_prom_mes = df_cpk_mes.groupby("Mes")["CPK"].mean().reset_index()
    fig_mantto = px.bar(
        cpk_prom_mes, x="Mes", y="CPK", title="CPK Mensual en Mantenimiento"
    )
    st.plotly_chart(fig_mantto, use_container_width=True)
"""

# --- Top y Bottom 10 rutas por CPK ---

st.markdown("### Top y Bottom 10 Rutas por CPK")
top10_rutas = df_toprutas.groupby("Ruta")["CPK"].mean().nlargest(10).reset_index()
bottom10_rutas = df_bottomrutas.groupby("Ruta")["CPK"].mean().nsmallest(10).reset_index()
rutas_cpk = pd.concat(
    [top10_rutas.assign(Tipo="Top 10"), bottom10_rutas.assign(Tipo="Bottom 10")]
)

fig_rutas = px.bar(
    rutas_cpk,
    x="Ruta",
    y="CPK",
    color="Tipo",
    barmode="group",
    title="Top y Bottom 10 Rutas por CPK",
    color_discrete_map={"Top 10": "#FF5733", "Bottom 10": "#3498DB"},
)
st.plotly_chart(fig_rutas, use_container_width=True)
