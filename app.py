import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# --- CONFIGURAÇÃO DO BANCO DE DADOS (O QUE SALVA DE VERDADE) ---
def criar_banco():
    conn = sqlite3.connect('dados_transporte.db')
    c = conn.cursor()
    # Tabela de alunos
    c.execute('''CREATE TABLE IF NOT EXISTS alunos 
                 (id INTEGER PRIMARY KEY, nome TEXT, endereco TEXT, turno TEXT)''')
    # Tabela de presença
    c.execute('''CREATE TABLE IF NOT EXISTS presenca 
                 (id_aluno INTEGER, data TEXT, status INTEGER)''')
    conn.commit()
    conn.close()

def carregar_alunos():
    conn = sqlite3.connect('dados_transporte.db')
    df = pd.read_sql_query("SELECT * FROM alunos", conn)
    conn.close()
    return df

def salvar_aluno(id_aluno, endereco, turno):
    conn = sqlite3.connect('dados_transporte.db')
    c = conn.cursor()
    c.execute("UPDATE alunos SET endereco = ?, turno = ? WHERE id = ?", (endereco, turno, id_aluno))
    conn.commit()
    conn.close()

def marcar_presenca(id_aluno, data, status):
    conn = sqlite3.connect('dados_transporte.db')
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO presenca (id_aluno, data, status) VALUES (?, ?, ?)", 
              (id_aluno, data, status))
    conn.commit()
    conn.close()

def get_presenca(data):
    conn = sqlite3.connect('dados_transporte.db')
    df = pd.read_sql_query(f"SELECT id_aluno FROM presenca WHERE data = '{data}' AND status = 1", conn)
    conn.close()
    return df['id_aluno'].tolist()

# --- INICIALIZAÇÃO ---
criar_banco()
st.set_page_config(page_title="Van Escolar Pro", layout="wide")

# Lista inicial de nomes (só insere se o banco estiver vazio)
df_existente = carregar_alunos()
if df_existente.empty:
    LISTA_NOMES = ["Abel Bernardo", "Adeli da Silva", "Alice Andrade", "Alice Bernardes", "Alicia da Silva", "Allyce Gonçalves", "Amaya Rocha", "Ana Beatriz Neves", "Ana Clara Neves", "Ana Gabrielly", "Ana Liz Cardoso", "Analice Marques", "Anna Elisa Delpuppo", "Anna Jhullya Bastos", "Anna Laura", "Anna Vitória Pereira", "Anthony Gabriel", "Anthony Miguel Vauna", "Anthony Nascimento", "Apolo da Silva", "Arthur Charles", "Arthur Portugal", "Asaphe Lima", "Cecília de Souza", "Claricy Guimarães", "Cristyan Silva", "Davi Lucca Nery", "Diogo Soares", "Elisa Soares", "Eloáh Silva", "Elyza Reami", "Emanuelly Machado", "Emílio Sena", "Enzo Victor", "Esther Cristina", "Fernando Arthur", "Gabriel Chagas", "Gael Alfredo", "Gael Santos", "Gael Vauna", "Geferson Lorenzo", "Giúlia Rosa", "Hector Felipe", "Heitor Ávila", "Heitor da Silva", "Heitor de Almeida", "Helena Rocha", "Hillary Almeida", "Hillary Victoria", "Ícaro Samuel", "Isabel Barbosa", "Isabela Ribeiro", "Isabela Valverde", "Isadora Ferreira", "Isaque Serafim", "Ísis Xaviex", "Itallo Matheus", "Jhenyt Rebeka", "Jhulya Ferreira", "Jhulia Vitória de Souza", "João Vitor Alves", "Kailany Toledo", "Kalleb Santos", "Kauã Gabriel", "Kaue de Sonza", "Laura Ferraz", "Lavinia Viera", "Léo Victor", "Lívia Lopes", "Lívia Silveira", "Liz Leonora", "Lorenzo Olegário", "Luiz Eduardo Lima", "Luisa Negrelli", "Luyz Fernando", "Maitê Araújo", "Maitê Fuzari", "Maitê Moreira", "Manuela Barbosa", "Maria Alice Toneti", "Maria Antonia", "Maria Cecília Moraes", "Maria Eduarda Miranda", "Maria Flor Dias", "Maria Heloísa Santos", "Maria Julia Lubase", "Maria Luiza", "Maria Vitória Fagundes", "Maria Vitória Miranda", "Matheus Henrique L", "Maxsuel Fagundes", "Maysa Vitoria", "Mikaela de Souza", "Milena Ferreira", "Miguel Joaquim", "Miguel Pereira", "Mirella de Souza", "Murilo Pereira", "Nathyelle Zanon", "Neymar Junior", "Nicolas Gomes", "Nicolas Silveira", "Otto Miguel", "Paulo Daniel", "Rafaela Costa", "Ravi Pereira", "Rayner Renovatto", "Rayssa Severino", "Rhiana Rangel", "Samara Vaz", "Samara Vitória", "Sarah Buzato", "Sofia Santos", "Sofia Vitória", "Sophia Amaral", "Sophia Cardoso", "Talles Emanuel", "Thallya Malta", "Théo Nascimento", "Vitora Bernandes", "Wallace Andrade", "Wathila Correa", "Yuri Paiva"]
    conn = sqlite3.connect('dados_transporte.db')
    for nome in LISTA_NOMES:
        conn.execute("INSERT INTO alunos (nome, endereco, turno) VALUES (?, ?, ?)", (nome, "", "pendente"))
    conn.commit()
    conn.close()
    df_existente = carregar_alunos()

# --- MENU ---
st.sidebar.title("🚐 Controle Van")
aba = st.sidebar.radio("Ir para:", ["✅ Chamada", "📍 Rota", "⚙️ Configurar Alunos"])

# 1. CHAMADA
if aba == "✅ Chamada":
    st.header("Chamada do Dia")
    data_hoje = datetime.now().strftime("%Y-%m-%d")
    turno = st.radio("Turno", ["matutino", "vespertino"], horizontal=True)
    
    alunos = df_existente[df_existente['turno'] == turno]
    presentes_hoje = get_presenca(data_hoje)
    
    for _, row in alunos.iterrows():
        c1, c2 = st.columns([3, 1])
        c1.write(f"**{row['nome']}**")
        is_p = c2.checkbox("Presente", value=(row['id'] in presentes_hoje), key=f"p_{row['id']}")
        marcar_presenca(row['id'], data_hoje, 1 if is_p else 0)

# 2. ROTA
elif aba == "📍 Rota":
    st.header("📍 Lista de Busca")
    data_hoje = datetime.now().strftime("%Y-%m-%d")
    presentes_ids = get_presenca(data_hoje)
    
    rota = df_existente[df_existente['id'].isin(presentes_ids)]
    
    if rota.empty:
        st.info("Ninguém marcado como presente.")
    else:
        for _, row in rota.iterrows():
            with st.expander(f"🏠 {row['nome']}"):
                st.write(f"Endereço: {row['endereco']}")
                if row['endereco']:
                    url = f"https://www.google.com/maps/search/?api=1&query={row['endereco'].replace(' ', '+')}"
                    st.link_button("Abrir GPS", url)

# 3. CONFIGURAR (ONDE SALVA TUDO)
elif aba == "⚙️ Configurar Alunos":
    st.header("Configurar Endereços e Turnos")
    st.info("Preencha e clique em 'SALVAR TUDO' no final da página.")
    
    with st.form("form_config"):
        for index, row in df_existente.iterrows():
            st.write(f"**{row['nome']}**")
            c1, c2 = st.columns([1, 2])
            turno_val = c1.selectbox("Turno", ["pendente", "matutino", "vespertino"], 
                                    index=["pendente", "matutino", "vespertino"].index(row['turno']),
                                    key=f"t_{row['id']}")
            end_val = c2.text_input("Endereço", value=row['endereco'], key=f"e_{row['id']}")
            
            # Guardamos os valores para salvar depois do clique
            df_existente.at[index, 'turno'] = turno_val
            df_existente.at[index, 'endereco'] = end_val
            st.divider()
        
        if st.form_submit_button("💾 SALVAR TUDO"):
            for _, r in df_existente.iterrows():
                salvar_aluno(r['id'], r['endereco'], r['turno'])
            st.success("Dados salvos com sucesso no banco de dados!")
            st.rerun()
