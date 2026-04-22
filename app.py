import streamlit as st
import pandas as pd
from datetime import datetime

# Configuração visual para não ficar "um lixo"
st.set_page_config(page_title="Transporte Escolar Pro", layout="wide", initial_sidebar_state="expanded")

# Estilo personalizado para botões grandes
st.markdown("""
    <style>
    .stButton>button { width: 100%; height: 3em; font-size: 1.2em; }
    [data-testid="stMetricValue"] { font-size: 2em; color: #ff4b4b; }
    </style>
    """, unsafe_allow_html=True)

# LISTA COMPLETA DE ALUNOS (OPÇÃO 3 - CARGA AUTOMÁTICA)
LISTA_NOMES = [
    "Abel Bernardo", "Adeli da Silva", "Alice Andrade", "Alice Bernardes", "Alicia da Silva",
    "Allyce Gonçalves", "Amaya Rocha", "Ana Beatriz Neves", "Ana Clara Neves", "Ana Gabrielly",
    "Ana Liz Cardoso", "Analice Marques", "Anna Elisa Delpuppo", "Anna Jhullya Bastos",
    "Anna Laura", "Anna Vitória Pereira", "Anthony Gabriel", "Anthony Miguel Vauna",
    "Anthony Nascimento", "Apolo da Silva", "Arthur Charles", "Arthur Portugal", "Asaphe Lima",
    "Cecília de Souza", "Claricy Guimarães", "Cristyan Silva", "Davi Lucca Nery", "Diogo Soares",
    "Elisa Soares", "Eloáh Silva", "Elyza Reami", "Emanuelly Machado", "Emílio Sena",
    "Enzo Victor", "Esther Cristina", "Fernando Arthur", "Gabriel Chagas", "Gael Alfredo",
    "Gael Santos", "Gael Vauna", "Geferson Lorenzo", "Giúlia Rosa", "Hector Felipe",
    "Heitor Ávila", "Heitor da Silva", "Heitor de Almeida", "Helena Rocha", "Hillary Almeida",
    "Hillary Victoria", "Ícaro Samuel", "Isabel Barbosa", "Isabela Ribeiro", "Isabela Valverde",
    "Isadora Ferreira", "Isaque Serafim", "Ísis Xaviex", "Itallo Matheus", "Jhenyt Rebeka",
    "Jhulya Ferreira", "Jhulia Vitória de Souza", "João Vitor Alves", "Kailany Toledo",
    "Kalleb Santos", "Kauã Gabriel", "Kaue de Sonza", "Laura Ferraz", "Lavinia Viera",
    "Léo Victor", "Lívia Lopes", "Lívia Silveira", "Liz Leonora", "Lorenzo Olegário",
    "Luiz Eduardo Lima", "Luisa Negrelli", "Luyz Fernando", "Maitê Araújo", "Maitê Fuzari",
    "Maitê Moreira", "Manuela Barbosa", "Maria Alice Toneti", "Maria Antonia", "Maria Cecília Moraes",
    "Maria Eduarda Miranda", "Maria Flor Dias", "Maria Heloísa Santos", "Maria Julia Lubase",
    "Maria Luiza", "Maria Vitória Fagundes", "Maria Vitória Miranda", "Matheus Henrique L",
    "Maxsuel Fagundes", "Maysa Vitoria", "Mikaela de Souza", "Milena Ferreira", "Miguel Joaquim",
    "Miguel Pereira", "Mirella de Souza", "Murilo Pereira", "Nathyelle Zanon", "Neymar Junior",
    "Nicolas Gomes", "Nicolas Silveira", "Otto Miguel", "Paulo Daniel", "Rafaela Costa",
    "Ravi Pereira", "Rayner Renovatto", "Rayssa Severino", "Rhiana Rangel", "Samara Vaz",
    "Samara Vitória", "Sarah Buzato", "Sofia Santos", "Sofia Vitória", "Sophia Amaral",
    "Sophia Cardoso", "Talles Emanuel", "Thallya Malta", "Théo Nascimento", "Vitora Bernandes",
    "Wallace Andrade", "Wathila Correa", "Yuri Paiva"
]

# Inicialização do Banco de Dados
if 'children' not in st.session_state:
    # Carrega a lista automaticamente na primeira vez
    st.session_state.children = [
        {"id": i, "name": nome, "defaultAddress": "", "notes": "", "shift": "pendente"} 
        for i, nome in enumerate(LISTA_NOMES)
    ]
if 'attendance' not in st.session_state:
    st.session_state.attendance = {}

# --- NAVEGAÇÃO ---
st.sidebar.title("🚐 Menu")
choice = st.sidebar.radio("Ir para:", ["📊 Resumo", "✅ Chamada/Presença", "📍 Rota de Busca", "⚙️ Organizar Turnos"])

# 1. RESUMO
if choice == "📊 Resumo":
    st.header("📊 Painel de Controle")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Alunos", len(st.session_state.children))
    col2.metric("Matutino", sum(1 for c in st.session_state.children if c['shift'] == 'matutino'))
    col3.metric("Vespertino", sum(1 for c in st.session_state.children if c['shift'] == 'vespertino'))
    
    st.subheader("Lista Completa")
    df = pd.DataFrame(st.session_state.children)
    st.table(df[['name', 'shift']])

# 2. CHAMADA (Aqui é onde o bicho pega no dia a dia)
elif choice == "✅ Chamada/Presença":
    st.header("✅ Chamada Diária")
    turno = st.selectbox("Escolha o Turno para a Chamada", ["matutino", "vespertino", "pendente"])
    data_hoje = datetime.now().strftime("%Y-%m-%d")
    
    alunos_filtrados = [c for c in st.session_state.children if c['shift'] == turno]
    
    if not alunos_filtrados:
        st.warning(f"Não há alunos definidos como '{turno}'. Vá em 'Organizar Turnos'.")
    else:
        for aluno in alunos_filtrados:
            col_n, col_b = st.columns([2, 1])
            col_n.write(f"### {aluno['name']}")
            
            # Chave única para o botão
            key = f"att_{data_hoje}_{aluno['id']}"
            status = col_b.radio("Status", ["Faltou", "Presente"], key=key, horizontal=True)
            st.session_state.attendance[key] = status
            st.divider()

# 3. ROTA DE BUSCA
elif choice == "📍 Rota de Busca":
    st.header("📍 Rota de Coleta")
    data_hoje = datetime.now().strftime("%Y-%m-%d")
    
    lista_rota = []
    for aluno in st.session_state.children:
        if st.session_state.attendance.get(f"att_{data_hoje}_{aluno['id']}") == "Presente":
            lista_rota.append(aluno)
            
    if not lista_rota:
        st.info("Nenhum aluno marcado como 'Presente' ainda.")
    else:
        for i, aluno in enumerate(lista_rota, 1):
            with st.expander(f"{i}º - {aluno['name']}"):
                st.write(f"🏠 Endereço: {aluno['defaultAddress'] if aluno['defaultAddress'] else 'Não cadastrado'}")
                if st.button(f"Abrir no GPS: {aluno['name']}", key=f"gps_{aluno['id']}"):
                    st.write(f"Abrindo Google Maps para: {aluno['defaultAddress']}...")

# 4. ORGANIZAR TURNOS (Manual para não dar erro)
elif choice == "⚙️ Organizar Turnos":
    st.header("⚙️ Configuração Manual")
    st.write("Defina aqui quem é da manhã e quem é da tarde.")
    
    for i, aluno in enumerate(st.session_state.children):
        col1, col2 = st.columns([2, 1])
        col1.write(aluno['name'])
        novo_turno = col2.selectbox("", ["pendente", "matutino", "vespertino"], 
                                   index=["pendente", "matutino", "vespertino"].index(aluno['shift']),
                                   key=f"shift_{aluno['id']}")
        st.session_state.children[i]['shift'] = novo_turno
