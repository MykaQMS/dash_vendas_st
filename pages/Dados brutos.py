import streamlit as st
import pandas as pd
import time
from utils import carregar_dados, formata_numero

st.set_page_config(
    page_title="Self-Service Analytics & Dados Brutos | BI Project",
    page_icon="🗄️",
    layout="wide"
)

# --- Criando funções úteis
@st.cache_data
def converte_csv(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode('utf-8')

def mensagem_sucesso():
    sucesso = st.success('Download do arquivo CSV realizado com sucesso!', icon="✅")
    time.sleep(4)
    sucesso.empty()

st.title("Explorador de Dados Brutos & Self-Service Analytics 🗄️")
st.caption("Filtre, explore e exporte o conjunto completo de dados operacionais de vendas para análises ad-hoc.")

# --- Chamando a API via função em cache com feedback visual
with st.spinner('Conectando à base de dados...'):
    dados = carregar_dados()

if dados.empty:
    st.error("Não foi possível carregar os dados brutos da API.")
    st.stop()

# --- Criando filtros na interface
with st.expander('🔍 Seleção de Colunas Visíveis'):
    colunas = st.multiselect('Selecione as colunas a serem exibidas', list(dados.columns), default=list(dados.columns))

st.sidebar.title("Filtros Granulares")
with st.sidebar.expander('📦 Nome do Produto'):
    produtos = st.multiselect('Filtrar produtos', dados['Produto'].unique(), default=dados['Produto'].unique())

with st.sidebar.expander('💵 Faixa de Preço (R$)'):
    min_p, max_p = float(dados['Preço'].min()), float(dados['Preço'].max())
    preco = st.slider('Selecione a faixa de preço', 0.0, max_p, (0.0, max_p))

with st.sidebar.expander('📅 Data da Compra'):
    data_compra = st.date_input('Selecione o intervalo de datas', (dados['Data da Compra'].min(), dados['Data da Compra'].max()))   

with st.sidebar.expander('👤 Vendedor'):
    vendedores = st.multiselect('Filtrar vendedores', dados['Vendedor'].unique(), default=dados['Vendedor'].unique())

with st.sidebar.expander('📍 Local da Compra (UF)'):
    local_compra = st.multiselect('Filtrar estados', dados['Local da compra'].unique(), default=dados['Local da compra'].unique())

with st.sidebar.expander('🏷️ Categoria do Produto'):
    categoria_produto = st.multiselect('Filtrar categorias', dados['Categoria do Produto'].unique(), default=dados['Categoria do Produto'].unique())

with st.sidebar.expander('💳 Tipo de Pagamento'):
    tipo_pagamento = st.multiselect('Filtrar meios de pagamento', dados['Tipo de pagamento'].unique(), default=dados['Tipo de pagamento'].unique())

with st.sidebar.expander('🔢 Parcelas'):
    parcelas = st.slider('Selecione a quantidade de parcelas', 1, 12, (1, 12))

with st.sidebar.expander('⭐ Avaliação da Compra'):
    avaliacao = st.slider('Selecione a faixa de avaliação (estrelas)', 1, 5, (1, 5))

# --- Aplicação dos Filtros ---
if len(data_compra) == 2:
    data_inicio, data_fim = pd.to_datetime(data_compra[0]), pd.to_datetime(data_compra[1])
else:
    data_inicio, data_fim = dados['Data da Compra'].min(), dados['Data da Compra'].max()

query = '''
Produto in @produtos and \
@preco[0] <= Preço <= @preco[1] and \
@data_inicio <= `Data da Compra` <= @data_fim and \
Vendedor in @vendedores and \
`Local da compra` in @local_compra and \
`Categoria do Produto` in @categoria_produto and \
`Tipo de pagamento` in @tipo_pagamento and \
@parcelas[0] <= `Quantidade de parcelas` <= @parcelas[1] and \
@avaliacao[0] <= `Avaliação da compra` <= @avaliacao[1]
'''

try:
    dados_filtrados = dados.query(query)
    if colunas:
        dados_filtrados = dados_filtrados[colunas]
except Exception as e:
    st.error(f"Erro ao aplicar os filtros selecionados: {e}")
    dados_filtrados = pd.DataFrame()

# --- Exibição de Métricas da Tabela Filtrada ---
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Registros Encontrados", f"{dados_filtrados.shape[0]:,}".replace(',', '.'))
with c2:
    st.metric("Colunas Selecionadas", dados_filtrados.shape[1])
with c3:
    rec_filt = dados_filtrados['Preço'].sum() if 'Preço' in dados_filtrados.columns else 0
    st.metric("Receita Filtrada", formata_numero(rec_filt, 'R$ '))

st.dataframe(dados_filtrados, use_container_width=True)

st.markdown("---")

# --- Exportação em CSV ---
st.subheader("📥 Exportação de Dados para BI / Excel")
col_exp1, col_exp2 = st.columns([2, 1])

with col_exp1:
    nome_arquivo = st.text_input('Defina o nome do arquivo de exportação (sem extensão):', value='relatorio_vendas_filtrado')
    if not nome_arquivo.endswith('.csv'):
        nome_arquivo += '.csv'

with col_exp2:
    st.markdown("  ")
    st.markdown("  ")
    st.download_button(
        label='⬇️ Exportar CSV Filtrado',
        data=converte_csv(dados_filtrados),
        file_name=nome_arquivo,
        mime='text/csv',
        on_click=mensagem_sucesso,
        use_container_width=True
    )
