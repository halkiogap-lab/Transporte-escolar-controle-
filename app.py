import streamlit as st
import pandas as pd
from datetime import datetime

# Configuração da Página
st.set_page_config(page_title="Monitoramento Escolar", layout="wide")

# Simulação de Banco de Dados (conforme sua especificação OpenAPI)
if 'children' not in st.session_state:
    st.session_state.children = []
if 'attendance' not in st.session_state:
    st.session_state.attendance = {}

# --- FUNÇÕES DA API (CRUD) ---
def list_children():
    return st.session_state.children

def create_child(name, address, notes, shift):
    new_id = len(st.session_state.children) + 1
    child = {
        "id": new_id,
        "name": name,
        "defaultAddress": address,
        "notes": notes,
        "shift": shift,
        "createdAt": datetime.now().isoformat()
    }
    st.session_state.children.append(child)
    return child

# --- INTERFACE VISUAL ---
st.title("🚌 Monitoramento de Transporte Escolar")

menu = ["Painel Principal", "Cadastrar Aluno", "Chamada do Dia", "Rota de Busca"]
choice = st.sidebar.selectbox("Menu de Navegação", menu)

# 1. PAINEL PRINCIPAL (Stats)
if choice == "Painel Principal":
    st.header("📊 Resumo Geral")
    total = len(st.session_state.children)
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Crianças", total)
    col2.metric("Endereços Salvos", sum(1 for c in st.session_state.children if c['defaultAddress']))
    
    if total > 0:
        df = pd.DataFrame(st.session_state.children)
        st.dataframe(df[['name', 'shift', 'defaultAddress']])

# 2. CADASTRAR ALUNO (CreateChild)
elif choice == "Cadastrar Aluno":
    st.header("📝 Novo Cadastro")
    with st.form("form_cadastro"):
        name = st.text_input("Nome da Criança")
        address = st.text_input("Endereço Padrão")
        notes = st.text_area("Observações")
        shift = st.selectbox("Turno", ["matutino", "vespertino"])
        
        submit = st.form_submit_button("Salvar Aluno")
        if submit:
            if name:
                create_child(name, address, notes, shift)
                st.success(f"{name} cadastrado com sucesso!")
            else:
                st.error("O nome é obrigatório.")

# 3. CHAMADA DO DIA (Attendance)
elif choice == "Chamada do Dia":
    st.header("✅ Presença Diária")
    data_hoje = st.date_input("Data", datetime.now())
    turno_filtro = st.radio("Filtrar Turno", ["matutino", "vespertino"])
    
    alunos = [c for c in st.session_state.children if c['shift'] == turno_filtro]
    
    if not alunos:
        st.info(f"Nenhum aluno cadastrado no turno {turno_filtro}.")
    else:
        for aluno in alunos:
            col_n, col_p = st.columns([3, 1])
            col_n.write(f"**{aluno['name']}**")
            status = col_p.selectbox("Status", ["unmarked", "present", "absent"], key=aluno['id'])
            # Salva o status (UpsertAttendance)
            st.session_state.attendance[f"{data_hoje}_{aluno['id']}"] = status

# 4. ROTA DE BUSCA (Route)
elif choice == "Rota de Busca":
    st.header("📍 Rota de Hoje")
    data_hoje = st.date_input("Ver Rota para:", datetime.now())
    
    rota = []
    for aluno in st.session_state.children:
        status = st.session_state.attendance.get(f"{data_hoje}_{aluno['id']}", "unmarked")
        if status == "present" and aluno['defaultAddress']:
            rota.append(aluno)
            
    if not rota:
        st.warning("Marque a presença dos alunos primeiro ou cadastre endereços.")
    else:
        for i, stop in enumerate(rota, 1):
            st.info(f"**Parada {i}:** {stop['name']}\n\n📍 {stop['defaultAddress']}")
