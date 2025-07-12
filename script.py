#importando bibliotecas
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import datetime as dt

#lendo dataset
dataset = ('your path here')

#setando a coluna de data como um date time e criando uma coluna com o ano de referência
dataset['Order Date']=pd.to_datetime(dataset['Order Date'], format = '%d/%m/%Y')
dataset['Ano'] = dataset['Order Date'].dt.year

#inicializando app
app = Dash()

#layout
app.layout = html.Div([
    html.H1("Vendas Anuais", style = {'textAlign': 'center', 'fontWeight': 'bold'}),

    html.Div([
        html.Div([
            html.Label("Tipo de Seguimento", style = {'fontWeight': 'bold'}),
            dcc.Checklist(
                id='seguimento',
                options = [
                    {'label': 'Consumidor', 'value':'Consumer'},
                    {'label': 'Corporativo', 'value':'Corporate'},
                    {'label': 'Home office', 'value':'Home Office'}
                ],
                value = dataset['Segment'].unique(),
                labelStyle={'display': 'inline-block', 'margin-right': '15px'},
                inputStyle={'margin-right': '5px'}
            )
        ], style={
            'background-color': '#f8f9fa',
            'padding': '15px',
            'border-radius': '5px',
            'margin-bottom': '20px'
        })
    ]),

    dcc.Graph(
        id = 'grafico-de-vendas',
        style = {'height':'80vh'}
    )
]),

@app.callback(
    Output('grafico-de-vendas','figure'),
    Input('seguimento', 'value')
)

def update_graph(seguimento_selecionado):
    dados_filtrados =  dataset[dataset['Segment'].isin(seguimento_selecionado)]
    dados_agg = dados_filtrados.groupby(['Ano','Category'], as_index = False)['Sales'].sum()

    fig = px.bar(
        dados_agg,
        x = 'Ano',
        y = 'Sales',
        color = 'Category',
        title = 'Vendas Anuais',
        barmode = 'group',
        labels={'Sales': 'Total de Vendas', 'Ano': 'Ano', 'Category': 'Categoria'},
        text = 'Sales',
        color_discrete_map={
            'Furniture': '#040950',  
            'Office Supplies': '#383e9b',  
            'Technology': '#515a5a'   
        },
        category_orders={'Ano': sorted(dados_agg['Ano'].unique())}
    ).update_layout(
            xaxis={'type': 'category'},  # Garante que o ano seja tratado como categoria
            plot_bgcolor='rgba(0,0,0,0)'
        )

    fig.update_traces(
        texttemplate='%{text:.0f}',
        textposition='outside',
        marker_line_width=1.5,
        opacity=0.8
    )


    return fig

app.run(debug=True)
