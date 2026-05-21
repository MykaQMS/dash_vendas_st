import pandas as pd
import requests
import streamlit as st

@st.cache_data(ttl=3600) # O cache expira após 1 hora (3600 segundos)
def carregar_dados(regiao='', ano=''):
    url = 'https://labdados.com/produtos'
    query_string = {'regiao': regiao.lower(), 'ano': ano}
    
    response = requests.get(url, params=query_string)
    dados = pd.DataFrame.from_dict(response.json())
    dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format='%d/%m/%Y')
    
    return dados