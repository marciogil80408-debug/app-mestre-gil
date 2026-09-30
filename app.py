import sqlite3
import pandas as pd
import streamlit as st

# 1. Função para conectar e criar o banco de dados (Roda invisível no fundo)
def inicializar_banco():
    conn = sqlite3.connect("mestre_gil_erp.db")
    cursor = conn.cursor()
    # Cria a tabela de Fila de Produção se ela não existir
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fila_producao (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto TEXT,
            quantidade REAL,
            status TEXT,
            data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Executa a criação do banco logo ao abrir o app
inicializar_banco()

# 2. Como seria a nova tela de Fila de Produção (com salvamento definitivo)
st.subheader("📋 Fila de Produção (Salva no Banco de Dados)")

col1, col2 = st.columns(2)
with col1:
    novo_produto = st.text_input("Produto a Produzir:")
with col2:
    qtd_produzir = st.number_input("Quantidade (kg/L):", min_value=1.0, step=1.0)

if st.button("➕ Adicionar à Fila"):
    if novo_produto:
        conn = sqlite3.connect("mestre_gil_erp.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO fila_producao (produto, quantidade, status) VALUES (?, ?, ?)", 
                       (novo_produto, qtd_produzir, "Pendente"))
        conn.commit()
        conn.close()
        st.success(f"{novo_produto} adicionado à fila com sucesso!")
        st.rerun() # Atualiza a tela para mostrar o item novo

# 3. Mostrando a fila que NUNCA some
st.markdown("---")
st.markdown("### ⏳ Ordens Pendentes")
conn = sqlite3.connect("mestre_gil_erp.db")
df_fila = pd.read_sql_query("SELECT id, produto, quantidade, status FROM fila_producao WHERE status='Pendente'", conn)
conn.close()

if not df_fila.empty:
    st.dataframe(df_fila, hide_index=True, use_container_width=True)
else:
    st.info("A fila de produção está vazia.")
