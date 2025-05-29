import pandas as pd
from dash import Dash, dash_table, html, dcc, Output, Input, callback_context

# Leer las dos hojas
df1 = pd.read_excel("./data/Rutas_Resumen.xlsx", sheet_name="Rutas")
df2 = pd.read_excel("./data/Rutas_Resumen.xlsx", sheet_name="Rutas_Unidad")
df3 = pd.read_excel("./data/Rutas_Resumen.xlsx", sheet_name="Gastos por Unidad")

app = Dash(__name__)

app.layout = html.Div([
    html.H2("Top 10 Rutas y Rutas por Unidad"),
    html.P("Seleccione una opción para ver la tabla correspondiente:"),
    html.Div([
        html.Button("Rutas", id="btn-rutas", n_clicks=0),
        html.Button("Rutas Unidad", id="btn-rutas-unidad", n_clicks=0),
        html.Button("Gastos por Unidad", id="btn-gastos-unidad", n_clicks=0),
    ]),
    html.Div(id="tabla-container")
])

@app.callback(
    Output("tabla-container", "children"),
    Input("btn-rutas", "n_clicks"),
    Input("btn-rutas-unidad", "n_clicks"),
    Input("btn-gastos-unidad", "n_clicks"),
)
def mostrar_tabla(n_rutas, n_rutas_unidad, n_gastos_unidad):
    ctx = callback_context
    if not ctx.triggered:
        df = df1  # default
    else:
        btn_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if btn_id == "btn-rutas":
            df = df1
        elif btn_id == "btn-rutas-unidad":
            df = df2
        else:
            df = df3  # fallback

    return dash_table.DataTable(
        data=df.to_dict('records'),
        columns=[{"name": col, "id": col} for col in df.columns],
        page_size=10,
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left'}
    )

if __name__ == '__main__':
    app.run(debug=True)
