import streamlit as st

# Criando duas abas na sua tela
aba_editar, aba_imprimir = st.tabs(["📝 Modo Edição", "🖨️ Visualizar para Impressão"])

with aba_editar:
    st.subheader("➕ Montar Nova Ficha Técnica")
    
    col1, col2 = st.columns(2)
    with col1:
        sku = st.text_input("Cód. SKU (Ex: ACAI-01):")
        embalagem = st.text_input("Embalagem de Venda (Ex: Caixa 5L):")
    with col2:
        nome_comercial = st.text_input("Nome Comercial da Formulação:")
        peso = st.number_input("Peso Líquido da Embalagem (kg):", value=2.500)
    
    # Texto do POP mais curto e direto
    pop_padrao_curto = """
1. PREPARO: Sanitizar equipamentos (200ppm). Pesar todos os ingredientes na balança de precisão.
2. MISTURA: Adicionar líquidos na tina/liquidificador. Incorporar os pós lentamente sob agitação.
3. PRODUÇÃO: Inserir a calda na produtora. Bater até atingir a textura ideal e extrair a -6°C.
4. ENVASE: Envasar, selar, colocar lote/validade e enviar imediatamente para o freezer a -25°C.
    """.strip()
    
    pop_texto = st.text_area("Procedimento Operacional Padrão (POP):", value=pop_padrao_curto, height=150)
    
    st.button("💾 Salvar Ficha Técnica no Cofre")

with aba_imprimir:
    # Esta aba fica limpa, sem campos de digitação, ideal para imprimir (Ctrl+P)
    st.markdown(f"## 🏭 FICHA TÉCNICA DE PRODUÇÃO")
    st.markdown("---")
    
    colA, colB = st.columns(2)
    with colA:
        st.markdown(f"**SKU:** {sku if sku else '---'}")
        st.markdown(f"**Produto:** {nome_comercial if nome_comercial else '---'}")
    with colB:
        st.markdown(f"**Embalagem:** {embalagem if embalagem else '---'}")
        st.markdown(f"**Peso/Rendimento:** {peso} kg")
    
    st.markdown("---")
    st.markdown("### 📋 Procedimento Operacional Padrão (POP)")
    
    # O st.markdown vai renderizar o texto exatamente como você formatar, ótimo para leitura
    st.markdown(pop_texto)
    
    st.markdown("---")
    st.markdown("### 🧬 Matriz de Ingredientes")
    st.info("Aqui entrará a sua tabela de ingredientes gerada pelo sistema.")
