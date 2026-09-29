import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("🧪 Motor de Balanceamento Físico-Químico")

# 1. Banco de Dados Técnico (Simulado) - Valores em % (por 100g)
# PAC = Poder Anticongelante (Relativo à Sacarose = 100)
# POD = Poder Adoçante (Relativo à Sacarose = 100)
BASE_INGREDIENTES = {
    "Água Filtrada": {"ST": 0.0, "Gordura": 0.0, "SNG": 0.0, "PAC": 0, "POD": 0},
    "Leite Integral (Fluido)": {"ST": 12.0, "Gordura": 3.0, "SNG": 9.0, "PAC": 0, "POD": 0},
    "Leite em Pó Integral": {"ST": 97.0, "Gordura": 26.0, "SNG": 71.0, "PAC": 0, "POD": 0},
    "Açúcar (Sacarose)": {"ST": 100.0, "Gordura": 0.0, "SNG": 0.0, "PAC": 100, "POD": 100},
    "Glucose em Pó (DE 40)": {"ST": 95.0, "Gordura": 0.0, "SNG": 0.0, "PAC": 45, "POD": 50},
    "Maltodextrina": {"ST": 95.0, "Gordura": 0.0, "SNG": 0.0, "PAC": 15, "POD": 10},
    "Gordura de Palma": {"ST": 100.0, "Gordura": 100.0, "SNG": 0.0, "PAC": 0, "POD": 0},
    "Emustab / Estabilizante": {"ST": 100.0, "Gordura": 0.0, "SNG": 0.0, "PAC": 0, "POD": 0},
}

# 2. Interface de Entrada da Receita
st.subheader("📝 Montagem da Calda")
col1, col2 = st.columns([2, 1])

with col1:
    # Seleção múltipla para escolher o que vai na receita
    ingredientes_selecionados = st.multiselect(
        "Selecione os ingredientes da formulação:",
        options=list(BASE_INGREDIENTES.keys()),
        default=["Água Filtrada", "Leite em Pó Integral", "Açúcar (Sacarose)", "Emustab / Estabilizante"]
    )

with col2:
    st.info("Digite o peso em KG de cada ingrediente.")

# 3. Coleta de Pesos
pesos_receita = {}
st.write("---")
cols_pesos = st.columns(4) # Divide em 4 colunas para não ficar uma lista gigante

for i, ingrediente in enumerate(ingredientes_selecionados):
    with cols_pesos[i % 4]:
        # Coleta o peso em kg
        peso = st.number_input(f"{ingrediente} (kg)", min_value=0.0, value=0.0, step=0.1, key=ingrediente)
        pesos_receita[ingrediente] = peso

# 4. Algoritmo de Cálculo do Balanço de Massa
peso_total_calda = sum(pesos_receita.values())

if peso_total_calda > 0:
    st.markdown("---")
    st.subheader("📊 Análise Físico-Química da Calda")
    
    # Variáveis acumuladoras
    total_st = 0.0
    total_gordura = 0.0
    total_sng = 0.0
    total_pac = 0.0
    total_pod = 0.0
    
    for ing, peso_kg in pesos_receita.items():
        # Regra de 3: (Peso do ingrediente * Porcentagem do componente) / 100
        prop = BASE_INGREDIENTES[ing]
        total_st += (peso_kg * prop["ST"]) / 100
        total_gordura += (peso_kg * prop["Gordura"]) / 100
        total_sng += (peso_kg * prop["SNG"]) / 100
        total_pac += (peso_kg * prop["PAC"]) / 100
        total_pod += (peso_kg * prop["POD"]) / 100
    
    # Cálculo das porcentagens finais na calda
    perc_st = (total_st / peso_total_calda) * 100
    perc_gordura = (total_gordura / peso_total_calda) * 100
    perc_sng = (total_sng / peso_total_calda) * 100
    
    # PAC e POD geralmente são calculados em índice absoluto ou % em relação à água/sólidos. 
    # Aqui usamos o índice direto da mistura.
    indice_pac = (total_pac / peso_total_calda) * 100
    indice_pod = (total_pod / peso_total_calda) * 100

    # 5. Exibição dos Resultados com Alertas Reológicos
    metrica1, metrica2, metrica3, metrica4 = st.columns(4)
    
    with metrica1:
        st.metric("Peso Total da Calda", f"{peso_total_calda:.3f} kg")
    
    with metrica2:
        st.metric("Sólidos Totais (ST)", f"{perc_st:.1f}%")
        if perc_st < 36:
            st.error("⚠️ Baixo ST. Risco de formação de cristais de gelo.")
        elif perc_st > 42:
            st.warning("⚠️ Alto ST. Risco de textura pesada/arenosa.")
        else:
            st.success("✅ ST Ideal.")

    with metrica3:
        st.metric("Gordura Total", f"{perc_gordura:.1f}%")
        if perc_gordura < 6:
            st.warning("⚠️ Gordura baixa. Pode faltar cremosidade.")
            
    with metrica4:
        st.metric("SNG (Sól. Não-Gordurosos)", f"{perc_sng:.1f}%")
        if perc_sng > 11:
            st.error("⚠️ SNG Alto. Risco de arenosidade (cristalização da lactose).")

    st.markdown(f"**Poder Anticongelante (PAC):** {indice_pac:.1f} | **Poder Adoçante (POD):** {indice_pod:.1f}")
else:
    st.warning("Adicione os pesos dos ingredientes para gerar o cálculo.")
