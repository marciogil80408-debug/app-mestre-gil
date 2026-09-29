# ==========================================
# MÓDULO 2: NOVO MOTOR DE BALANCEAMENTO
# ==========================================
elif menu == "🧪 Motor Físico-Químico":
    st.title("🧪 Motor de Balanceamento Físico-Químico")
    
    # 1. Categoria do Produto Final
    st.subheader("📋 Classificação da Formulação")
    colA, colB = st.columns(2)
    with colA:
        nome_receita = st.text_input("Nome da Calda (Ex: Calda Base Branca):")
    with colB:
        categoria_receita = st.selectbox("Categoria do Produto:", ["Sorvete de Massa", "Gelato", "Açaí", "Picolé", "Creme Zero Açúcar"])
    
    # 2. Banco de Dados Técnico - Agora com a chave "Categoria"
    BASE_INGREDIENTES = {
        "Água Filtrada": {"Categoria": "💧 Líquidos Base", "ST": 0.0, "Gordura": 0.0, "SNG": 0.0, "PAC": 0, "POD": 0},
        "Leite Integral (Fluido)": {"Categoria": "💧 Líquidos Base", "ST": 12.0, "Gordura": 3.0, "SNG": 9.0, "PAC": 0, "POD": 0},
        
        "Leite em Pó Integral": {"Categoria": "🥛 Laticínios em Pó", "ST": 97.0, "Gordura": 26.0, "SNG": 71.0, "PAC": 0, "POD": 0},
        
        "Açúcar (Sacarose)": {"Categoria": "🍬 Açúcares e Carboidratos", "ST": 100.0, "Gordura": 0.0, "SNG": 0.0, "PAC": 100, "POD": 100},
        "Glucose em Pó (DE 40)": {"Categoria": "🍬 Açúcares e Carboidratos", "ST": 95.0, "Gordura": 0.0, "SNG": 0.0, "PAC": 45, "POD": 50},
        "Maltodextrina": {"Categoria": "🍬 Açúcares e Carboidratos", "ST": 95.0, "Gordura": 0.0, "SNG": 0.0, "PAC": 15, "POD": 10},
        
        "Gordura de Palma": {"Categoria": "🧈 Gorduras e Pastas", "ST": 100.0, "Gordura": 100.0, "SNG": 0.0, "PAC": 0, "POD": 0},
        
        "Emustab / Estabilizante": {"Categoria": "🧪 Aditivos e Gomas", "ST": 100.0, "Gordura": 0.0, "SNG": 0.0, "PAC": 0, "POD": 0},
    }

    st.markdown("---")
    st.subheader("📝 Montagem da Calda")
    
    ingredientes_selecionados = st.multiselect(
        "1. Selecione os ingredientes da formulação:",
        options=list(BASE_INGREDIENTES.keys()),
        default=["Água Filtrada", "Leite em Pó Integral", "Açúcar (Sacarose)", "Emustab / Estabilizante"]
    )

    st.write("2. Insira os pesos separados por categoria:")
    
    pesos_receita = {}
    
    # Agrupando a exibição na tela por Categorias
    categorias_unicas = sorted(list(set([BASE_INGREDIENTES[ing]["Categoria"] for ing in ingredientes_selecionados])))
    
    for cat in categorias_unicas:
        # Cria uma caixinha expansível para cada categoria
        with st.expander(f"{cat}", expanded=True):
            cols_pesos = st.columns(4)
            # Filtra os ingredientes selecionados que pertencem a esta categoria
            itens_desta_categoria = [ing for ing in ingredientes_selecionados if BASE_INGREDIENTES[ing]["Categoria"] == cat]
            
            for i, ingrediente in enumerate(itens_desta_categoria):
                with cols_pesos[i % 4]:
                    peso = st.number_input(f"{ingrediente} (kg)", min_value=0.00, value=0.00, step=0.10, key=f"peso_{ingrediente}")
                    pesos_receita[ingrediente] = peso

    peso_total_calda = sum(pesos_receita.values())

    if peso_total_calda > 0:
        st.markdown("---")
        st.subheader("📊 Análise Físico-Química da Calda")
        
        total_st, total_gordura, total_sng, total_pac, total_pod = 0.0, 0.0, 0.0, 0.0, 0.0
        
        for ing, peso_kg in pesos_receita.items():
            prop = BASE_INGREDIENTES[ing]
            total_st += (peso_kg * prop["ST"]) / 100
            total_gordura += (peso_kg * prop["Gordura"]) / 100
            total_sng += (peso_kg * prop["SNG"]) / 100
            total_pac += (peso_kg * prop["PAC"]) / 100
            total_pod += (peso_kg * prop["POD"]) / 100
        
        perc_st = (total_st / peso_total_calda) * 100
        perc_gordura = (total_gordura / peso_total_calda) * 100
        perc_sng = (total_sng / peso_total_calda) * 100
        indice_pac = (total_pac / peso_total_calda) * 100
        indice_pod = (total_pod / peso_total_calda) * 100

        metrica1, metrica2, metrica3, metrica4 = st.columns(4)
        
        with metrica1:
            st.metric("Peso Total da Calda", f"{peso_total_calda:.3f} kg")
        with metrica2:
            st.metric("Sólidos Totais (ST)", f"{perc_st:.1f}%")
            if perc_st < 36: st.error("⚠️ Baixo ST (Risco de gelo).")
            elif perc_st > 42: st.warning("⚠️ Alto ST (Risco arenoso).")
            else: st.success("✅ ST Ideal.")
        with metrica3:
            st.metric("Gordura Total", f"{perc_gordura:.1f}%")
            if perc_gordura < 6: st.warning("⚠️ Gordura baixa.")
        with metrica4:
            st.metric("SNG (Sólidos Não-Gordurosos)", f"{perc_sng:.1f}%")
            if perc_sng > 11: st.error("⚠️ SNG Alto (Risco lactose).")

        st.markdown(f"**Poder Anticongelante (PAC):** {indice_pac:.1f} | **Poder Adoçante (POD):** {indice_pod:.1f}")
    else:
        st.warning("Adicione os pesos dos ingredientes para gerar o cálculo.")
