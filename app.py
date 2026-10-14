import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px
import io

# 1. Configuração da Página
st.set_page_config(page_title="Família Finanças", layout="wide")


# 2. Conexão com o Supabase
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


supabase: Client = init_connection()


# 3. Funções de Busca de Dados
@st.cache_data(ttl=600)
def load_data():
    # Exemplo: Buscando transações
    response = supabase.table("transacoes").select("*").execute()
    return pd.DataFrame(response.data)


df = load_data()

# 4. Barra Lateral (Filtros Globais)
st.sidebar.header("Filtros")
membros_disponiveis = ["Pedro", "Rafa", "Paulo", "Sandra"]  # Pode vir do banco
membros_selecionados = st.sidebar.multiselect(
    "Membros Visíveis", membros_disponiveis, default=membros_disponiveis
)

# Trava de segurança: Mínimo 2 membros
if len(membros_selecionados) < 2:
    st.sidebar.warning("Selecione pelo menos 2 membros para visualização.")
    st.stop()

# 5. Organização em Abas
aba1, aba2 = st.tabs(["Visão Geral (Gráficos)", "Extrato Detalhado (Tabela)"])

with aba1:
    st.title("Visão Geral do Orçamento")

    # Linha de métricas de Saldo
    st.metric(label="Saldo Investido / Guardado", value="R$ 84.500,00")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Tendência Mensal e Projeções")
        # Exemplo de gráfico Plotly
        # fig = px.line(df_agrupado, x='data', y='valor', title="Gastos ao longo do tempo")
        # st.plotly_chart(fig, use_container_width=True)
        st.info("Gráfico de tendência renderizado aqui.")

    with col2:
        st.subheader("Regra 50/30/20")
        # Lógica para calcular os percentuais baseados na renda
        st.progress(0.48, text="Gastos Obrigatórios (Máx 50%) - 48%")
        st.progress(0.34, text="Desejos / Lazer (Máx 30%) - 34% (⚠️ Excedido)")
        st.progress(0.18, text="Guardado (Mín 20%) - 18%")

with aba2:
    st.title("Extrato Detalhado")

    # Filtra o dataframe pelos membros selecionados
    # df_filtrado = df[df['membro'].isin(membros_selecionados)]

    st.dataframe(df, use_container_width=True)

    # Botão de Exportação para Excel
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Extrato")

    st.download_button(
        label="📥 Exportar para Excel (.xlsx)",
        data=buffer,
        file_name="extrato_familia.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
