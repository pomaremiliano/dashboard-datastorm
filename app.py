import pandas as pd
from dash import Dash, dash_table, html, dcc, Output, Input, State, callback_context

# Leer las dos hojas
df1 = pd.read_excel("./data/Rutas_Resumen.xlsx", sheet_name="Top 10 Rutas Mas Eficientes")
df2 = pd.read_excel("./data/Rutas_Resumen.xlsx", sheet_name="Top 10 Rutas Menos Eficientes")
df3 = pd.read_excel("./data/Rutas_Resumen.xlsx", sheet_name="Top 10 Unidades Más Eficientes")
df4 = pd.read_excel("./data/Rutas_Resumen.xlsx", sheet_name="Top 10 Unidades Menos Eficientes")

app = Dash(__name__)

button_ids = [
    "btn-top10-eficientes",
    "btn-top10-menos-eficientes",
    "btn-top10-unidades-eficientes",
    "btn-top10-unidades-menos-eficientes"
]

app.layout = html.Div([
    dcc.Store(id='active-button', data='btn-top10-eficientes'),
    html.H2("Top 10 Rutas Unidades Más y Menos Eficientes"),
    html.Br(),
    html.H3("CPK calculado contemplando Costo de combustible y Costo de Mantenimiento entre Kilometros totales recorridos por cada unidad"),
    html.P("Seleccione una opción para ver la tabla correspondiente:"),
    html.Div([
        html.Button("Top 10 Rutas Más Eficientes", id="btn-top10-eficientes", n_clicks=0),
        html.Button("Top 10 Rutas Menos Eficientes", id="btn-top10-menos-eficientes", n_clicks=0),
        html.Button("Top 10 Unidades Más Eficientes", id="btn-top10-unidades-eficientes", n_clicks=0),
        html.Button("Top 10 Unidades Menos Eficientes", id="btn-top10-unidades-menos-eficientes", n_clicks=0),
    ], id="button-group"),
    html.Div(id="tabla-container")
])

@app.callback(
    Output('active-button', 'data'),
    [Input(btn_id, 'n_clicks') for btn_id in button_ids],
    prevent_initial_call=True
)
def update_active_button(*btn_clicks):
    ctx = callback_context
    if not ctx.triggered:
        return dash.no_update
    btn_id = ctx.triggered[0]['prop_id'].split('.')[0]
    return btn_id

@app.callback(
    [Output(btn_id, 'style') for btn_id in button_ids],
    Input('active-button', 'data')
)
def highlight_active_button(active_btn):
    highlight = {'backgroundColor': "#6aee49", 'fontWeight': 'bold'}
    normal = {}
    return [highlight if btn_id == active_btn else normal for btn_id in button_ids]

@app.callback(
    Output("tabla-container", "children"),
    [Input(btn_id, 'n_clicks') for btn_id in button_ids],
    State('active-button', 'data')
)
def mostrar_tabla(n_clicks_eficientes, n_clicks_menos_eficientes, n_clicks_unidades_eficientes, n_clicks_unidades_menos_eficientes, active_btn):
    if active_btn == "btn-top10-eficientes":
        df = df1
    elif active_btn == "btn-top10-menos-eficientes":
        df = df2
    elif active_btn == "btn-top10-unidades-eficientes":
        df = df3
    elif active_btn == "btn-top10-unidades-menos-eficientes":
        df = df4
    else:
        df = df1  # default

    return dash_table.DataTable(
        data=df.to_dict('records'),
        columns=[{"name": col, "id": col} for col in df.columns],
        page_size=10,
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left'},
        style_header={
            'backgroundColor': 'lightgrey',
            'fontWeight': 'bold',
            'textAlign': 'center',
        },
    )

if __name__ == '__main__':
    app.run(debug=True)
