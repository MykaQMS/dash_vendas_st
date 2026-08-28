# --- Importando as bibliotecas necessárias
import streamlit as st
import pandas as pd
import plotly.express as px
from utils import carregar_dados, formata_numero

# --- Configuração da página
st.set_page_config(
    page_title="Executive Sales Dashboard | Business Intelligence",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Resgatando as cores definidas no .streamlit/config.toml
try:
    cor_primaria = st.get_option("theme.primaryColor")
except Exception:
    cor_primaria = "#556DE8"

# --- Estilização CSS Customizada para Métricas e Elementos visuais
st.markdown("""
<style>
    /* Estilização dos Cards de Métricas */
    [data-testid="stMetricValue"] {
        color: #556DE8;
        font-size: 28px !important;
        font-weight: 700 !important;
    }
    [data-testid="stMetricLabel"] {
        color: #31333F;
        font-size: 15px !important;
        font-weight: 600 !important;
    }
    div[data-testid="stMetric"] {
        background-color: #F8F9FA;
        border: 1px solid #E9ECEF;
        padding: 15px 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        white-space: pre-wrap;
        border-radius: 8px 8px 0 0;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# --- Cabeçalho da Aplicação
st.title("Sales Dashboard & Business Intelligence 📈")
st.caption("Painel executivo interativo para análise de desempenho comercial, distribuição geográfica e receita nacional.")

# --- Barra Lateral: Filtros Estratégicos
st.sidebar.title("Filtros Estratégicos")

regioes = ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul']
regiao_sel = st.sidebar.selectbox('Região Geográfica', regioes)
regiao = '' if regiao_sel == 'Brasil' else regiao_sel

todos_anos = st.sidebar.checkbox('Todo o Período Histórico', value=True)
ano = '' if todos_anos else st.sidebar.slider('Ano de Exercício', min_value=2020, max_value=2023, value=2022)

# --- Carregamento de Dados com Feedback
with st.spinner('Conectando à base de dados de vendas...'):
    dados = carregar_dados(regiao, str(ano))

if dados.empty:
    st.warning("⚠️ Nenhuma informação encontrada para os filtros selecionados.")
    st.stop()

# --- Filtro Dinâmico de Vendedores
vendedores_unicos = sorted(dados['Vendedor'].dropna().unique())
filtro_vendedores = st.sidebar.multiselect('Equipe de Vendedores', vendedores_unicos)
if filtro_vendedores:
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]

if dados.empty:
    st.info("Nenhum registro encontrado para a combinação de vendedores selecionada.")
    st.stop()

# --- Transformações e Agregações de Dados ---
# 1. Visão por Estado
receita_estado = dados.groupby('Local da compra')[['Preço']].sum()
receita_estado = dados.drop_duplicates(subset=['Local da compra'])[['Local da compra', 'lat', 'lon']].merge(receita_estado, left_on='Local da compra', right_index=True).sort_values('Preço', ascending=False)

vendas_estados = pd.DataFrame(dados.groupby('Local da compra')['Preço'].count()).rename(columns={'Preço': 'Contagem'})
vendas_estados = dados.drop_duplicates(subset=['Local da compra'])[['Local da compra', 'lat', 'lon']].merge(vendas_estados, left_on='Local da compra', right_index=True).sort_values('Contagem', ascending=False)

# 2. Visão Temporal (Mensal)
receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq='ME'))['Preço'].sum().reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mês'] = receita_mensal['Data da Compra'].dt.month_name()

vendas_mensal = pd.DataFrame(dados.set_index('Data da Compra').groupby(pd.Grouper(freq='ME'))['Preço'].count()).reset_index().rename(columns={'Preço': 'Contagem'})
vendas_mensal['Ano'] = vendas_mensal['Data da Compra'].dt.year
vendas_mensal['Mês'] = vendas_mensal['Data da Compra'].dt.month_name()

# 3. Visão por Categoria
receita_categorias = dados.groupby('Categoria do Produto')['Preço'].sum().reset_index().sort_values('Preço', ascending=False)
vendas_categorias = dados.groupby('Categoria do Produto')['Preço'].count().reset_index().rename(columns={'Preço': 'Contagem'}).sort_values('Contagem', ascending=False)

# 4. Visão Comercial (Vendedores)
vendedores_df = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum', 'count']))

# Palette de Cores para Séries Temporais
color_scale = ["#556DE8", "#00A86B", "#FFB703", "#E63946", "#7209B7"]

# --- Construção dos Gráficos Interativos ---

# Mapa de Receita
teto_cor = receita_estado['Preço'].quantile(0.9) if not receita_estado.empty else 1000
fig_mapa_receita = px.scatter_mapbox(
    receita_estado,
    lat='lat', lon='lon', color='Preço',
    color_continuous_scale='Plasma',
    range_color=(0, teto_cor),
    size_max=15, zoom=3,
    center={'lat': -14.2350, 'lon': -51.9253},
    mapbox_style='open-street-map',
    hover_name='Local da compra',
    hover_data={'lat': False, 'lon': False, 'Preço': ':.2f'},
    title='<b>Distribuição Geográfica da Receita</b>'
)
fig_mapa_receita.update_traces(marker=dict(size=12))
fig_mapa_receita.update_layout(margin={'r':0, 't':40, 'l':0, 'b':0})

# Mapa de Volume de Vendas
fig_mapa_vendas = px.scatter_mapbox(
    vendas_estados,
    lat='lat', lon='lon', color='Contagem',
    color_continuous_scale='Viridis',
    size_max=15, zoom=3,
    center={'lat': -14.2350, 'lon': -51.9253},
    mapbox_style='open-street-map',
    hover_name='Local da compra',
    hover_data={'lat': False, 'lon': False},
    title='<b>Distribuição Geográfica do Volume de Vendas</b>'
)
fig_mapa_vendas.update_traces(marker=dict(size=12))
fig_mapa_vendas.update_layout(margin={'r':0, 't':40, 'l':0, 'b':0})

# Receita Mensal (Linha)
fig_receita_mensal = px.line(
    receita_mensal, x='Mês', y='Preço', markers=True,
    color='Ano', line_dash='Ano',
    title='<b>Evolução Mensal do Faturamento (R$)</b>',
    color_discrete_sequence=color_scale
)
fig_receita_mensal.update_layout(yaxis_title='Receita (R$)')

# Volume Mensal (Linha)
fig_vendas_mensal = px.line(
    vendas_mensal, x='Mês', y='Contagem', markers=True,
    color='Ano', line_dash='Ano',
    title='<b>Evolução Mensal do Volume de Vendas</b>',
    color_discrete_sequence=color_scale
)
fig_vendas_mensal.update_layout(yaxis_title='Unidades Vendidas')

# Top 5 Estados Receita
fig_receita_estado = px.bar(
    receita_estado.head(5), x='Local da compra', y='Preço', text_auto='.2s',
    title='<b>Top 5 Estados por Receita Total</b>',
    color_discrete_sequence=[cor_primaria]
)
fig_receita_estado.update_layout(xaxis_title='Estado', yaxis_title='Receita (R$)')

# Top 5 Estados Volume
fig_vendas_estado = px.bar(
    vendas_estados.head(5), x='Local da compra', y='Contagem', text_auto=True,
    title='<b>Top 5 Estados por Volume de Vendas</b>',
    color_discrete_sequence=[cor_primaria]
)
fig_vendas_estado.update_layout(xaxis_title='Estado', yaxis_title='Unidades Vendidas')

# Receita por Categoria
fig_receitas_categorias = px.bar(
    receita_categorias, x='Categoria do Produto', y='Preço', text_auto='.2s',
    title='<b>Receita por Categoria de Produto</b>',
    color_discrete_sequence=[cor_primaria]
)
fig_receitas_categorias.update_layout(xaxis_title='Categoria', yaxis_title='Receita (R$)')

# Volume por Categoria
fig_vendas_categorias = px.bar(
    vendas_categorias, x='Categoria do Produto', y='Contagem', text_auto=True,
    title='<b>Volume por Categoria de Produto</b>',
    color_discrete_sequence=[cor_primaria]
)
fig_vendas_categorias.update_layout(xaxis_title='Categoria', yaxis_title='Unidades Vendidas')

# --- Métricas Executivas Globais ---
receita_total = dados['Preço'].sum()
quantidade_vendas = dados.shape[0]
ticket_medio = receita_total / quantidade_vendas if quantidade_vendas > 0 else 0

# --- Estrutura em Abas (Tabs) ---
aba1, aba2, aba3 = st.tabs(['💰 Faturamento & Receita', '📦 Volume de Vendas', '👥 Desempenho Comercial'])

with aba1:
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Receita Total", formata_numero(receita_total, 'R$ '))
    with m2:
        st.metric("Total de Pedidos", formata_numero(quantidade_vendas))
    with m3:
        st.metric("Ticket Médio", formata_numero(ticket_medio, 'R$ '))

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig_mapa_receita, use_container_width=True)
        st.plotly_chart(fig_receita_estado, use_container_width=True)
    with col2:
        st.plotly_chart(fig_receita_mensal, use_container_width=True)
        st.plotly_chart(fig_receitas_categorias, use_container_width=True)

with aba2:
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Receita Total", formata_numero(receita_total, 'R$ '))
    with m2:
        st.metric("Total de Pedidos", formata_numero(quantidade_vendas))
    with m3:
        st.metric("Ticket Médio", formata_numero(ticket_medio, 'R$ '))

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig_mapa_vendas, use_container_width=True)
        st.plotly_chart(fig_vendas_estado, use_container_width=True)
    with col2:
        st.plotly_chart(fig_vendas_mensal, use_container_width=True)
        st.plotly_chart(fig_vendas_categorias, use_container_width=True)

with aba3:
    qtd_vendedores = st.number_input("Top Vendedores em Destaque", min_value=2, max_value=20, value=10)
    
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Receita Total", formata_numero(receita_total, 'R$ '))
    with m2:
        st.metric("Total de Pedidos", formata_numero(quantidade_vendas))
    with m3:
        st.metric("Vendedores Ativos", len(vendedores_df))

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        top_rec = vendedores_df[['sum']].sort_values('sum', ascending=False).head(qtd_vendedores)
        fig_receita_vendedores = px.bar(
            top_rec, x='sum', y=top_rec.index, text_auto='.2s', orientation='h',
            title=f'<b>Top {qtd_vendedores} Vendedores por Receita Gerada</b>',
            color_discrete_sequence=[cor_primaria],
            labels={'sum': 'Receita (R$)', 'y': 'Vendedor'}
        )
        fig_receita_vendedores.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_receita_vendedores, use_container_width=True)
    with col2:
        top_qtd = vendedores_df[['count']].sort_values('count', ascending=False).head(qtd_vendedores)
        fig_vendas_vendedores = px.bar(
            top_qtd, x='count', y=top_qtd.index, text_auto=True, orientation='h',
            title=f'<b>Top {qtd_vendedores} Vendedores por Volume de Pedidos</b>',
            color_discrete_sequence=[cor_primaria],
            labels={'count': 'Unidades Vendidas', 'y': 'Vendedor'}
        )
        fig_vendas_vendedores.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_vendas_vendedores, use_container_width=True)
