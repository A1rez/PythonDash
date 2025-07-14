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

    html.Div([
        #gráfico de barras
        html.Div([
            dcc.Graph(
                id = 'grafico-de-vendas',
                style = {'height':'80vh'}
            )
        ], style={'width': '60%', 'display': 'inline-block'}),

        #gráfico de pizza
        html.Div([
            dcc.Graph(
                id = 'grafico-pizza-regiao',
                style = {'height':'40vh'}
            )
        ],style={'width': '40%', 'display': 'inline-block'})
    ],style={'display': 'flex'})
])

@app.callback(
    [Output('grafico-de-vendas','figure'),
     Output('grafico-pizza-regiao', 'figure')],
    Input('seguimento', 'value')
)

def update_graph(seguimento_selecionado):
    dados_filtrados =  dataset[dataset['Segment'].isin(seguimento_selecionado)]
    dados_agg = dados_filtrados.groupby(['Ano','Category'], as_index = False)['Sales'].sum()

    fig_bar = px.bar(
        dados_agg,
        x = 'Ano',
        y = 'Sales',
        color = 'Category',
        title = 'Vendas Anuais',
        barmode = 'group',
        labels={'Sales': 'Total de Vendas', 'Ano': 'Ano', 'Category': 'Categoria'},
        text = 'Sales',
        color_discrete_map={
            'Furniture': '#040950',  # Azul
            'Office Supplies': '#383e9b',  # Laranja
            'Technology': '#515a5a'   # Vermelho
        },
        category_orders={'Ano': sorted(dados_agg['Ano'].unique())}
    ).update_layout(
            xaxis={'type': 'category'},  # Garante que o ano seja tratado como categoria
            plot_bgcolor='rgba(0,0,0,0)'
        )

    fig_bar.update_traces(
        texttemplate='%{text:.0f}',
        textposition='outside',
        marker_line_width=1.5,
        opacity=1,
        textfont_size=200
    )

    region_counts = dados_filtrados['Region'].value_counts().reset_index()
    region_counts.columns = ['Region', 'Count']

    fig_pie = px.pie(
        region_counts,
        names = 'Region',
        values = 'Count',
        title = f'Procentegem de Participação por Região',
        labels ={'Region' : 'Região', 'Procentagem' : 'Participação'},
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    
    fig_pie.update_traces(
        textposition='outside',
        textinfo='percent',
        insidetextorientation='radial'
    )


    return fig_bar,fig_pie

app.run(debug=True)
