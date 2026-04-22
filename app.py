import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import urllib.parse

# --- CONFIGURAÇÃO DO BANCO DE DADOS ---
def criar_banco():
    conn = sqlite3.connect('dados_transporte.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS alunos 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, endereco TEXT, turno TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS presenca 
                 (id_aluno INTEGER, data TEXT, status INTEGER, hora_entrega TEXT, PRIMARY KEY (id_aluno, data))''')
    
    try:
        c.execute("SELECT hora_entrega FROM presenca LIMIT 1")
    except sqlite3.OperationalError:
        c.execute("ALTER TABLE presenca ADD COLUMN hora_entrega TEXT DEFAULT ''")
        
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

# --- MENU LATERAL ---
st.sidebar.title("🚐 Controle Van")
data_selecionada = st.sidebar.date_input("📅 Calendário", datetime.now())
data_str = data_selecionada.strftime("%Y-%m-%d")

aba = st.sidebar.radio("Navegação", ["✅ Chamada", "📍 Rota e Entrega", "⚙️ Configurar Alunos", "➕ Novo Aluno"])

# --- 1. CHAMADA ---
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
                conn.execute("INSERT OR REPLACE INTO presenca (id_aluno, data, status, hora_entrega) VALUES (?, ?, ?, COALESCE((SELECT hora_entrega FROM presenca WHERE id_aluno=? AND data=?), ''))", 
                             (row['id'], data_str, status, row['id'], data_str))
                conn.commit()
                conn.close()
                st.rerun()

# --- 2. ROTA E ENTREGA (COM BOTÃO GPS NOVO) ---
elif aba == "📍 Rota e Entrega":
    st.header(f"📍 Rota - {data_selecionada.strftime('%d/%m/%Y')}")
    presenca_data = carregar_presenca_detalhada(data_str)
    presentes_ids = presenca_data[presenca_data['status'] == 1]['id_aluno'].tolist()
    
    rota = df_atual[df_atual['id'].isin(presentes_ids)]
    
    if rota.empty:
        st.info("Ninguém marcado como presente hoje.")
    else:
        for _, row in rota.iterrows():
            with st.expander(f"🏠 {row['nome']}"):
                st.write(f"Endereço: {row['endereco']}")
                
                # --- NOVO: BOTÃO DE GPS ---
                if row['endereco'] and row['endereco'] != "Não cadastrado":
                    endereco_codificado = urllib.parse.quote(row['endereco'])
                    link_maps = f"https://www.google.com/maps/search/?api=1&query={endereco_codificado}"
                    st.link_button(f"🗺️ Abrir GPS: {row['nome']}", link_maps)
                else:
                    st.warning("Endereço não cadastrado para abrir o GPS.")
                
                # Registro de Entrega
                entrega_row = presenca_data[presenca_data['id_aluno'] == row['id']]
                hora_atual = entrega_row['hora_entrega'].values[0] if not entrega_row.empty else ""
                
                if not hora_atual:
                    if st.button(f"✅ Confirmar Entrega: {row['nome']}", key=f"ent_{row['id']}"):
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
            st.subheader("📋 Relatório Final")
            hora_gen = datetime.now().strftime("%H:%M")
            texto_relatorio = f"🚌 RELATÓRIO VAN - DATA: {data_str} às {hora_gen}\n\n✅ PRESENTES:\n"
            
            for _, r in rota.iterrows():
                info_p = presenca_data[presenca_data['id_aluno'] == r['id']]
                h_ent = info_p['hora_entrega'].values[0] if not info_p.empty else "Pendente"
                texto_relatorio += f"- {r['nome']} (Entregue: {h_ent if h_ent else 'Pendente'})\n"
            
            texto_relatorio += "\n❌ AUSENTES:\n"
            faltantes = df_atual[~df_atual['id'].isin(presentes_ids) & (df_atual['turno'] != 'pendente')]
            for _, f in faltantes.iterrows():
                texto_relatorio += f"- {f['nome']}\n"
            
            st.text_area("Copie o texto:", texto_relatorio, height=200)

# --- 3. CONFIGURAR ---
elif aba == "⚙️ Configurar Alunos":
    st.header("⚙️ Configurações")
    with st.form("form_config"):
        novos_dados = []
        for index, row in df_atual.iterrows():
            st.write(f"**{row['nome']}**")
            c1, c2 = st.columns([1, 2])
            t = c1.selectbox("Turno", ["pendente", "matutino", "vespertino"], index=["pendente", "matutino", "vespertino"].index(row['turno']), key=f"t_{row['id']}")
            e = c2.text_input("Endereço", value=row['endereco'], key=f"e_{row['id']}")
            novos_dados.append((e, t, row['id']))
        if st.form_submit_button("💾 SAL
