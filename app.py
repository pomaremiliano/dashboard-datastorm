import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt

# --- Cargar datos completos solo una vez ---
df_cluster = pd.read_csv("data/df_maestra_cluster.csv")
df_rutas = pd.read_csv("data/tabla_rutas_unidad.csv")
df_gastos = pd.read_csv("data/df_gastos_unidad.csv")


# --- Filtrar datos para top y bottom 10 rutas ---

top10_cpk = df_gastos.copy()
bottom10_cpk = df_gastos.copy()
subset_df = pd.concat([top10_cpk, bottom10_cpk])

# --- Página general ---
st.set_page_config(page_title="Dashboard CPK Optimizado", layout="wide")
st.title("Dashboard CPK TDR")
st.subheader("DataStorm")

# --- Métricas generales ---
st.markdown("### CPK Promedio General")


st.metric("CPK Promedio", f"{df_cluster['CPK'].mean():.2f}")



ef_stats = (
    df_gastos.groupby("Unidad")["Eficiencia (km/l)"]
    .agg(Mayor="max", Promedio="mean", Menor="min")
    .nlargest(10, "Promedio")  # Top 10 con mejor eficiencia promedio
    .reset_index()
)

ef_stats_long = ef_stats.melt(id_vars="Unidad", value_vars=["Mayor", "Promedio", "Menor"],
                              var_name="Tipo", value_name="Eficiencia")

# Create a grouped bar chart using Altair
chart = alt.Chart(ef_stats_long).mark_bar().encode(
    x=alt.X('Tipo', axis=None),  # Use Tipo for the inner grouping on the x-axis, hide axis labels
    y='Eficiencia',
    color=alt.Color('Tipo', scale=alt.Scale(domain=['Mayor', 'Promedio', 'Menor'],
                                            range=['#7EA6E0', '#9D9C9C', "#000000"])),  # Colores para cada tipo
    tooltip=['Unidad', 'Tipo', 'Eficiencia']
).facet(
    column=alt.Column('Unidad', header=alt.Header(titleOrient="bottom", labelOrient="bottom"))
)

# Show the chart
st.markdown("### Eficiencia por Unidad (Top 10)")
altair_chart = st.altair_chart(chart, use_container_width=True)

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
df_tabla = df_tabla.sort_values(by="CPK", ascending=(orden == "Ascendente")).reset_index(drop=True)
df_tabla.insert(0, "#", df_tabla.index + 1)  # Agrega columna de conteo

st.dataframe(
    df_tabla[
        [
            "#",
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
    color_discrete_map={"Top 10": "#FF5733", "Bottom 10": "#3498DB"},
)
st.plotly_chart(fig_rutas, use_container_width=True)
