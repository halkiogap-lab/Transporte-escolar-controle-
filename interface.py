import streamlit as st
import requests

# COLOQUE O LINK DA SUA API AQUI ABAIXO
API_URL = "https://transporte-escolar-controle.onrender.com"

st.set_page_config(page_title="Van Escolar Pro", layout="centered")

st.title("🚐 Van Escolar Pro")
st.subheader("Gestão de Alunos e Presença")

menu = ["Cadastrar Aluno", "Marcar Presença", "Ver Lista"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Cadastrar Aluno":
    st.header("Novo Cadastro")
    with st.form("form_aluno"):
        nome = st.text_input("Nome do Aluno")
        endereco = st.text_input("Endereço Completo")
        responsavel = st.text_input("Nome do Responsável")
        telefone = st.text_input("Telefone de Contato")
        
        submitted = st.form_submit_button("Salvar Aluno")
        
        if submitted:
            dados = {
                "name": nome,
                "address": endereco,
                "guardian_name": responsavel,
                "phone": telefone
            }
            res = requests.post(f"{API_URL}/api/children", json=dados)
            if res.status_code == 200 or res.status_code == 201:
                st.success(f"Aluno {nome} cadastrado com sucesso!")
            else:
                st.error("Erro ao cadastrar. Verifique a conexão.")

elif choice == "Ver Lista":
    st.header("Alunos Cadastrados")
    res = requests.get(f"{API_URL}/api/children")
    if res.status_code == 200:
        alunos = res.json()
        for a in alunos:
            st.write(f"👤 **{a['name']}** - {a['address']}")
    else:
        st.info("Nenhum aluno encontrado ou erro na API.")

elif choice == "Marcar Presença":
    st.header("Chamada do Dia")
    st.write("Selecione os alunos que entraram na van:")
    # Aqui você pode expandir para buscar a lista e marcar um por um
    st.warning("Módulo de chamada em desenvolvimento.")
  
