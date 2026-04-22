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
    # Adicionada coluna 'hora_entrega' na tabela de presenca
    c.execute('''CREATE TABLE IF NOT EXISTS presenca 
                 (id_aluno INTEGER, data TEXT, status INTEGER, hora_entrega TEXT, PRIMARY KEY (id_aluno, data))''')
    conn.commit()
    conn.close()

def carregar_alunos():
    conn = sqlite3.connect('dados_transporte.db')
    df = pd.read_sql_query("SELECT * FROM alunos ORDER BY nome ASC", conn)
    conn.close()
    return df

def carregar_presenca_detalhada(data):
    conn = sqlite3.connect('dados_transporte.db')
    df = pd.read_sql_query(f"SELECT * FROM presenca WHERE data = '{data}'", conn)
    conn.close()
    return df

# --- INICIALIZAÇÃO ---
criar_banco()
st.set_page_config(page_title="Van Escolar Pro", layout="wide")

df_atual = carregar_alunos()
# Carga inicial (mesma lista de 125 nomes)
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
data_selecionada = st.sidebar.date_input("📅 Calendário", datetime.now())
data_str = data_selecionada.strftime("%Y-%m-%d")

aba = st.sidebar.radio("Navegação", ["✅ Chamada", "📍 Rota e Entrega", "⚙️ Configurar Alunos", "➕ Novo Aluno"])

# --- 1. CHAMADA (Limpada Diariamente via Calendário) ---
if aba == "✅ Chamada":
    st.header(f"✅ Chamada - Dia {data_selecionada.strftime('%d/%m/%Y')}")
    turno = st.radio("Turno", ["matutino", "vespertino"], horizontal=True)
    
    alunos_turno = df_atual[df_atual['turno'] == turno]
    presenca_data = carregar_presenca_detalhada(data_str)
    presentes_ids = presenca_data[presenca_data['status'] == 1]['id_aluno'].tolist()
    
    if alunos_turno.empty:
        st.warning("Nenhum aluno neste turno.")
    else:
        for _, row in alunos_turno.iterrows():
            c1, c2 = st.columns([3, 1])
            c1.write(f"**{row['nome']}**")
            check = c2.checkbox("Presente", value=(row['id'] in presentes_ids), key=f"p_{data_str}_{row['id']}")
            
            if check != (row['id'] in presentes_ids):
                status = 1 if check else 0
                conn = sqlite3.connect('dados_transporte.db')
                conn.execute("INSERT OR REPLACE INTO presenca (id_aluno, data, status, hora_entrega) VALUES (?, ?, ?, ?)", 
                             (row['id'], data_str, status, ""))
                conn.commit()
                conn.close()
                st.rerun()

# --- 2. ROTA E ENTREGA (Com botão Finalizar e Relatório) ---
elif aba == "📍 Rota e Entrega":
    st.header(f"📍 Rota - {data_selecionada.strftime('%d/%m/%Y')}")
    presenca_data = carregar_presenca_detalhada(data_str)
    presentes_ids = presenca_data[presenca_data['status'] == 1]['id_aluno'].tolist()
    
    rota = df_atual[df_atual['id'].isin(presentes_ids)]
    
    if rota.empty:
        st.info("Nenhum aluno marcado como presente hoje.")
    else:
        for _, row in rota.iterrows():
            with st.expander(f"🏠 {row['nome']}"):
                st.write(f"Endereço: {row['endereco']}")
                # Registrar Hora da Entrega
                hora_atual = presenca_data[presenca_data['id_aluno'] == row['id']]['hora_entrega'].values[0]
                if not hora_atual:
                    if st.button(f"Confirmar Entrega: {row['nome']}", key=f"ent_{row['id']}"):
                        h_agora = datetime.now().strftime("%H:%M")
                        conn = sqlite3.connect('dados_transporte.db')
                        conn.execute("UPDATE presenca SET hora_entrega = ? WHERE id_aluno = ? AND data = ?", (h_agora, row['id'], data_str))
                        conn.commit()
                        conn.close()
                        st.rerun()
                else:
                    st.success(f"Entregue às {hora_atual}")

        st.divider()
        if st.button("🏁 FINALIZAR E GERAR RELATÓRIO", type="primary"):
            st.subheader("📋 Relatório de Encerramento")
            hora_gen = datetime.now().strftime("%H:%M")
            
            # Construindo o texto do relatório
            texto_relatorio = f"🚌 RELATÓRIO VAN - DATA: {data_str} às {hora_gen}\n\n"
            texto_relatorio += "✅ PRESENTES:\n"
            
            for _, r in rota.iterrows():
                h_ent = presenca_data[presenca_data['id_aluno'] == r['id']]['hora_entrega'].values[0]
                texto_relatorio += f"- {r['nome']} (Entregue: {h_ent if h_ent else 'Pendente'})\n"
            
            # Faltantes (quem é do turno mas não foi marcado)
            texto_relatorio += "\n❌ NÃO EMBARCARAM / AUSENTES:\n"
            faltantes = df_atual[~df_atual['id'].isin(presentes_ids) & (df_atual['turno'] != 'pendente')]
            for _, f in faltantes.iterrows():
                texto_relatorio += f"- {f['nome']}\n"
            
            st.text_area("Copie o texto abaixo para o WhatsApp:", texto_relatorio, height=300)
            st.link_button("Abrir WhatsApp", f"https://wa.me/?text={texto_relatorio.replace(' ', '%20').replace('', '%0A')}")

# --- 3. CONFIGURAR (Mesma lógica de antes) ---
elif aba == "⚙️ Configurar Alunos":
    st.header("⚙️ Configurações Gerais")
    with st.form("form_config"):
        novos_dados = []
        for index, row in df_atual.iterrows():
            st.write(f"**{row['nome']}**")
            c1, c2 = st.columns([1, 2])
            t = c1.selectbox("Turno", ["pendente", "matutino", "vespertino"], index=["pendente", "matutino", "vespertino"].index(row['turno']), key=f"t_{row['id']}")
            e = c2.text_input("Endereço", value=row['endereco'], key=f"e_{row['id']}")
            novos_dados.append((e, t, row['id']))
        if st.form_submit_button("💾 SALVAR TUDO"):
            conn = sqlite3.connect('dados_transporte.db')
            conn.executemany("UPDATE alunos SET endereco = ?, turno = ? WHERE id = ?", novos_dados)
            conn.commit()
            conn.close()
            st.success("Dados salvos!")
            st.rerun()

# --- 4. NOVO ALUNO ---
elif aba == "➕ Novo Aluno":
    st.header("➕ Novo Aluno")
    with st.form("f_novo"):
        n = st.text_input("Nome")
        e = st.text_input("Endereço")
        t = st.selectbox("Turno", ["matutino", "vespertino", "pendente"])
        if st.form_submit_button("Adicionar"):
            if n:
                conn = sqlite3.connect('dados_transporte.db')
                conn.execute("INSERT INTO alunos (nome, endereco, turno) VALUES (?, ?, ?)", (n, e, t))
                conn.commit()
                conn.close()
                st.success("Adicionado!")
                st.rerun()
