import pandas as pd
from dash import Dash, dash_table, html, dcc, Output, Input, callback_context

# Leer las dos hojas
df1 = pd.read_excel("./data/Rutas_Resumen.xlsx", sheet_name="Top 10 Rutas Mas Eficientes")
df2 = pd.read_excel("./data/Rutas_Resumen.xlsx", sheet_name="Top 10 Rutas Menos Eficientes")
df3 = pd.read_excel("./data/Rutas_Resumen.xlsx", sheet_name="Top 10 Unidades Más Eficientes")
df4 = pd.read_excel("./data/Rutas_Resumen.xlsx", sheet_name="Top 10 Unidades Menos Eficientes")
app = Dash(__name__)

app.layout = html.Div([
    html.Div(className="header", children=[
        html.H2("Top 10 Rutas y Unidades Más y Menos Eficientes", className="header-title"),
        html.Br(),
        html.H3 ("CPK calculado contemplando Costo de combustible y Costo de Mantenimiento entre Kilometros totales recorridos por cada unidad", className="header-subtitle"),
        html.P("Seleccione una opción para ver la tabla correspondiente:", className="header-description"),
    ]),
    html.Div([
        html.Button("Top 10 Rutas Más Eficientes", id="btn-top10-eficientes", n_clicks=0, className="button hoverable-button"),
        html.Button("Top 10 Rutas Menos Eficientes", id="btn-top10-menos-eficientes", n_clicks=0, className="button hoverable-button"),
        html.Button("Top 10 Unidades Más Eficientes", id="btn-top10-unidades-eficientes", n_clicks=0, className="button hoverable-button"),
        html.Button("Top 10 Unidades Menos Eficientes", id="btn-top10-unidades-menos-eficientes", n_clicks=0, className="button hoverable-button"),
    ]),
    html.Div(id="tabla-container", className="table-container"),
])

@app.callback(
    Output("tabla-container", "children"),
    Input("btn-top10-eficientes", "n_clicks"),
    Input("btn-top10-menos-eficientes", "n_clicks"),
    Input("btn-top10-unidades-eficientes", "n_clicks"),
    Input("btn-top10-unidades-menos-eficientes", "n_clicks"),
)
def mostrar_tabla(n_top10_eficientes, n_top10_menos_eficientes, n_top10_unidades_eficientes, n_top10_unidades_menos_eficientes):
    ctx = callback_context
    if not ctx.triggered:
        df = df1  # default
    else:
        btn_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if btn_id == "btn-top10-eficientes":
            df = df1
        elif btn_id == "btn-top10-menos-eficientes":
            df = df2
        elif btn_id == "btn-top10-unidades-eficientes":
            df = df3
        elif btn_id == "btn-top10-unidades-menos-eficientes":
            df = df4

    return dash_table.DataTable(
        data=df.to_dict('records'),
        columns=[{"name": col, "id": col} for col in df.columns],
        page_size=10,
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left', 'padding': '10px'},
        style_cell_conditional=[
            {'if': {'column_id': 'Ruta'}, 'width': '30%'},
            {'if': {'column_id': 'Unidad'}, 'width': '10%'},
            {'if': {'column_id': 'CPK'}, 'width': '20%'},
            {'if': {'column_id': 'Costo Combustible'}, 'width': '20%'},
        ],
        style_header={
            'backgroundColor': 'lightgrey',
            'fontWeight': 'bold',
            'textAlign': 'center',
            'whiteSpace': 'normal',
        },
        style_data={
            'whiteSpace': 'normal',
            'height': 'auto',
            'lineHeight': '15px',
        }
        
    )

if __name__ == '__main__':
    app.run(debug=True, port=8050)
