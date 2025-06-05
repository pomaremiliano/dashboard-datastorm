import pandas as pd
import streamlit as st

# Leer las dos hojas
df1 = pd.read_excel("./data/Rutas_Resumen.xlsx", sheet_name="Top 10 Rutas Mas Eficientes")
df2 = pd.read_excel("./data/Rutas_Resumen.xlsx", sheet_name="Top 10 Rutas Menos Eficientes")
df3 = pd.read_excel("./data/Rutas_Resumen.xlsx", sheet_name="Top 10 Unidades Más Eficientes")
df4 = pd.read_excel("./data/Rutas_Resumen.xlsx", sheet_name="Top 10 Unidades Menos Eficientes")

st.set_page_config(page_title="Top 10 Rutas y Unidades Más y Menos Eficientes", layout="wide")

st.markdown(
    """
    <div class="header">
        <h2 class="header-title">Top 10 Rutas y Unidades Más y Menos Eficientes</h2>
        <br>
        <h3 class="header-subtitle">CPK calculado contemplando Costo de combustible y Costo de Mantenimiento entre Kilometros totales recorridos por cada unidad</h3>
        <p class="header-description">Seleccione una opción para ver la tabla correspondiente:</p>
    </div>
    """,
    unsafe_allow_html=True
)

opciones = {
    "Top 10 Rutas Más Eficientes": df1,
    "Top 10 Rutas Menos Eficientes": df2,
    "Top 10 Unidades Más Eficientes": df3,
    "Top 10 Unidades Menos Eficientes": df4,
}

opcion = st.radio(
    "Opciones:",
    list(opciones.keys()),
    horizontal=True
)

df = opciones[opcion]

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)