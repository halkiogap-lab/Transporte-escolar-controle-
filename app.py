import streamlit as st
import pandas as pd
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Transporte Escolar Pro", layout="wide")

# Estilo para botões e campos
st.markdown("""
    <style>
    .stTextInput>div>div>input { background-color: #262730; color: white; border: 1px solid #4b4b4b; }
    .stSelectbox>div>div { background-color: #262730; }
    </style>
    """, unsafe_allow_html=True)

# LISTA OFICIAL DE ALUNOS
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

# Inicialização do Banco de Dados na memória
if 'children' not in st.session_state:
    st.session_state.children = [
        {"id": i, "name": nome, "defaultAddress": "", "shift": "pendente"} 
        for i, nome in enumerate(LISTA_NOMES)
    ]
if 'attendance' not in st.session_state:
    st.session_state.attendance = {}

# MENU LATERAL
st.sidebar.title("🚐 Van Escolar")
choice = st.sidebar.radio("Navegação", ["📊 Resumo", "✅ Chamada", "📍 Rota de Hoje", "⚙️ Cadastrar Endereços"])

# 1. RESUMO
if choice == "📊 Resumo":
    st.header("📊 Resumo Geral")
    col1, col2 = st.columns(2)
    col1.metric("Total Alunos", len(st.session_state.children))
    col2.metric("Endereços Salvos", sum(1 for c in st.session_state.children if c['defaultAddress'] != ""))

# 2. CHAMADA
elif choice == "✅ Chamada":
    st.header("✅ Chamada do Dia")
    turno = st.radio("Selecione o Turno", ["matutino", "vespertino"], horizontal=True)
    data_hoje = datetime.now().strftime("%Y-%m-%d")
    
    alunos_turno = [c for c in st.session_state.children if c['shift'] == turno]
    
    if not alunos_turno:
        st.warning(f"Nenhum aluno no turno {turno}. Use a aba 'Cadastrar Endereços' primeiro.")
    else:
        for aluno in alunos_turno:
            c1, c2 = st.columns([2, 1])
            c1.write(f"**{aluno['name']}**")
            key = f"att_{data_hoje}_{aluno['id']}"
            st.session_state.attendance[key] = c2.checkbox("Presente", key=key)

# 3. ROTA
elif choice == "📍 Rota de Hoje":
    st.header("📍 Rota de Coleta")
    data_hoje = datetime.now().strftime("%Y-%m-%d")
    
    presentes = [c for c in st.session_state.children if st.session_state.attendance.get(f"att_{data_hoje}_{c['id']}") == True]
    
    if not presentes:
        st.info("Ninguém marcado como 'Presente' ainda.")
    else:
        for p in presentes:
            with st.expander(f"🏠 {p['name']}"):
                if p['defaultAddress']:
                    st.write(f"Endereço: {p['defaultAddress']}")
                    url = f"https://www.google.com/maps/search/?api=1&query={p['defaultAddress'].replace(' ', '+')}"
                    st.link_button("Abrir no GPS", url)
                else:
                    st.error("Endereço não cadastrado!")

# 4. CADASTRAR ENDEREÇOS (AQUI VOCÊ SALVA TUDO!)
elif choice == "⚙️ Cadastrar Endereços":
    st.header("⚙️ Cadastro de Endereços e Turnos")
    st.write("Preencha as informações abaixo. O app salva automaticamente conforme você digita.")
    
    for i, aluno in enumerate(st.session_state.children):
        with st.container():
            st.write(f"### {aluno['name']}")
            col1, col2 = st.columns([1, 2])
            
            # Campo de Turno
            novo_turno = col1.selectbox("Turno", ["pendente", "matutino", "vespertino"], 
                                       index=["pendente", "matutino", "vespertino"].index(aluno['shift']),
                                       key=f"sh_{aluno['id']}")
            
            # CAMPO DE ENDEREÇO (QUE ESTAVA FALTANDO!)
            novo_endereco = col2.text_input("Endereço da Casa (Rua, Número, Bairro)", 
                                           value=aluno['defaultAddress'],
                                           key=f"ad_{aluno['id']}")
            
            # Atualiza os dados
            st.session_state.children[i]['shift'] = novo_turno
            st.session_state.children[i]['defaultAddress'] = novo_endereco
            st.divider()
