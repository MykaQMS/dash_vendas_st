# Dashboard de Vendas com Streamlit

Aplicação em Streamlit para visualizar dados de vendas de produtos a partir da API `https://labdados.com/produtos`.

O projeto possui um dashboard principal com métricas e gráficos interativos, além de uma página de dados brutos com filtros detalhados e exportação em CSV.

## Funcionalidades

- Filtro por região e ano no dashboard principal.
- Filtro por vendedores.
- Indicadores de receita total e quantidade de vendas.
- Gráficos de receita por estado, mês, categoria e vendedor.
- Gráficos de quantidade de vendas por estado, mês, categoria e vendedor.
- Página de dados brutos com filtros por produto, preço, data, vendedor, local, categoria, pagamento, parcelas e avaliação.
- Download dos dados filtrados em CSV.
- Tema customizado via `.streamlit/config.toml`.

## Estrutura do projeto

```text
Dashboard_Streamlit/
├── Dashboard.py
├── requirements.txt
├── README.md
├── .streamlit/
│   └── config.toml
└── pages/
    └── Dados brutos.py
```

## Requisitos

- Python 3.13 ou superior
- Ambiente virtual recomendado

Dependências principais:

```text
streamlit
pandas
plotly
requests
```

## Como executar

1. Crie e ative um ambiente virtual:

```powershell
python -m venv venv
.\venv\Scripts\activate
```

2. Instale as dependências:

```powershell
pip install -r requirements.txt
```

3. Execute o app a partir da raiz do projeto:

```powershell
streamlit run Dashboard.py
```

4. Acesse no navegador:

```text
http://localhost:8501
```

## Páginas

### Dashboard

Arquivo principal: `Dashboard.py`

Exibe uma visão consolidada das vendas, com abas para:

- Receita
- Quantidade de vendas
- Vendedores

### Dados Brutos

Arquivo: `pages/Dados brutos.py`

Permite visualizar a tabela completa da API, aplicar filtros detalhados, selecionar colunas e baixar o resultado em CSV.

## Configuração visual

O tema do app fica em:

```text
.streamlit/config.toml
```

Exemplo:

```toml
[theme]
primaryColor = "#556DE8"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#D6D6D6"
textColor = "#000000"
font = "sans serif"
```

Para alterações de tema, salve o arquivo e recarregue o app. Para algumas configurações do Streamlit, pode ser necessário parar o servidor e executar novamente.

## Fonte dos dados

Os dados são carregados da API:

```text
https://labdados.com/produtos
```

O app depende de conexão com a internet para buscar os dados.
