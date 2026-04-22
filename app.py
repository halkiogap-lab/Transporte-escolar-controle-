import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# --- CONFIGURAÇÃO DO BANCO DE DADOS ---
def criar_banco():
    conn = sqlite3.connect('dados_transporte.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS alunos 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, endereco TEXT, turno TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS presenca 
                 (id_aluno INTEGER, data TEXT, status INTEGER, PRIMARY KEY (id_aluno, data))''')
    conn.commit()
    conn.close()

def carregar_alunos():
    conn = sqlite3.connect('dados_transporte.db')
    df = pd.read_sql_query("SELECT * FROM alunos ORDER BY nome ASC", conn)
    conn.close()
    return df

def carregar_presenca(data):
    conn = sqlite3.connect('dados_transporte.db')
    df = pd.read_sql_query(f"SELECT id_aluno FROM presenca WHERE data = '{data}' AND status = 1", conn)
    conn.close()
    return df['id_aluno'].tolist()

# --- INICIALIZAÇÃO ---
criar_banco()
st.set_page_config(page_title="Van Escolar Pro", layout="wide")

# Carga Inicial de Alunos (Só roda se o banco estiver vazio)
df_atual = carregar_alunos()
if df_atual.empty:
    LISTA_NOMES = ["Abel Bernardo", "Adeli da Silva", "Alice Andrade", "Alice Bernardes", "Alicia da Silva", "Allyce Gonçalves", "Amaya Rocha", "Ana Beatriz Neves", "Ana Clara Neves", "Ana Gabrielly", "Ana Liz Cardoso", "Analice Marques", "Anna Elisa Delpuppo", "Anna Jhullya Bastos", "Anna Laura", "Anna Vitória Pereira", "Anthony Gabriel", "Anthony Miguel Vauna", "Anthony Nascimento", "Apolo da Silva", "Arthur Charles", "Arthur Portugal", "Asaphe Lima", "Cecília de Souza", "Claricy Guimarães", "Cristyan Silva", "Davi Lucca Nery", "Diogo Soares", "Elisa Soares", "Eloáh Silva", "Elyza Reami", "Emanuelly Machado", "Emílio Sena", "Enzo Victor", "Esther Cristina", "Fernando Arthur", "Gabriel Chagas", "Gael Alfredo", "Gael Santos", "Gael Vauna", "Geferson Lorenzo", "Giúlia Rosa", "Hector Felipe", "Heitor Ávila", "Heitor da Silva", "Heitor de Almeida", "Helena Rocha", "Hillary Almeida", "Hillary Victoria", "Ícaro Samuel", "Isabel Barbosa", "Isabela Ribeiro", "Isabela Valverde", "Isadora Ferreira", "Isaque Serafim", "Ísis Xaviex", "Itallo Matheus", "Jhenyt Rebeka", "Jhulya Ferreira", "Jhulia Vitória de Souza", "João Vitor Alves", "Kailany Toledo", "Kalleb Santos", "Kauã Gabriel", "Kaue de Sonza", "Laura Ferraz", "Lavinia Viera", "Léo Victor", "Lívia Lopes", "Lívia Silveira", "Liz Leonora", "Lorenzo Olegário", "Luiz Eduardo Lima", "Luisa Negrelli", "Luyz Fernando", "Maitê Araújo", "Maitê Fuzari", "Maitê Moreira", "Manuela Barbosa", "Maria Alice Toneti", "Maria Antonia", "Maria Cecília Moraes", "Maria Eduarda Miranda", "Maria Flor Dias", "Maria Heloísa Santos", "Maria Julia Lubase", "Maria Luiza", "Maria Vitória Fagundes", "Maria Vitória Miranda", "Matheus Henrique L", "Maxsuel Fagundes", "Maysa Vitoria", "Mikaela de Souza", "Milena Ferreira", "Miguel Joaquim", "Miguel Pereira", "Mirella de Souza", "Murilo Pereira", "Nathyelle Zanon", "Neymar Junior", "Nicolas Gomes", "Nicolas Silveira", "Otto Miguel", "Paulo Daniel", "Rafaela Costa", "Ravi Pereira", "Rayner Renovatto", "Rayssa Severino", "Rhiana Rangel", "Samara Vaz", "Samara Vitória", "Sarah Buzato", "Sofia Santos", "Sofia Vitória", "Sophia Amaral", "Sophia Cardoso", "Talles Emanuel", "Thallya Malta", "Théo Nascimento", "Vitora Bernandes", "Wallace Andrade", "Wathila Correa", "Yuri Paiva"]
    conn = sqlite3.connect('dados_transporte.db')
    for nome in LISTA_NOMES:
        conn.execute("INSERT INTO alunos (nome, endereco, turno) VALUES (?, ?, ?)", (nome, "", "pendente"))
    conn.commit()
    conn.close()
    df_atual = carregar_alunos()

# --- MENU LATERAL ---
st.sidebar.title("🚐 Controle Van")
aba = st.sidebar.radio("Navegação", ["✅ Chamada", "📍 Rota", "⚙️ Configurar Alunos", "➕ Novo Aluno"])

# --- 1. CHAMADA ---
if aba == "✅ Chamada":
    st.header("✅ Chamada do Dia")
    data_hoje = datetime.now().strftime("%Y-%m-%d")
    turno = st.radio("Turno", ["matutino", "vespertino"], horizontal=True)
    
    alunos_turno = df_atual[df_atual['turno'] == turno]
    presentes_ids = carregar_presenca(data_hoje)
    
    if alunos_turno.empty:
        st.warning(f"Nenhum aluno no turno {turno}. Configure em 'Configurar Alunos'.")
    else:
        for _, row in alunos_turno.iterrows():
            c1, c2 = st.columns([3, 1])
            c1.write(f"**{row['nome']}**")
            # Salva na hora que clica
            check = c2.checkbox("Presente", value=(row['id'] in presentes_ids), key=f"p_{row['id']}")
            status = 1 if check else 0
            conn = sqlite3.connect('dados_transporte.db')
            conn.execute("INSERT OR REPLACE INTO presenca (id_aluno, data, status) VALUES (?, ?, ?)", (row['id'], data_hoje, status))
            conn.commit()
            conn.close()

# --- 2. ROTA ---
elif aba == "📍 Rota":
    st.header("📍 Rota de Coleta")
    data_hoje = datetime.now().strftime("%Y-%m-%d")
    presentes_ids = carregar_presenca(data_hoje)
    
    rota = df_atual[df_atual['id'].isin(presentes_ids)]
    
    if rota.empty:
        st.info("Marque quem está 'Presente' na chamada primeiro.")
    else:
        for _, row in rota.iterrows():
            with st.expander(f"🏠 {row['nome']}"):
                if row['endereco']:
                    st.write(f"Endereço: {row['endereco']}")
                    url = f"https://www.google.com/maps/search/?api=1&query={row['endereco'].replace(' ', '+')}"
                    st.link_button("Abrir no GPS", url)
                else:
                    st.error("Endereço não cadastrado!")

# --- 3. CONFIGURAR (SALVA ENDEREÇOS E TURNOS) ---
elif aba == "⚙️ Configurar Alunos":
    st.header("⚙️ Configurar Endereços e Turnos")
    st.info("Preencha e clique no botão 'SALVAR TUDO' no final da página.")
    
    with st.form("form_config"):
        # Criamos dicionários para capturar os novos valores
        novos_dados = []
        for index, row in df_atual.iterrows():
            st.write(f"**{row['nome']}**")
            c1, c2 = st.columns([1, 2])
            t = c1.selectbox("Turno", ["pendente", "matutino", "vespertino"], 
                            index=["pendente", "matutino", "vespertino"].index(row['turno']),
                            key=f"t_{row['id']}")
            e = c2.text_input("Endereço", value=row['endereco'], key=f"e_{row['id']}")
            novos_dados.append((e, t, row['id']))
            st.divider()
        
        if st.form_submit_button("💾 SALVAR TUDO"):
            conn = sqlite3.connect('dados_transporte.db')
            conn.executemany("UPDATE alunos SET endereco = ?, turno = ? WHERE id = ?", novos_dados)
            conn.commit()
            conn.close()
            st.success("Dados salvos com sucesso!")
            st.rerun()

# --- 4. NOVO ALUNO (CORRIGIDO) ---
elif aba == "➕ Novo Aluno":
    st.header("➕ Cadastrar Novo Aluno")
    with st.form("form_novo_aluno"):
        nome_n = st.text_input("Nome Completo da Criança")
        end_n = st.text_input("Endereço")
        turno_n = st.selectbox("Turno", ["matutino", "vespertino", "pendente"])
        
        # O botão que estava faltando
        submit_n = st.form_submit_button("Adicionar Aluno")
        
        if submit_n:
            if nome_n:
                conn = sqlite3.connect('dados_transporte.db')
                conn.execute("INSERT INTO alunos (nome, endereco, turno) VALUES (?, ?, ?)", (nome_n, end_n, turno_n))
                conn.commit()
                conn.close()
                st.success(f"{nome_n} adicionado!")
                st.rerun()
            else:
                st.error("Digite o nome do aluno.")
