import pandas as pd
import requests
import streamlit as st
import plotly.express as px
from typing import Optional

@st.cache_data(ttl=3600)
def carregar_dados(regiao: str = '', ano: str = '') -> pd.DataFrame:
    """
    Carrega e trata os dados da API de vendas labdados.com.
    Aplica cache por 1 hora para otimização de performance.
    """
    url = 'https://labdados.com/produtos'
    query_string = {'regiao': regiao.lower(), 'ano': ano}
    
    try:
        response = requests.get(url, params=query_string, timeout=15)
        response.raise_for_status()
        dados = pd.DataFrame.from_dict(response.json())
        if not dados.empty and 'Data da Compra' in dados.columns:
            dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format='%d/%m/%Y')
        return dados
    except Exception as e:
        st.error(f"Erro ao conectar com a API de dados: {e}")
        return pd.DataFrame()

def formata_numero(valor: float, prefixo: str = '') -> str:
    """
    Formata valores numéricos para notação simplificada (Mil, Milhões) ou moeda BRL.
    """
    if pd.isna(valor) or valor is None:
        return f"{prefixo}0,00"
        
    for unidade in ['', 'mil']:
        if abs(valor) < 1000:
            return f"{prefixo}{valor:,.2f} {unidade}".replace(',', 'X').replace('.', ',').replace('X', '.')
        valor /= 1000
    return f"{prefixo}{valor:,.2f} milhões".replace(',', 'X').replace('.', ',').replace('X', '.')

def criar_mapa_scatter(df, lat, lon, color, color_continuous_scale, range_color=None, size_max=15, zoom=3, center=None, hover_name=None, hover_data=None, title=''):
    """
    Cria um gráfico de mapa scatter compatível com Plotly 5.x (scatter_mapbox) e Plotly 6.x+ (scatter_map).
    """
    if hasattr(px, 'scatter_map'):
        return px.scatter_map(
            df, lat=lat, lon=lon, color=color,
            color_continuous_scale=color_continuous_scale,
            range_color=range_color,
            size_max=size_max, zoom=zoom, center=center,
            map_style='open-street-map',
            hover_name=hover_name, hover_data=hover_data,
            title=title
        )
    elif hasattr(px, 'scatter_mapbox'):
        return px.scatter_mapbox(
            df, lat=lat, lon=lon, color=color,
            color_continuous_scale=color_continuous_scale,
            range_color=range_color,
            size_max=size_max, zoom=zoom, center=center,
            mapbox_style='open-street-map',
            hover_name=hover_name, hover_data=hover_data,
            title=title
        )
    else:
        fig = px.scatter_geo(
            df, lat=lat, lon=lon, color=color,
            color_continuous_scale=color_continuous_scale,
            hover_name=hover_name, title=title
        )
        fig.update_geos(fitbounds="locations")
        return fig

def exibir_grafico_plotly(fig):
    """
    Exibe gráfico Plotly de forma responsiva sem emitir avisos de depreciação.
    """
    try:
        st.plotly_chart(fig, width='stretch')
    except (TypeError, ValueError, Exception):
        st.plotly_chart(fig, use_container_width=True)
