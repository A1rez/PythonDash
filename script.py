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
    html.H1("Overview de Vendas", style = {'textAlign': 'center', 'fontWeight': 'bold'}),

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
                style = {'height':'80vh', 'margin-bottom':'20px'}
            ),
    

    html.Div([
        #gráfico de participação por região
        html.Div([
            dcc.Graph(
                id = 'grafico-regiao',
                style = {'height':'75vh'}
            )
        ],style={'width': '50%', 'display': 'inline-block'}),

        #gráfico tempo médio de envio
        html.Div([
            dcc.Graph(
                id = 'grafico-tempo-envio',
                style = {'height': '75vh'}
            )
            ], style = {'width': '50%', 'display': 'inline-block'}),
    ],style = {'display': 'flex'})
], style = {'height' : '500px'})

@app.callback(
    [Output('grafico-de-vendas','figure'),
     Output('grafico-regiao', 'figure'),
     Output('grafico-tempo-envio', 'figure')],
    Input('seguimento', 'value')
)

def update_graph(seguimento_selecionado):
    #filtragem dos dados de vendas
    dados_filtrados =  dataset[dataset['Segment'].isin(seguimento_selecionado)]
    dados_agg = dados_filtrados.groupby(['Ano','Category'], as_index = False)['Sales'].sum()

    #filtragem da porcentagem de vendas por região
    region_year = dados_filtrados.groupby(['Ano', 'Region'], as_index=False)['Sales'].sum()
    total_sales = region_year.groupby('Ano')['Sales'].transform('sum')
    region_year['Percentage'] = (region_year['Sales'] / total_sales) * 100

    #gráfico de vendas anuais
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
            plot_bgcolor='rgba(0,0,0,0)',
            legend = dict(
                orientation = "h",
                yanchor = 'bottom',
                y = 1,
                xanchor = "left",
                x = -0.1
            )
        )

    fig_bar.update_traces(
        texttemplate='%{text:.0f}',
        textposition='outside',
        marker_line_width=1.5,
        opacity=1,
        textfont_size=200
    )

    #gráfico de porcentagem anual de vendas por região
    fig_stacked = px.bar(
        region_year,
        x = 'Ano',
        y = 'Percentage',
        color= 'Region',
        title = 'Participação regional de vendas',
        labels ={'Percentage' : 'Participação (%)', 'Ano' : 'Ano', 'Region' : 'Região'},
        text = 'Percentage',
        barmode = 'stack',
        color_discrete_sequence=px.colors.qualitative.Bold
    ).update_layout(
        yaxis = {'ticksuffix' : '%'},
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis={'type': 'category'}
    )
    
    fig_stacked.update_traces(
        texttemplate='%{text:.1f}%',
        textposition='inside',
        marker_line_width=0.5
    )

    #gráfico do tempo médio de envio
    dados_filtrados["tempo de envio"] = (dados_filtrados['Ship Date'] - dados_filtrados['Order Date']).dt.days
    tempo_de_envio = dados_filtrados.groupby(['Ano','Ship Mode'], as_index = False)['tempo de envio'].mean()

    fig_shipping = px.bar(
        tempo_de_envio,
        x= 'Ano',
        y = 'tempo de envio',
        color = 'Ship Mode',
        title = 'Tempo médio de envio (dias)',
        labels = {'tempo de envio' : 'Dias', 'Ano' : 'Ano', 'Ship Mode' : 'Modo de Envio'},
        text = 'tempo de envio',
        barmode = 'group',
        color_discrete_sequence=px.colors.qualitative.Vivid
    ).update_layout(
        xaxis={'type': 'category'},
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation="h", yanchor="bottom", y=-0.4, xanchor="center", x=0.5)
    )
    
    fig_shipping.update_traces(
        texttemplate='%{text:.1f}',
        textposition='outside',
        marker_line_width=1,
        opacity=0.8
    )


    return fig_bar,fig_stacked, fig_shipping

app.run(debug=True)
