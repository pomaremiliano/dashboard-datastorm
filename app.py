import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuración general ---
st.set_page_config(page_title="Dashboard CPK", layout="wide")
col_logo, col_title = st.columns([0.15, 0.85])
with col_logo:
    st.image("assets/logo_datastorm_sinfondo.png", width=120)
with col_title:
    st.title("Dashboard CPK - Proyecto TDR")

# --- Carga de datos ---
df_eficiencia_completa = pd.read_csv("data/eficiencia_completa_por_tracto.csv")
df_cluster = pd.read_csv("data/df_maestra_cluster.csv")
df_rutas = pd.read_csv("data/tabla_rutas_unidad.csv")
df_gastos = pd.read_csv("data/df_gastos_unidad.csv")
df_unidadesxruta = pd.read_csv("data/tabla_unidades_por_ruta.csv")
df_viajesunidadruta = pd.read_csv("data/viajes_unidad_ruta.csv")
df_toprutasmes = pd.read_csv("data/top_rutas_mes.csv")
top10rutaseficientes = pd.read_csv("data/top10_rutas_eficientes.csv")
top10rutasmeneeficientes = pd.read_csv("data/top10_rutas_menos_eficientes.csv")

# --- Colores personalizados ---
PALETTE = ["#0c232c", "#c0c0c1", "#046dbf", "#6c7882", "#758c96"]
COLOR_MAP = {
    "Mayor": PALETTE[0],
    "Promedio": PALETTE[1],
    "Menor": PALETTE[2],
    "Top 10": PALETTE[2],
    "Bottom 10": PALETTE[0],
}

# --- Subset para unidades ---
top10_cpk = df_gastos.copy()
bottom10_cpk = df_gastos.copy()
subset_df = pd.concat([top10_cpk, bottom10_cpk])

# --- Tabs ---
tabs = st.tabs(
    [
        "Resumen General",
        "Eficiencia de Combustible",
        "Unidades Críticas",
        "Rutas Críticas",
        "Rutas por Mes",
        "Unidades por Ruta",
        "Top 10 Rutas Más Eficientes/Ineficientes",
        "Calculadora de CPK",
    ]
)

# TAB 1
with tabs[0]:
    st.header("Resumen General de CPK")
    st.write(
        "Este tablero presenta un análisis integral del Costo por Kilómetro (CPK). En este caso, el CPK se define como CPK = (Combustible + Mantenimiento + Peajes) / Kilómetros Recorridos"
    )
    st.metric("CPK Promedio General", f"{df_cluster['CPK'].mean():.2f}")
    # Mostrar las 4 tablas en un layout de matriz 2x2
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top 10 Unidades con Mayor CPK")
        top10_unidades_mayor_cpk = df_gastos[df_gastos["CPK"] > 0].nlargest(10, "CPK")
        st.dataframe(top10_unidades_mayor_cpk[["Unidad", "CPK"]], use_container_width=True)

        st.subheader("Top 10 Rutas con Mayor CPK")
        top10_rutas_mayor_cpk = (
            df_rutas[df_rutas["CPK_Ruta"] > 0]
            .groupby("Ruta")["CPK_Ruta"]
            .mean()
            .nlargest(10)
            .reset_index()
        )
        st.dataframe(top10_rutas_mayor_cpk, use_container_width=True)

    with col2:
        st.subheader("Top 10 Unidades con Menor CPK")
        top10_unidades_menor_cpk = df_gastos[df_gastos["CPK"] > 0].nsmallest(10, "CPK")
        st.dataframe(top10_unidades_menor_cpk[["Unidad", "CPK"]], use_container_width=True)

        st.subheader("Top 10 Rutas con Menor CPK")
        top10_rutas_menor_cpk = (
            df_rutas[df_rutas["CPK_Ruta"] > 0]
            .groupby("Ruta")["CPK_Ruta"]
            .mean()
            .nsmallest(10)
            .reset_index()
        )
        st.dataframe(top10_rutas_menor_cpk, use_container_width=True)

# TAB 2
with tabs[1]:
    st.header("Eficiencia de Combustible por Unidad")
    st.write(
        "Las unidades con mejor eficiencia de combustible contribuyen significativamente a mantener el CPK bajo."
    )

    df_eficiencia = df_eficiencia_completa.rename(
        columns={
            "Tracto": "Unidad",
            "Eficiencia Min (km/l)": "Menor",
            "Eficiencia Media (km/l)": "Promedio",
            "Eficiencia Max (km/l)": "Mayor",
        }
    )
    top10 = df_eficiencia.nlargest(10, "Mayor").copy()
    ef_stats_long = top10.melt(
        id_vars="Unidad",
        value_vars=["Mayor", "Promedio", "Menor"],
        var_name="Tipo",
        value_name="Eficiencia",
    )
    ef_stats_long["Eficiencia"] = pd.to_numeric(
        ef_stats_long["Eficiencia"], errors="coerce"
    )
    ef_stats_long = ef_stats_long[ef_stats_long["Eficiencia"] > 0]

    fig = px.bar(
        ef_stats_long,
        x="Tipo",
        y="Eficiencia",
        color="Tipo",
        facet_col="Unidad",
        barmode="group",
        category_orders={"Tipo": ["Menor", "Promedio", "Mayor"]},
        color_discrete_map=COLOR_MAP,
        title="Eficiencia de Combustible por Unidad (km/L)",
        labels={"Eficiencia": "km por litro"},
    )
    st.plotly_chart(fig, use_container_width=True)

# TAB 3
with tabs[2]:
    st.header("Comparativa de Top y Bottom 10 Unidades (CPK)")
    st.write("Comparativa directa de las unidades más eficientes y las más costosas.")
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

# TAB 4
with tabs[3]:
    st.header("Top y Bottom 10 Rutas por CPK")
    st.write(
        "Identificación de las rutas críticas donde se concentran los mayores costos."
    )
    df_rutas_filtrado = df_rutas[df_rutas["CPK_Ruta"] > 0]
    df_top10_rutas = (
        df_rutas_filtrado.groupby("Ruta")["CPK_Ruta"].mean().nlargest(10).reset_index()
    )
    df_bottom10_rutas = (
        df_rutas_filtrado.groupby("Ruta")["CPK_Ruta"].mean().nsmallest(10).reset_index()
    )
    rutas_cpk = pd.concat(
        [
            df_top10_rutas.assign(Tipo="Top 10"),
            df_bottom10_rutas.assign(Tipo="Bottom 10"),
        ]
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

# TAB 5
with tabs[4]:
    st.header("Top 3 Rutas con Más Viajes por Mes")
    st.write("Distribución mensual de las rutas más frecuentadas.")
    df_toprutasmes = df_toprutasmes.dropna(subset=["Mes", "Ruta", "Cantidad de viajes"])
    df_toprutasmes["Mes"] = df_toprutasmes["Mes"].astype(int)
    top3_rutas = (
        df_toprutasmes.sort_values(
            ["Mes", "Cantidad de viajes"], ascending=[True, False]
        )
        .groupby("Mes")
        .head(3)
    )
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
    todos_meses = pd.DataFrame({"Mes": list(range(1, 13)), "MesNombre": meses_es})
    top3_rutas = todos_meses.merge(top3_rutas, on=["Mes", "MesNombre"], how="left")
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

    st.header("Viajes por Unidad y Ruta")
    st.write("Total de viajes realizados por cada unidad en las rutas.")
    st.dataframe(df_viajesunidadruta, use_container_width=True)

# TAB 7
with tabs[5]:
    st.header("Unidades por Ruta")
    st.write("Relación de unidades asignadas por ruta.")
    st.dataframe(df_unidadesxruta, use_container_width=True)

# TAB 8
with tabs[6]:
    st.header("Top 10 Rutas Más Eficientes/Ineficientes")
    st.write("Rutas que presentan el mejor desempeño de CPK.")
    st.dataframe(top10rutaseficientes, use_container_width=True)

    st.header("Top 10 Rutas Más Ineficientes")
    st.write("Rutas donde se concentran las mayores oportunidades de optimización.")
    st.dataframe(top10rutasmeneeficientes, use_container_width=True)

# TAB 9
with tabs[7]:
    st.header("Simulador de CPK por Combinación Operativa")
    st.write(
        "Permite simular el CPK esperado según la combinación de Proyecto, Tipo de Ruta y Tipo de Unidad."
    )
    proyectos = (
        sorted(df_cluster["Proyecto"].dropna().unique())
        if "Proyecto" in df_cluster.columns
        else []
    )
    tipos_ruta = (
        sorted(df_cluster["TipoRuta"].dropna().unique())
        if "TipoRuta" in df_cluster.columns
        else []
    )
    tipos_unidad = (
        sorted(df_cluster["TipoUnidad"].dropna().unique())
        if "TipoUnidad" in df_cluster.columns
        else []
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        proyecto_sel = st.selectbox("Proyecto", ["Todos"] + proyectos)
    with col2:
        tipo_ruta_sel = st.selectbox("Tipo de Ruta", ["Todos"] + tipos_ruta)
    with col3:
        tipo_unidad_sel = st.selectbox("Tipo de Unidad", ["Todos"] + tipos_unidad)

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
        st.dataframe(
            df_sim[["Proyecto", "TipoRuta", "TipoUnidad", "CPK"]],
            use_container_width=True,
        )
    else:
        st.warning("No hay datos para la combinación seleccionada.")
