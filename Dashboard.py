# --- Importando as bibliotecas necessárias
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from utils import carregar_dados

# --- Deixando a aplicação em wide mode
st.set_page_config(layout = 'wide')

# --- Resgatando as cores definidas no .streamlit/config.toml
cor_primaria = st.get_option("theme.primaryColor")

# --- Função para formatar os números em uma forma mais legível
def formata_numero(valor, prefixo = ''):
    for unidade in ['', 'mil']:
        if valor < 1000:
            return f"{prefixo}{valor:.2f} {unidade}"
        valor /= 1000
    return f"{prefixo}{valor:.2f} milhões"

# --- Criando o título do dashboard
st.title("Sales Dashboard 📈", text_alignment='center')

# --- URL da API para obter os dados dos produtos
url = 'https://labdados.com/produtos'
regioes = ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul']

# --- Criando uma barra lateral para filtros
st.sidebar.title("Filtros")
regiao = st.sidebar.selectbox('Região', regioes)

if regiao == 'Brasil':
    regiao = ''

todos_anos = st.sidebar.checkbox('Dados de todo o período', value=True)
if todos_anos:
    ano = ''
else:
    ano = st.sidebar.slider('Ano', min_value=2020, max_value=2023)

query_string = {'regiao': regiao.lower(), 'ano': ano}

# --- Chamando a API via função em cache com feedback visual
with st.spinner('Conectando à base de dados...'):
    dados = carregar_dados(regiao, ano)
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format='%d/%m/%Y')

# --- Criando filtro vendedores
filtro_vendedores = st.sidebar.multiselect('Vendedores', dados['Vendedor'].unique())
if filtro_vendedores:
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]
else:
    dados = dados

## --- Seção: Tabelas ---

# --- Criando variáveis de receita
receita_estado = dados.groupby('Local da compra')[['Preço']].sum()
receita_estado = dados.drop_duplicates(subset=['Local da compra'])[['Local da compra', 'lat', 'lon']].merge(receita_estado, left_on='Local da compra', right_index=True).sort_values('Preço', ascending=False)
receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq='ME'))['Preço'].sum().reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mês'] = receita_mensal['Data da Compra'].dt.month_name()
receita_categorias = dados.groupby('Categoria do Produto')['Preço'].sum().reset_index().sort_values('Preço', ascending=False)

# --- Criando tabelas de quantidade de vendas
vendas_estados = pd.DataFrame(dados.groupby('Local da compra')['Preço'].count())
vendas_estados = dados.drop_duplicates(subset=['Local da compra'])[['Local da compra', 'lat', 'lon']].merge(vendas_estados, left_on='Local da compra', right_index=True).sort_values('Preço', ascending=False)
vendas_mensal = pd.DataFrame(dados.set_index('Data da Compra').groupby(pd.Grouper(freq='ME'))['Preço'].count()).reset_index()
vendas_mensal['Ano'] = vendas_mensal['Data da Compra'].dt.year
vendas_mensal['Mês'] = vendas_mensal['Data da Compra'].dt.month_name()
vendas_categorias = pd.DataFrame(dados.groupby('Categoria do Produto')['Preço'].count().sort_values(ascending=False))

# --- Criando tabelas de vendedores
vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum', 'count']))

## --- Seção: Gráficos ---

# --- Mapa de receita por estado
# Calcula o percentil 85 (ou outro que se ajuste melhor aos seus dados)
teto_cor = receita_estado['Preço'].quantile(0.9)
fig_mapa_receita = px.scatter_mapbox(receita_estado,
                                     lat = 'lat',
                                     lon = 'lon',
                                     color = 'Preço',
                                     color_continuous_scale = 'Plasma',
                                     range_color = (0, teto_cor),
                                     size_max = 15,
                                     zoom = 3,
                                     center = {'lat': -14.2350, 'lon': -51.9253},
                                     mapbox_style = 'carto-positron',
                                     hover_name = 'Local da compra',
                                     hover_data={'lat': False, 'lon': False},
                                     title = 'Receita por Estado')
fig_mapa_receita.update_traces(marker=dict(size=12))
fig_mapa_receita.update_layout(margin={'r':0, 't':40, 'l':0, 'b':0})

# --- Mapa de quantidade de vendas por estado
fig_mapa_vendas = px.scatter_mapbox(vendas_estados,
                                 lat= 'lat',
                                 lon = 'lon',
                                 color='Preço',
                                 color_continuous_scale='Plasma',
                                 size_max=15,
                                 zoom=3,
                                 center={'lat': -14.2350, 'lon': -51.9253},
                                 mapbox_style='carto-positron',
                                 hover_name='Local da compra',
                                 hover_data={'lat': False, 'lon': False},
                                 title='Quantidade de Vendas por Estado')
fig_mapa_vendas.update_traces(marker=dict(size=12))
fig_mapa_vendas.update_layout(margin={'r':0, 't':40, 'l':0, 'b':0})

# Escala categórica de 4 cores
color_scale = ["#7f0098", "#009879", "#984700", "#0074d9"]

# --- Gráfico de quantidade de vendas mensal
fig_vendas_mensal = px.line(vendas_mensal,
                            x = 'Mês',
                            y = 'Preço',
                            markers = True,
                            range_y = (0, vendas_mensal['Preço'].max() * 1.1),
                            color = 'Ano',
                            line_dash = 'Ano',
                            title = 'Quantidade de Vendas Mensal',
                            color_discrete_sequence=[color_scale[0], color_scale[1], color_scale[2], color_scale[3]])
fig_vendas_mensal.update_layout(yaxis_title = 'Quantidade de Vendas')

# --- Gráfico dos 5 estados com mais vendas
fig_vendas_estado = px.bar(vendas_estados.head(),
                           x = 'Local da compra',
                           y = 'Preço',
                           text_auto = True,
                           title = 'Top 5 Estados por Quantidade de Vendas',
                           color_discrete_sequence=[cor_primaria])
fig_vendas_estado.update_layout(xaxis_title = 'Estado', yaxis_title = 'Quantidade de Vendas')

# --- Gráfico de quantidade de vendas por categoria
fig_vendas_categorias = px.bar(vendas_categorias,
                              text_auto = True,
                              title = 'Quantidade de Vendas por Categoria',
                              color_discrete_sequence=[cor_primaria])
fig_vendas_categorias.update_layout(xaxis_title = 'Categoria do Produto', yaxis_title = 'Quantidade de Vendas')

# --- Gráfico de receita mensal
fig_receita_mensal = px.line(receita_mensal,
                             x = 'Mês',
                             y = 'Preço',
                             markers = True,
                             range_y = (0, receita_mensal['Preço'].max() * 1.1),
                             color = 'Ano',
                             line_dash = 'Ano',
                             title = 'Receita Mensal',
                             color_discrete_sequence=[color_scale[0], color_scale[1], color_scale[2], color_scale[3]])
fig_receita_mensal.update_layout(yaxis_title = 'Receita (R$)')

# --- Gráfico de receita por estado
fig_receita_estado = px.bar(receita_estado.head(),
                            x = 'Local da compra',
                            y = 'Preço',
                            text_auto = True,
                            title = 'Top 5 Estados por Receita',
                            color_discrete_sequence=[cor_primaria])
fig_receita_estado.update_layout(xaxis_title = 'Estado', yaxis_title = 'Receita (R$)')

# --- Gráfico de receita por categoria
fig_receitas_categorias = px.bar(receita_categorias,
                             x = 'Categoria do Produto',
                             y = 'Preço',
                             text_auto = True,
                             title = 'Receita por Categoria',
                             color_discrete_sequence=[cor_primaria])
fig_receitas_categorias.update_layout(xaxis_title = 'Categoria do Produto', yaxis_title = 'Receita (R$)')

## --- Seção: Visualização

# --- Criando as abas
aba1, aba2, aba3 = st.tabs(['Receita', 'Quantidade de Vendas', 'Vendedores'])

# --- Exibindo as métricas
receita_total = dados['Preço'].sum()
quantidade_vendas = dados.shape[0]

# --- Customizando o estilo das métricas
st.markdown("""
<style>
[data-testid="stMetricValue"] {
            color: "FF4B4B";
            font-size: 30px;
            font-weight: bold
}

[data-testid="stMetricLabel"] {
            color: "00C2FF";
            font-size: 18px;
}
            
[data-testid="stMetricDelta"]: {
            font-size: 14px;
}
</style>
""", unsafe_allow_html=True)

with aba1:
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Receita Total 💵", 
                  formata_numero(receita_total, 'R$ '),
                  border=True)
        st.plotly_chart(fig_mapa_receita, use_container_width=True)
        st.plotly_chart(fig_receita_estado, use_container_width=True)
    with col2:
        st.metric("Quantidade de Vendas 📦",
                  formata_numero(quantidade_vendas),
                  border=True)
        st.plotly_chart(fig_receita_mensal, use_container_width=True)
        st.plotly_chart(fig_receitas_categorias, use_container_width=True)

with aba2:
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Receita Total 💵", 
                  formata_numero(receita_total, 'R$ '),
                  border=True)
        st.plotly_chart(fig_mapa_vendas, use_container_width=True)
        st.plotly_chart(fig_vendas_estado, use_container_width=True)
    with col2:
        st.metric("Quantidade de Vendas 📦", 
                  formata_numero(quantidade_vendas), 
                  border=True)
        st.plotly_chart(fig_vendas_mensal, use_container_width=True)
        st.plotly_chart(fig_vendas_categorias, use_container_width=True)

with aba3:
    qtd_vendedores = st.number_input("Quantidade de Vendedores", min_value=2, value=10)
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Receita Total 💵", 
                  formata_numero(receita_total, 'R$ '),
                  border=True)
        fig_receita_vendedores = px.bar(vendedores[[ 'sum']].sort_values('sum', ascending=False).head(qtd_vendedores),
                                        x = 'sum',
                                        y = vendedores[['sum']].sort_values('sum', ascending=False).head(qtd_vendedores).index,
                                        text_auto = True,
                                        orientation='h',
                                        title = f'Top {qtd_vendedores} Vendedores por Receita',
                                        color_discrete_sequence=[cor_primaria],
                                        labels={'sum': 'Receita (R$)', 'y': 'Vendedor'})
        fig_receita_vendedores.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_receita_vendedores)
    with col2:
        st.metric("Quantidade de Vendas 📦", 
                  formata_numero(quantidade_vendas), 
                  border=True)
        fig_vendas_vendedores = px.bar(vendedores[['count']].sort_values('count', ascending=False).head(qtd_vendedores),
                                        x = 'count',
                                        y = vendedores[['count']].sort_values('count', ascending=False).head(qtd_vendedores).index,
                                        text_auto = True,
                                        orientation='h',
                                        title = f'Top {qtd_vendedores} Vendedores por Quantidade de Vendas',
                                        color_discrete_sequence=[cor_primaria],
                                        labels={'count': 'Quantidade de Vendas', 'y': 'Vendedor'})
        fig_vendas_vendedores.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_vendas_vendedores)
