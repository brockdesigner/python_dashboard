import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Dashboard de Classificação de Projeto",
    page_icon="📊",
    layout="wide"
)

# --- INJEÇÃO DE CSS PARA PERSONALIZAÇÃO ---
# Você pode alterar qualquer valor aqui para customizar o visual



with open("assets/streamlit.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

estilo_css = """
<style>
/* Barra superior do Streamlit */
[data-testid="stHeader"] {
    background-color: rgba(5, 82, 152, 0.4); /* Branco com 50% de transparência */
    color: #fff !important;
    border: none;
}
/* Cor de fundo do container principal */
[data-testid="stAppViewContainer"] {
    background-color: #152D51; /* Um cinza escuro */
}

/* Cor de fundo da barra lateral */
[data-testid="stSidebar"] {
    background-color: #055298; /* Azul Ipiam */
}

/* Cor e tamanho da fonte do título principal */
h1 {
    color: #84BBD6; /* Azul bebê */
    font-size: 2.5rem; /* Aumenta o tamanho */
}

/* Cor e tamanho dos subtítulos */
h3 {
    color: #84BBD6; /* Azul bebê */
}

/* Estilo do rótulo das métricas (KPIs) */
[data-testid="stMetricLabel"] {
    color: #84BBD6; /* Azul bebê */
    font-size: 1rem;
}

/* Estilo do valor das métricas (KPIs) */
[data-testid="stMetricValue"] {
    color: #E0E9F0; /* Azul escuro */
    font-size: 2.2rem;
    font-weight: bold;
}

/* Estilo dos botões de rádio */
[data-testid="stRadio"] label {
    font-size: 1rem;
    color: #84BBD6;
}

</style>
"""
st.markdown(estilo_css, unsafe_allow_html=True)


# --- FUNÇÃO PARA CARREGAR E PROCESSAR OS DADOS ---
@st.cache_data
def carregar_dados(caminho_arquivo):
    """
    Carrega e processa os dados do arquivo CSV.
    Extrai KPIs, dados para gráficos e tabelas.
    """
    df = pd.read_csv(caminho_arquivo, delimiter=';', encoding='latin1')
    
    # Limpeza inicial
    df.dropna(axis=1, how='all', inplace=True)
    df.columns = ['Tema Principal', 'Requisitos Necessarios', 'Presente', 'Ausente'] # Renomeia para padronização
    
    # --- Extração de KPIs e Dados Relevantes ---

    # 1. Pontuação Geral Final
    df_pontuacao_raw = df.copy()
    try:
        pontuacao_final = int(pd.to_numeric(df_pontuacao_raw[df_pontuacao_raw['Requisitos Necessarios'] == 'Pontuação Geral Final']['Presente'].iloc[0]))
    except (IndexError, ValueError):
        pontuacao_final = 0

    # 2. Classificação por Faixas
    df_faixas = df[df['Tema Principal'] == 'Classificação por Faixas'].copy()
    df_faixas[['Min', 'Max']] = df_faixas['Presente'].astype(str).str.split('-', expand=True)
    df_faixas['Min'] = pd.to_numeric(df_faixas['Min'], errors='coerce').fillna(0)
    df_faixas['Max'] = pd.to_numeric(df_faixas['Max'], errors='coerce').fillna(100)
    
    # 3. Classificação Atual
    classificacao_atual = 'Não definido'
    for _, row in df_faixas.iterrows():
        if row['Min'] <= pontuacao_final <= row['Max']:
            classificacao_atual = row['Requisitos Necessarios']
            break
            
    # Conversão principal para numérico
    df['Presente'] = pd.to_numeric(df['Presente'], errors='coerce').fillna(0).astype(int)
    df['Ausente'] = pd.to_numeric(df['Ausente'], errors='coerce').fillna(0).astype(int)

    # 4. Dataframe apenas com os requisitos avaliáveis
    df_requisitos = df[
        ~df['Requisitos Necessarios'].str.contains('Total', case=False, na=False) &
        (df['Presente'] + df['Ausente'] > 0) &
        (df['Tema Principal'].isin(['Análise do Desafio Tecnológico', 'Avaliação de Recursos e Metodologia', 'Indicadores de Projeto Rotineiro']))
    ].copy()
    
    # 5. Total de Requisitos Atendidos
    requisitos_atendidos = int(df_requisitos['Presente'].sum())
    total_requisitos = len(df_requisitos)

    # 6. Dataframe com os totais por tema
    df_totais_tema = df[df['Requisitos Necessarios'].str.contains('Total Geral', case=False, na=False)].copy()
    df_totais_tema['Tema Principal'] = df_totais_tema['Requisitos Necessarios'].str.replace('Total Geral ', '')


    return {
        'pontuacao_final': pontuacao_final,
        'classificacao_atual': classificacao_atual,
        'df_faixas': df_faixas,
        'requisitos_atendidos': requisitos_atendidos,
        'total_requisitos': total_requisitos,
        'df_requisitos': df_requisitos,
        'df_totais_tema': df_totais_tema
    }

# --- CARREGAMENTO DOS DADOS ---
try:
    dados = carregar_dados('grau-1.csv')

    # --- BARRA LATERAL (SIDEBAR) COM LOGO E FILTROS ---
    with st.sidebar:
        # Adiciona a logo no topo da barra lateral
        try:
            st.image("assets/logo.png", width=200)
        except FileNotFoundError:
            st.warning("Arquivo de logo 'assets/logo.png' não encontrado.")
        
      


    # --- TÍTULO DO DASHBOARD ---
    st.markdown("<h1 style='text-align: center;'>📊 Dashboard de Análise e Classificação de Projeto</h1>", unsafe_allow_html=True)
    st.markdown("---")

        # --- SEÇÃO DE KPIs ---
    # Colunas com larguras personalizadas ([menor, maior, menor])
    col1, col2, col3 = st.columns([2, 3, 2])

    with col1:
        # Métrica personalizada com HTML para centralização
        pontuacao_html = f"""
        <div style="text-align: center; line-height: 1.2;">
            <div style="font-size: 1rem; color: #84BBD6; margin-bottom: 5px;">
                <strong>🎯 Pontuação Geral</strong>
            </div>
            <div style="font-size: 2.2rem; font-weight: bold; color: #E0E9F0;">
                {dados['pontuacao_final']} Pontos
            </div>
        </div>
        """
        st.markdown(pontuacao_html, unsafe_allow_html=True)

    with col2:
        # Métrica personalizada com HTML para centralização e quebra de linha
        classificacao_html = f"""
        <div style="text-align: center; line-height: 1.2;">
            <div style="font-size: 1rem; color: #84BBD6; margin-bottom: 5px;">
                <strong>🏆 Classificação do Projeto</strong>
            </div>
            <div style="font-size: 2.2rem; font-weight: bold; color: #E0E9F0;">
                {dados['classificacao_atual']}
            </div>
        </div>
        """
        st.markdown(classificacao_html, unsafe_allow_html=True)

    with col3:
        # Métrica personalizada com HTML para centralização
        requisitos_html = f"""
        <div style="text-align: center; line-height: 1.2;">
            <div style="font-size: 1rem; color: #84BBD6; margin-bottom: 5px;">
                <strong>✅ Requisitos Atendidos</strong>
            </div>
            <div style="font-size: 2.2rem; font-weight: bold; color: #E0E9F0;">
                {dados['requisitos_atendidos']} de {dados['total_requisitos']}
            </div>
        </div>
        """
        st.markdown(requisitos_html, unsafe_allow_html=True)

    st.markdown("---")

    # --- FILTROS NA BARRA LATERAL ---
    with st.sidebar:
        st.markdown("## **Filtros de Análise**")
        temas_unicos = dados['df_requisitos']['Tema Principal'].unique()
        temas_selecionados = st.multiselect("Filtrar por Tema Principal:", options=temas_unicos, default=temas_unicos)
        status_selecionado = st.radio("Filtrar por Status:", options=["Todos", "Apenas Presentes", "Apenas Ausentes"], horizontal=True)

    # --- APLICAÇÃO DOS FILTROS ---
    df_filtrado = dados['df_requisitos']
    if temas_selecionados:
        df_filtrado = df_filtrado[df_filtrado['Tema Principal'].isin(temas_selecionados)]
    if status_selecionado == "Apenas Presentes":
        df_filtrado = df_filtrado[df_filtrado['Presente'] > 0]
    elif status_selecionado == "Apenas Ausentes":
        df_filtrado = df_filtrado[df_filtrado['Presente'] == 0]

    # --- SEÇÃO DE GRÁFICOS ---
    col_graf1, col_graf2 = st.columns(2)

    with col_graf1:
        st.markdown("### **Pontuação por Tema Principal**")
        fig_barras = px.bar(
            dados['df_totais_tema'], x='Presente', y='Tema Principal', orientation='h',
            text='Presente', color='Tema Principal', color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_barras.update_layout(showlegend=False, yaxis_title=None, xaxis_title="Pontuação", template="plotly_white", 
        autosize=True, margin=dict(l=10, r=10, t=10, b=10), height=350,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#84BBD6'
        )
        
        fig_barras.update_traces(textposition='inside')
        st.plotly_chart(fig_barras, use_container_width=True, config={'displayModeBar': False})

        st.markdown("### **Proporção de Requisitos**")
        df_donut = pd.DataFrame({
            'Status': ['Presente', 'Ausente'],
            'Quantidade': [dados['requisitos_atendidos'], dados['total_requisitos'] - dados['requisitos_atendidos']]
        })
        fig_donut = px.pie(
            df_donut, names='Status', values='Quantidade', hole=0.5,
            color='Status', color_discrete_map={'Presente': 'mediumseagreen', 'Ausente': 'lightcoral'}
        )
        fig_donut.update_traces(textinfo='percent+label', pull=[0.05, 0])
        fig_donut.update_layout(
            showlegend=False, height=350, margin=dict(t=20, b=20, l=20, r=20),
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#84BBD6'
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    with col_graf2:
        st.markdown("### **Medidor de Classificação Geral**")
        max_score = dados['df_faixas']['Max'].max()
        
        # --- CORREÇÃO APLICADA AQUI ---
        # A lista de cores e a iteração no zip foram ajustadas
        
        cores_faixas = ['#2ECC71', '#F1C40F', '#E74C3C', '#9B59B6'] # Verde, Amarelo, Vermelho, Roxo
        
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=dados['pontuacao_final'],
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [0, max_score], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': "darkblue"},
                'bgcolor': "rgba(0,0,0,0)",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [row['Min'], row['Max']], 'color': color} 
                    for (_, row), color in zip(dados['df_faixas'].iterrows(), cores_faixas)
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': dados['pontuacao_final']}}))
        # --- FIM DA CORREÇÃO ---

        fig_gauge.update_layout(
            height=350, margin=dict(t=20, b=40, l=40, r=40),
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#84BBD6'
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

    # --- SEÇÃO DA TABELA DE DETALHES ---
    st.markdown("### **Detalhamento dos Requisitos Avaliados**")
    st.dataframe(df_filtrado, use_container_width=True, hide_index=True)

    # --- FOOTER ---
    st.markdown("---")
    st.markdown("<p style='text-align: center; color: #84BBD6;'>Todos os direitos reservados @brockdesigner</p>", unsafe_allow_html=True)

except FileNotFoundError:
    st.error("Erro: Arquivo `grau-1.csv` não encontrado. Por favor, certifique-se que o arquivo está no mesmo diretório que o script.")
except Exception as e:
    st.error(f"Ocorreu um erro inesperado ao processar os dados: {e}")