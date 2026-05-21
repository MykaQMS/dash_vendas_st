import streamlit as st
import requests
import pandas as pd
import time
from utils import carregar_dados

# --- Criando funções úteis
@st.cache_data
def converte_csv(df):
    return df.to_csv(index=False).encode('utf-8')

def mensagem_sucesso():
    sucesso = st.success('Arquivo baixado com sucesso!', icon="✅")
    time.sleep(5)
    sucesso.empty()

st.title("Dados Brutos dos Produtos 🗄️", text_alignment='center')

# --- Chamando a API via função em cache com feedback visual
with st.spinner('Conectando à base de dados...'):
    dados = carregar_dados()

# --- Criando filtros
with st.expander('Colunas'):
    colunas = st.multiselect('Selecione as colunas a serem exibidas', list(dados.columns), list(dados.columns))

st.sidebar.title("Filtros")
with st.sidebar.expander('Nome do produto'):
    produtos = st.multiselect('Selecione os produtos', dados['Produto'].unique(), dados['Produto'].unique())

with st.sidebar.expander('Preço do produto'):
    preco = st.slider('Selecione a faixa de preço', 0, 5000, (0, 5000))

with st.sidebar.expander('Data da compra'):
    data_compra = st.date_input('Selecione a data', (dados['Data da Compra'].min(), dados['Data da Compra'].max()))   

with st.sidebar.expander('Vendedor'):
    vendedores = st.multiselect('Selecione os vendedores', dados['Vendedor'].unique(), dados['Vendedor'].unique())

with st.sidebar.expander('Local da compra'):
    local_compra = st.multiselect('Selecione os locais de compra', dados['Local da compra'].unique(), dados['Local da compra'].unique())

with st.sidebar.expander('Categoria do produto'):
    categoria_produto = st.multiselect('Selecione as categorias de produto', dados['Categoria do Produto'].unique(), dados['Categoria do Produto'].unique())

with st.sidebar.expander('Tipo de pagamento'):
    tipo_pagamento = st.multiselect('Selecione os tipos de pagamento', dados['Tipo de pagamento'].unique(), dados['Tipo de pagamento'].unique())

with st.sidebar.expander('Quantidade de parcelas'):
    parcelas = st.slider('Selecione a quantidade de parcelas', 1, 12, (1, 12))

with st.sidebar.expander('Avaliação da compra'):
    avaliacao = st.slider('Selecione a avaliação do produto', 1, 5, (1, 5))

# --- Criando a query dos filtros
query = '''
Produto in @produtos and \
@preco[0] <= Preço <= @preco[1] and \
@data_compra[0] <= `Data da Compra` <= @data_compra[1] and \
Vendedor in @vendedores and \
`Local da compra` in @local_compra and \
`Categoria do Produto` in @categoria_produto and \
`Tipo de pagamento` in @tipo_pagamento and \
@parcelas[0] <= `Quantidade de parcelas` <= @parcelas[1] and \
@avaliacao[0] <= `Avaliação da compra` <= @avaliacao[1]
'''

# --- Aplicando e exibindo os dados filtrados
dados_filtrados = dados.query(query)
dados_filtrados = dados_filtrados[colunas]

st.dataframe(dados_filtrados)

st.markdown(f"A tabela possui :blue[{dados_filtrados.shape[0]}] linhas e :blue[{dados_filtrados.shape[1]}] colunas.")

# --- Criando botão para download dos dados filtrados
st.markdown('Escreva um nome para o arquivo')
col1, col2 = st.columns(2)
with col1:
    nome_arquivo = st.text_input('', label_visibility='collapsed')
    nome_arquivo += '.csv'
with col2:
    st.download_button('Fazer o download da tabela em csv',
                       data = converte_csv(dados_filtrados),
                       file_name = nome_arquivo,
                       mime = 'text/csv',
                       on_click = mensagem_sucesso)
