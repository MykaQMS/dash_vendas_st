import pandas as pd
import requests
import streamlit as st
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