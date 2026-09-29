import streamlit as st
import os
import sqlite3
import pandas as pd
import json
from datetime import datetime

# ==========================================
# ⚙️ 1. CONFIGURAÇÃO GERAL
# ==========================================
st.set_page_config(page_title="App Mestre Gil - ERP Industrial", page_icon="🏭", layout="wide")
DB_NAME = "fabrica_gelado.db"

# ==========================================
# 🗄️ 2. MÓDULO DE BANCO DE DADOS & SEGURANÇA
# ==========================================
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS fila_producao (id INTEGER PRIMARY KEY AUTOINCREMENT, receita TEXT, meta_kg REAL, status TEXT, instrucao TEXT DEFAULT '', batidas_total INTEGER DEFAULT 1)''')
    c.execute('''CREATE TABLE IF NOT EXISTS historico (id INTEGER PRIMARY KEY AUTOINCREMENT, receita TEXT, meta_kg REAL, caixas INTEGER, peseiro TEXT, batedor TEXT, obs TEXT, data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS receitas (nome TEXT PRIMARY KEY, ingredientes TEXT, und_nome TEXT DEFAULT 'Caixa 5L', und_peso REAL DEFAULT 2.5, modo_preparo TEXT DEFAULT '', sku TEXT DEFAULT '')''')
    c.execute('''CREATE TABLE IF NOT EXISTS estoque (ingrediente TEXT PRIMARY KEY, custo_kg REAL DEFAULT 0.0, qtd_atual_kg REAL DEFAULT 0.0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS tabela_nutricional (receita TEXT PRIMARY KEY, dados_json TEXT)''')
    
    # NOVA TABELA: SEGURANÇA E USUÁRIOS
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios (login TEXT PRIMARY KEY, nome TEXT, senha TEXT, perfil TEXT)''')
    
    # Popula os usuários da fábrica na primeira vez que o sistema rodar
    c.execute("SELECT COUNT(*) FROM usuarios")
    if c.fetchone()[0] == 0:
        usuarios_padrao = [
            ('gil', 'Mestre Gil', 'mestre123', 'Mestre'),
            ('alex', 'Alex (Produção)', 'fabrica123', 'Operador'),
            ('enyo', 'Enyo (Gerente)', 'gerente123', 'Gerente'),
            ('islane', 'Islane (Financeiro)', 'finan123', 'Financeiro')
        ]
        c.executemany("INSERT INTO usuarios (login, nome, senha, perfil) VALUES (?, ?, ?, ?)", usuarios_padrao)

    try: c.execute("ALTER TABLE fila_producao ADD COLUMN batidas_total INTEGER DEFAULT 1")
    except: pass
    try: c.execute("ALTER TABLE receitas ADD COLUMN modo_preparo TEXT DEFAULT ''")
    except: pass
    try: c.execute("ALTER TABLE receitas ADD COLUMN sku TEXT DEFAULT ''")
    except: pass

    conn.commit()
    conn.close()

def executar_query(query, params=()):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(query, params)
    conn.commit()
    conn.close()

def carregar_dados_tabela(query):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(query)
    linhas = c.fetchall()
    conn.close()
    return linhas

def carregar_receitas():
    linhas = carregar_dados_tabela("SELECT nome, ingredientes, und_nome, und_peso, modo_preparo, sku FROM receitas")
    receitas_db = {}
    for l in linhas:
        receitas_db[l[0]] = {
            "ingredientes": json.loads(l[1]), "und_nome": l[2], "und_peso": l[3],
            "modo_preparo": l[4] if l[4] else "1. Adicionar líquidos no tanque.\n2. Incorporar sólidos sob agitação.\n3. Homogeneizar até textura uniforme.",
            "sku": l[5] if l[5] else "S/N"
        }
    return receitas_db

def carregar_estoque():
    linhas = carregar_dados_tabela("SELECT ingrediente, custo_kg, qtd_atual_kg FROM estoque")
    return {l[0]: {"custo_kg": l[1], "qtd_atual_kg": l[2]} for l in linhas}

init_db()

# ==========================================
# 🎨 3. MÓDULO DE ESTILIZAÇÃO CSS
# ==========================================
def aplicar_css_premium():
    st.markdown("""
        <style>
        .stApp, .stAppHeader { background-color: #0f172a; color: #f8fafc; }
        [data-testid="stSidebar"] { background-color: #1e293b !important; border-right: 1px solid #334155; }
        [data-testid="stSidebar"] * { color: #f8fafc !important; }
        #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
        
        .stButton button[kind="secondary"], .stButton button:not([kind="primary"]) { background: linear-gradient(135deg, #2563eb, #1e40af); color: white; font-weight: bold; border-radius: 8px; width: 100%; border: none; padding: 0.6rem; transition: all 0.3s ease; }
        .stButton button[kind="secondary"]:hover, .stButton button:not([kind="primary"]):hover { background: linear-gradient(135deg, #1e40af, #1e3a8a); transform: translateY(-2px); color: white; }
        
        .stButton button[kind="primary"] { background: linear-gradient(135deg, #10b981, #059669) !important; color: white !important; font-weight: 900 !important; border-radius: 8px !important; border: none !important; padding: 0.8rem !important; font-size: 1.2em !important; transition: all 0.3s ease !important; box-shadow: 0 4px 10px rgba(16, 185, 129, 0.4) !important; }
        .stButton button[kind="primary"]:hover { background: linear-gradient(135deg, #059669, #047857) !important; transform: translateY(-2px) !important; }

        [data-testid="stImage"] img { border-radius: 20px; box-shadow: 0 8px 25px rgba(0, 0, 0, 0.5); border: 2px solid #1e293b; transition: transform 0.3s ease; }
        [data-testid="stImage"] img:hover { transform: scale(1.02); }
        
        h1, h2, h3, h4, h5, p, label { color: #e2e8f0 !important; }
        
        div[data-baseweb="input"] > div, div[data-baseweb="select"] > div, div[data-baseweb="textarea"] > div { background-color: #1e293b !important; border: 1px solid #3b82f6 !important; }
        div[data-baseweb="input"] input, div[data-baseweb="select"] div, div[data-baseweb="textarea"] textarea { color: #f8fafc !important; }
        [data-testid="stDataFrame"] { background-color: #1e293b !important; }
        [data-testid="stDataFrame"] * { color: #f8fafc !important; }
        
        input[type="checkbox"] { transform: scale(1.7); margin-right: 10px; cursor: pointer; }
        [data-testid="stCheckbox"] span[data-baseweb="checkbox"] > div { border: 2px solid #60a5fa !important; border-radius: 4px !important; }
        .stCheckbox label span { font-size: 1.1em; font-weight: 900; padding-left: 6px; color: #f8fafc !important;}
        
        .ficha-box { background-color: #1e293b; border: 2px solid #3b82f6; border-radius: 12px; padding: 25px; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.4); }
        .passo-passo-box { background-color: #111827; border-left: 4px solid #10b981; padding: 15px; border-radius: 6px; margin-top: 20px; font-family: monospace; color: #34d399; }
        
        .anvisa-table { width: 100%; max-width: 500px; border-collapse: collapse; font-family: Arial, sans-serif; background-color: white !important; color: black !important; margin: 0 auto; border: 2px solid black; }
        .anvisa-table th, .anvisa-table td, .anvisa-table span, .anvisa-table div { color: black !important; background-color: white !important; }
        .anvisa-table th, .anvisa-table td { border-bottom: 1px solid black; padding: 6px 4px; text-align: left; font-size: 14px; }
        .anvisa-table th { font-weight: 900; border-bottom: 2px solid black; }
        .anvisa-header { text-align: center; font-weight: 900; font-size: 20px; padding: 10px 0; border-bottom: 5px solid black; text-transform: uppercase; }
        .anvisa-sub { font-size: 12px; font-weight: bold; border-bottom: 1px solid black; padding: 4px; }
        </style>
    """, unsafe_allow_html=True)

    caminho_imagem = "gelato fran.jpg"
    if os.path.exists(caminho_imagem):
        col_img1, col_img2, col_img3 = st.columns([1, 2, 1])
        with col_img2: st.image(caminho_imagem, use_container_width=True)
    else:
        st.markdown("<h1 style='text-align: center; color: #60a5fa;'>🏭 APP MESTRE GIL</h1>", unsafe_allow_html=True)
    st.markdown("---")

# ==========================================
# 👑 4. MÓDULO: ROTEADOR DE TELAS INTELIGENTES (RBAC)
# ==========================================
def renderizar_painel_adm(matriz_receitas, fila_producao, estoque_atual, perfil):
    st.title("👑 Painel de Inteligência")
    
    # 🛡️ CONTROLE DE ACESSO: Monta as abas baseadas no Perfil
    abas_disponiveis = []
    if perfil in ["Mestre", "Gerente"]: abas_disponiveis.append("🏭 Gestão da Fila")
    if perfil in ["Mestre", "Gerente", "Financeiro"]: abas_disponiveis.append("📦 Estoque e Custos")
    if perfil in ["Mestre", "Financeiro"]: abas_disponiveis.append("💰 Lucro Real (CMV)")
    if perfil in ["Mestre", "Gerente", "Financeiro"]: abas_disponiveis.append("📊 Fechamento & BI")
    if perfil == "Mestre": abas_disponiveis.append("🔐 Cofre de Receitas")
    if perfil in ["Mestre", "Financeiro"]: abas_disponiveis.append("🍎 Tabela Anvisa")
    if perfil in ["Mestre", "Gerente"]: abas_disponiveis.append("👥 Gestão de Equipe (RH)")

    tabs = st.tabs(abas_disponiveis)
    tab_idx = 0

    if "🏭 Gestão da Fila" in abas_disponiveis:
        with tabs[tab_idx]:
            col_add, col_reorder = st.columns(2)
            with col_add:
                st.subheader("⚙️ Enviar Ordem de Produção")
                if not matriz_receitas:
                    st.warning("Cadastre as receitas no Cofre primeiro.")
                else:
                    lista_produtos = [f"[{v['sku']}] {k}" for k, v in matriz_receitas.items()]
                    selecao = st.selectbox("Selecione o Produto (SKU):", lista_produtos)
                    receita_escolhida = selecao.split("] ")[1] if "] " in selecao else selecao
                    meta_escolhida = st.number_input("Meta de Calda/Peso por Batida (kg):", min_value=1.0, value=150.0, step=1.0)
                    batidas_qtd = st.number_input("Quantidade de Batidas (Vezes):", min_value=1, value=1, step=1)
                    instrucao_envase = st.text_area("Instruções de Envase (Opcional):", placeholder="Ex: 36 caixas de 4,1kg por batida")
                    if st.button("➕ Enviar Ordem para a Fábrica"):
                        executar_query("INSERT INTO fila_producao (receita, meta_kg, status, instrucao, batidas_total) VALUES (?, ?, 'Pendente', ?, ?)", (receita_escolhida, meta_escolhida, instrucao_envase, batidas_qtd))
                        st.rerun()
            
            with col_reorder:
                st.subheader("🔀 Reordenar Fila")
                if len(fila_producao) > 1:
                    opcoes_pendentes = {f"#{idx+1} - {p['Receita']} ({p['Meta_Kg']} kg)": p for idx, p in enumerate(fila_producao)}
                    escolha_prioridade = st.selectbox("Lote Prioritário (Fazer AGORA):", list(opcoes_pendentes.keys()))
                    if st.button("⭐ Mover para o Topo"):
                        lote_selec = opcoes_pendentes[escolha_prioridade]
                        fila_producao.remove(lote_selec)
                        fila_producao.insert(0, lote_selec)
                        executar_query("DELETE FROM fila_producao")
                        for l in fila_producao:
                            executar_query("INSERT INTO fila_producao (receita, meta_kg, status, instrucao, batidas_total) VALUES (?, ?, ?, ?, ?)", (l["Receita"], l["Meta_Kg"], l["Status"], l["Instrucao"], l["Batidas"]))
                        st.rerun()

            st.markdown("---")
            st.subheader("📋 Visão em Tempo Real da Fábrica")
            if not fila_producao:
                st.info("Fábrica ociosa. Nenhuma ordem na fila.")
            else:
                for idx, lote in enumerate(fila_producao):
                    rec_dados = matriz_receitas.get(lote['Receita'], {"und_nome": "Unidade", "und_peso": 1.0, "sku": "S/N"})
                    peso_total_lote = lote['Meta_Kg'] * lote['Batidas']
                    with st.container(border=True):
                        st.markdown(f"### **#{idx + 1} | [{rec_dados['sku']}] {lote['Receita']}**")
                        st.markdown(f"**Planejamento:** `{lote['Batidas']} Batida(s)` de `{lote['Meta_Kg']} kg` (Total: **{peso_total_lote} kg**) ")
                        if lote['Instrucao']: st.warning(f"⚠️ **Instrução:** {lote['Instrucao']}")
        tab_idx += 1

    if "📦 Estoque e Custos" in abas_disponiveis:
        with tabs[tab_idx]:
            st.subheader("📦 Gestão de Estoque e Preços Base")
            ingredientes_unicos = set()
            for rec in matriz_receitas.values():
                for ing in rec["ingredientes"].keys(): ingredientes_unicos.add(ing)
            for ing in ingredientes_unicos:
                if ing not in estoque_atual: executar_query("INSERT INTO estoque (ingrediente, custo_kg, qtd_atual_kg) VALUES (?, 0.0, 0.0)", (ing,))
            
            df_estoque = pd.DataFrame([{"Insumo": k, "Custo por Kg (R$)": v["custo_kg"], "Estoque Atual (Kg)": v["qtd_atual_kg"]} for k, v in carregar_estoque().items()])
            df_editado_estoque = st.data_editor(df_estoque, hide_index=True, use_container_width=True)
            if st.button("💾 Salvar Alterações de Estoque"):
                for _, row in df_editado_estoque.iterrows():
                    executar_query("UPDATE estoque SET custo_kg = ?, qtd_atual_kg = ? WHERE ingrediente = ?", (float(row["Custo por Kg (R$)"]), float(row["Estoque Atual (Kg)"]), row["Insumo"]))
                st.success("Estoque atualizado!")
                st.rerun()
        tab_idx += 1

    if "💰 Lucro Real (CMV)" in abas_disponiveis:
        with tabs[tab_idx]:
            st.subheader("💰 Precificação e Lucro Real (CMV)")
            if not matriz_receitas:
                st.info("Cadastre receitas no Cofre primeiro.")
            else:
                rec_fin_selecionada = st.selectbox("Selecione o Produto para Análise:", list(matriz_receitas.keys()))
                rec_dados_fin = matriz_receitas[rec_fin_selecionada]
                und_nome_fin = rec_dados_fin["und_nome"]
                und_peso_fin = rec_dados_fin["und_peso"]
                soma_proporcoes = sum(rec_dados_fin["ingredientes"].values()) if sum(rec_dados_fin["ingredientes"].values()) > 0 else 1
                custo_total_unidade = 0.0
                detalhes_custo = []

                for ing, prop in rec_dados_fin["ingredientes"].items():
                    custo_bd = estoque_atual.get(ing, {}).get("custo_kg", 0.0)
                    qtd_unidade_kg = (prop / soma_proporcoes) * und_peso_fin
                    custo_ing = qtd_unidade_kg * custo_bd
                    custo_total_unidade += custo_ing
                    detalhes_custo.append({"Ingrediente": ing, "Qtd. na Embalagem": f"{qtd_unidade_kg*1000:.0f}g" if qtd_unidade_kg < 1 else f"{qtd_unidade_kg:.3f}kg", "Custo (R$)": f"R$ {custo_ing:.2f}"})

                col_custo, col_precificacao = st.columns([1, 1])
                with col_custo:
                    st.dataframe(pd.DataFrame(detalhes_custo), hide_index=True, use_container_width=True)
                    st.warning(f"**Custo Físico Total (1 {und_nome_fin}):** R$ {custo_total_unidade:.2f}")

                with col_precificacao:
                    preco_venda = st.number_input(f"Preço de Venda Praticado (1 {und_nome_fin}):", min_value=0.0, value=custo_total_unidade * 2 if custo_total_unidade > 0 else 10.0, step=1.0)
                    lucro_bruto = preco_venda - custo_total_unidade
                    margem = (lucro_bruto / preco_venda * 100) if preco_venda > 0 else 0
                    cc1, cc2 = st.columns(2)
                    cc1.metric("Lucro Limpo por Und (R$)", f"R$ {lucro_bruto:.2f}")
                    cc2.metric("Margem de Lucro (%)", f"{margem:.1f}%")
                    if margem < 30: st.error("🚨 Margem perigosa.")
                    elif margem <= 50: st.warning("⚠️ Margem média.")
                    else: st.success("✅ Margem Excelente Industrial!")
        tab_idx += 1

    if "📊 Fechamento & BI" in abas_disponiveis:
        with tabs[tab_idx]:
            st.subheader("📊 Relatório Industrial e Fechamento de Turno")
            conn = sqlite3.connect(DB_NAME)
            df_hist = pd.read_sql_query("SELECT receita as Receita, meta_kg as 'Meta(kg)', caixas as 'Envasadas', batedor as Operador, data_hora as Data FROM historico", conn)
            conn.close()
            if not df_hist.empty:
                hoje = datetime.now().strftime("%Y-%m-%d")
                df_hist['Data_Curta'] = pd.to_datetime(df_hist['Data']).dt.strftime('%Y-%m-%d')
                df_hoje = df_hist[df_hist['Data_Curta'] == hoje]
                
                st.markdown("### 🏆 Fechamento de Hoje")
                if not df_hoje.empty:
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Kg Batidos Hoje", f"{df_hoje['Meta(kg)'].sum():.1f} kg")
                    c2.metric("Unidades Envasadas Hoje", int(df_hoje['Envasadas'].sum()))
                    c3.metric("Lotes Fechados Hoje", len(df_hoje))
                    st.bar_chart(df_hoje.groupby("Operador")["Meta(kg)"].sum(), color="#10b981")
                else:
                    st.info("Nenhuma produção finalizada no turno de hoje até o momento.")
                st.markdown("---")
                st.markdown("### 📈 Histórico Geral da Fábrica")
                st.dataframe(df_hist.drop(columns=['Data_Curta']), use_container_width=True)
        tab_idx += 1
            
    if "🔐 Cofre de Receitas" in abas_disponiveis:
        with tabs[tab_idx]:
            st.subheader("🔐 O Cofre do Mestre (Engenharia de Receitas)")
            # SEM SENHA DUPLA! A própria senha do login "Mestre" já libera a aba.
            with st.container(border=True):
                st.markdown("### ➕ Cadastrar Nova Fórmula")
                col_sku, col_nome = st.columns([1, 3])
                with col_sku: sku_novo = st.text_input("Cód. SKU (Ex: ACAI-01):")
                with col_nome: nome_nova = st.text_input("Nome da Fórmula (Sabor):")
                
                col_und1, col_und2 = st.columns(2)
                with col_und1: und_nome_nova = st.text_input("Tipo de Embalagem:", placeholder="Ex: Caixa 5L")
                with col_und2: und_peso_nova = st.number_input("Peso dessa Embalagem (kg):", min_value=0.010, value=2.500, format="%.3f")
                
                modo_preparo_novo = st.text_area("Passo a Passo do Processo:", placeholder="1. Adicionar líquidos...")
                st.markdown("**Quantidade na Receita Base:**")
                df_vazio = pd.DataFrame([{"Ingrediente": "", "Quantidade": 0.0} for _ in range(12)])
                df_editado = st.data_editor(df_vazio, num_rows="dynamic", use_container_width=True)
                
                if st.button("💾 Salvar Fórmula no Banco"):
                    nova_formula = {str(r["Ingrediente"]).strip(): float(r["Quantidade"]) for _, r in df_editado.iterrows() if str(r["Ingrediente"]).strip() != "" and float(r["Quantidade"]) > 0}
                    if nome_nova and und_nome_nova and nova_formula and sku_novo:
                        executar_query("INSERT OR REPLACE INTO receitas (nome, ingredientes, und_nome, und_peso, modo_preparo, sku) VALUES (?, ?, ?, ?, ?, ?)", (nome_nova, json.dumps(nova_formula), und_nome_nova, und_peso_nova, modo_preparo_novo, sku_novo.upper()))
                        st.success(f"Receita blindada no cofre!")
                        st.rerun()

            st.markdown("---")
            st.markdown("### 📚 Fórmulas Salvas")
            if matriz_receitas:
                for rec_nome, rec_dados_cofre in matriz_receitas.items():
                    with st.expander(f"📖 [{rec_dados_cofre['sku']}] {rec_nome} ({rec_dados_cofre['und_nome']})"):
                        st.json(rec_dados_cofre["ingredientes"])
                        st.info(rec_dados_cofre["modo_preparo"])
                        if st.button(f"🗑️ Excluir Fórmula: {rec_nome}", key=f"del_{rec_nome}"):
                            executar_query("DELETE FROM receitas WHERE nome = ?", (rec_nome,))
                            st.rerun()
        tab_idx += 1

    if "🍎 Tabela Anvisa" in abas_disponiveis:
        with tabs[tab_idx]:
            st.subheader("🍎 Sistema de Rotulagem (Anvisa)")
            if not matriz_receitas:
                st.info("Cadastre receitas no Cofre primeiro.")
            else:
                rec_selecionada = st.selectbox("Selecione o Produto para Gerar o Rótulo:", list(matriz_receitas.keys()))
                linhas_anvisa = carregar_dados_tabela(f"SELECT dados_json FROM tabela_nutricional WHERE receita = '{rec_selecionada}'")
                dados_salvos = json.loads(linhas_anvisa[0][0]) if linhas_anvisa else {}
                
                c1, c2 = st.columns(2)
                with c1: porcao_g = st.number_input("Porção do Rótulo (ex: 60g):", value=dados_salvos.get("porcao_g", 60.0))
                with c2: medida_caseira = st.text_input("Medida Caseira (ex: 1 bola):", value=dados_salvos.get("medida_caseira", "1 bola"))
                
                df_nutri_base = pd.DataFrame([
                    {"Nutriente": "Valor Energético (kcal)", "Valor em 100g": dados_salvos.get("energia", 0.0)},
                    {"Nutriente": "Carboidratos (g)", "Valor em 100g": dados_salvos.get("carbo", 0.0)},
                    {"Nutriente": "Açúcares Totais (g)", "Valor em 100g": dados_salvos.get("acucar_tot", 0.0)},
                    {"Nutriente": "Açúcares Adicionados (g)", "Valor em 100g": dados_salvos.get("acucar_add", 0.0)},
                    {"Nutriente": "Proteínas (g)", "Valor em 100g": dados_salvos.get("prot", 0.0)},
                    {"Nutriente": "Gorduras Totais (g)", "Valor em 100g": dados_salvos.get("gord_tot", 0.0)},
                    {"Nutriente": "Gorduras Saturadas (g)", "Valor em 100g": dados_salvos.get("gord_sat", 0.0)},
                    {"Nutriente": "Gorduras Trans (g)", "Valor em 100g": dados_salvos.get("gord_trans", 0.0)},
                    {"Nutriente": "Fibra Alimentar (g)", "Valor em 100g": dados_salvos.get("fibra", 0.0)},
                    {"Nutriente": "Sódio (mg)", "Valor em 100g": dados_salvos.get("sodio", 0.0)},
                ])
                df_editado_nutri = st.data_editor(df_nutri_base, hide_index=True, use_container_width=True)
                
                if st.button("💾 Gerar Tabela Anvisa"):
                    valores = df_editado_nutri["Valor em 100g"].tolist()
                    json_salvar = json.dumps({"porcao_g": porcao_g, "medida_caseira": medida_caseira, "energia": valores[0], "carbo": valores[1], "acucar_tot": valores[2], "acucar_add": valores[3], "prot": valores[4], "gord_tot": valores[5], "gord_sat": valores[6], "gord_trans": valores[7], "fibra": valores[8], "sodio": valores[9]})
                    executar_query("INSERT OR REPLACE INTO tabela_nutricional (receita, dados_json) VALUES (?, ?)", (rec_selecionada, json_salvar))
                    st.success("Dados salvos com sucesso!")
                    st.rerun()

                if dados_salvos:
                    VDs = [2000, 300, None, 50, 50, 65, 20, 2, 25, 2000] 
                    v_100 = [dados_salvos.get(k, 0) for k in ["energia", "carbo", "acucar_tot", "acucar_add", "prot", "gord_tot", "gord_sat", "gord_trans", "fibra", "sodio"]]
                    v_porcao = [v * (porcao_g / 100.0) for v in v_100]
                    vds_calc = [int(round((v_porcao[i] / VDs[i]) * 100)) if VDs[i] else "" for i in range(10)]
                    
                    st.markdown("<br><div style='background-color: white; padding: 20px; border-radius: 8px;'>", unsafe_allow_html=True)
                    st.markdown(f"""
                        <table class="anvisa-table">
                            <tr><td colspan="3" class="anvisa-header">INFORMAÇÃO NUTRICIONAL</td></tr>
                            <tr><td colspan="3" class="anvisa-sub">Porção: {porcao_g}g ({medida_caseira})</td></tr>
                            <tr><th style="width: 50%;"></th><th style="width: 25%; text-align: center;">100 g</th><th style="width: 25%; text-align: center;">{porcao_g} g</th><th style="width: 20%; text-align: center;">%VD*</th></tr>
                            <tr><td>Valor energético (kcal)</td><td style="text-align: center;">{v_100[0]:.0f}</td><td style="text-align: center;">{v_porcao[0]:.0f}</td><td style="text-align: center;">{vds_calc[0]}</td></tr>
                            <tr><td>Carboidratos (g)</td><td style="text-align: center;">{v_100[1]:.1f}</td><td style="text-align: center;">{v_porcao[1]:.1f}</td><td style="text-align: center;">{vds_calc[1]}</td></tr>
                            <tr><td>Açúcares adicionados (g)</td><td style="text-align: center;">{v_100[3]:.1f}</td><td style="text-align: center;">{v_porcao[3]:.1f}</td><td style="text-align: center;">{vds_calc[3]}</td></tr>
                            <tr><td>Proteínas (g)</td><td style="text-align: center;">{v_100[4]:.1f}</td><td style="text-align: center;">{v_porcao[4]:.1f}</td><td style="text-align: center;">{vds_calc[4]}</td></tr>
                            <tr><td>Gorduras totais (g)</td><td style="text-align: center;">{v_100[5]:.1f}</td><td style="text-align: center;">{v_porcao[5]:.1f}</td><td style="text-align: center;">{vds_calc[5]}</td></tr>
                            <tr><td>Sódio (mg)</td><td style="text-align: center;">{v_100[9]:.0f}</td><td style="text-align: center;">{v_porcao[9]:.0f}</td><td style="text-align: center;">{vds_calc[9]}</td></tr>
                        </table>
                    </div>
                    """, unsafe_allow_html=True)
        tab_idx += 1

    # NOVO: MÓDULO DE RECURSOS HUMANOS E USUÁRIOS
    if "👥 Gestão de Equipe (RH)" in abas_disponiveis:
        with tabs[tab_idx]:
            st.subheader("👥 Banco de RH e Controle de Acessos")
            st.markdown("Crie credenciais criptografadas para a sua equipe operar a fábrica e os computadores.")
            
            with st.container(border=True):
                c1, c2, c3, c4 = st.columns(4)
                with c1: novo_nome = st.text_input("Nome do Colaborador:")
                with c2: novo_login = st.text_input("Login de Acesso:")
                with c3: nova_senha = st.text_input("Senha:", type="password")
                with c4: novo_perfil = st.selectbox("Nível de Permissão:", ["Operador", "Financeiro", "Gerente", "Mestre"])
                
                if st.button("➕ Cadastrar Funcionário"):
                    if novo_nome and novo_login and nova_senha:
                        try:
                            executar_query("INSERT INTO usuarios (login, nome, senha, perfil) VALUES (?, ?, ?, ?)", (novo_login.lower().strip(), novo_nome, nova_senha, novo_perfil))
                            st.success(f"Funcionário {novo_nome} cadastrado com sucesso!")
                            st.rerun()
                        except:
                            st.error("Erro: Esse login já existe no sistema. Escolha outro.")
                    else:
                        st.error("Preencha todos os campos obrigatórios.")
            
            st.markdown("---")
            st.markdown("### Colaboradores Ativos")
            usuarios_bd = carregar_dados_tabela("SELECT login, nome, perfil FROM usuarios")
            df_usuarios = pd.DataFrame([{"Login": u[0], "Nome": u[1], "Acesso Restrito": u[2]} for u in usuarios_bd])
            st.dataframe(df_usuarios, hide_index=True, use_container_width=True)

# ==========================================
# ⚙️ 5. MÓDULO: TERMINAL DA FÁBRICA
# ==========================================
def painel_fabrica(matriz_receitas, fila_producao, hist_concluidos, usuario):
    # Puxa os operadores do banco (Nível Operador, Gerente e Mestre podem pesar/bater)
    equipe_bd = carregar_dados_tabela("SELECT nome FROM usuarios WHERE perfil IN ('Operador', 'Gerente', 'Mestre')")
    equipe_fabrica = [u[0] for u in equipe_bd]

    if not fila_producao:
        st.success("🎉 Fábrica 100% limpa! Todas as metas foram batidas.")
        return

    lote_atual = fila_producao[0]
    rec_dados = matriz_receitas.get(lote_atual["Receita"], {"ingredientes": {"Base": 1.0}, "und_nome": "Und", "und_peso": 1.0, "modo_preparo": "Seguir procedimento.", "sku": "S/N"})
    
    batidas_planejadas = lote_atual.get("Batidas", 1)
    peso_por_batida = lote_atual['Meta_Kg']
    peso_total_lote = peso_por_batida * batidas_planejadas

    st.markdown(f"""
        <div class="ficha-box">
            <h2 style="margin: 0; color: #60a5fa; text-align: center; text-transform: uppercase;">📋 FICHA DE PRODUÇÃO INDUSTRIAL</h2>
            <h1 style="margin: 10px 0; color: #f8fafc; text-align: center; font-size: 2.2rem;">[{rec_dados['sku']}] {lote_atual['Receita']}</h1>
            <hr style="border-color: #334155;">
            <div style="display: flex; justify-content: space-between; font-size: 1.1rem; font-weight: bold;">
                <span style="color: #34d399;">🎯 LOTE TOTAL: {peso_total_lote} KG ({batidas_planejadas} Batida(s) de {peso_por_batida}kg)</span>
                <span style="color: #cbd5e1;">📦 Rendimento Esperado: ~{int(peso_total_lote / rec_dados['und_peso'])} {rec_dados['und_nome']}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    if lote_atual["Instrucao"]:
        st.warning(f"🔔 **INSTRUÇÃO DE ENVASE DA GERÊNCIA:** {lote_atual['Instrucao']}")

    with st.form(key=f"fechamento_{lote_atual['ID']}", border=True):
        st.markdown("### 1. INGREDIENTES (PESAGEM POR BATIDA)")
        ingredientes = rec_dados["ingredientes"]
        soma_proporcoes = sum(ingredientes.values()) if sum(ingredientes.values()) > 0 else 1
        
        chaves_checkboxes = []
        for ing, prop in ingredientes.items():
            val_por_batida = (prop / soma_proporcoes) * peso_por_batida
            txt_val = f"{(val_por_batida * 1000):.1f} g".replace(".0 g", " g") if val_por_batida < 1.0 else f"{val_por_batida:.3f} kg"
            
            ratio_check = max(1.5, batidas_planejadas * 0.5)
            col_nome, col_tripla, col_peso = st.columns([2, ratio_check, 1.2])
            with col_nome: st.markdown(f"<div style='font-size: 1.15em; font-weight: bold; padding-top: 15px; color: #f8fafc;'>• {ing}</div>", unsafe_allow_html=True)
            with col_tripla:
                cols_b = st.columns(batidas_planejadas)
                for b in range(1, batidas_planejadas + 1):
                    k = f"chk_{lote_atual['ID']}_{ing}_{b}"
                    chaves_checkboxes.append(k)
                    with cols_b[b-1]: st.checkbox(f"{b}x", key=k)
            with col_peso: st.markdown(f"<div style='font-size: 22px; font-weight: 900; color: #34d399; text-align: right; background-color: #0f172a; padding: 10px 12px; border-radius: 6px; border: 1px solid #334155;'>{txt_val}</div>", unsafe_allow_html=True)
            st.markdown("<hr style='margin: 5px 0; border-color: #334155;'>", unsafe_allow_html=True)

        st.markdown("### 2. PASSO A PASSO DO PROCESSO")
        st.markdown(f"<div class='passo-passo-box'>{rec_dados['modo_preparo'].replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)

        st.markdown("### 4. CONTROLE & AUDITORIA DE FECHAMENTO")
        c1, c2 = st.columns(2)
        with c1: pes = st.selectbox("Peseiro Responsável:", equipe_fabrica, index=equipe_fabrica.index(usuario) if usuario in equipe_fabrica else 0)
        with c2: bat = st.selectbox("Batedor Responsável:", equipe_fabrica)
        
        obs = st.text_input("Registro de Ocorrências (Opcional):")
        batidas_realizadas = st.number_input(f"Quantas batidas foram realmente feitas? (Planejado: {batidas_planejadas}):", min_value=1, max_value=batidas_planejadas, value=batidas_planejadas, step=1)
        cx = st.number_input(f"Quantidade Efetivamente Envasada ({rec_dados['und_nome']}):", min_value=0, step=1)
        
        senha_autorizacao = ""
        if batidas_realizadas < batidas_planejadas:
            st.error(f"🚨 **DESVIO DE PRODUÇÃO:** Fechamento reduzido exige Assinatura Eletrônica Gerencial.")
            senha_autorizacao = st.text_input("Senha do Gerente ou Mestre para aprovar a redução:", type="password")

        submit_form = st.form_submit_button("✅ Concluir Lote e Gravar no Banco de Dados", type="primary")
        
        if submit_form:
            autorizado = True
            if batidas_realizadas < batidas_planejadas:
                # Checa na tabela de usuários se a senha digitada é de um Mestre ou Gerente
                validador = carregar_dados_tabela(f"SELECT perfil FROM usuarios WHERE senha='{senha_autorizacao}' AND perfil IN ('Mestre', 'Gerente')")
                if not validador: autorizado = False

            if not autorizado:
                st.error("❌ **Acesso Negado:** Assinatura eletrônica inválida ou sem privilégio de Gerente/Mestre.")
            else:
                if all(st.session_state.get(k, False) for k in chaves_checkboxes) or batidas_realizadas < batidas_planejadas:
                    peso_efetivo_lote = peso_por_batida * batidas_realizadas
                    executar_query("INSERT INTO historico (receita, meta_kg, caixas, peseiro, batedor, obs) VALUES (?, ?, ?, ?, ?, ?)", (lote_atual['Receita'], peso_efetivo_lote, cx, pes, bat, obs + f" [Desvio Aprovado: {batidas_realizadas}/{batidas_planejadas}]"))
                    for ing, prop in ingredientes.items():
                        qtd_usada_total = ((prop / soma_proporcoes) * peso_por_batida) * batidas_realizadas
                        executar_query("UPDATE estoque SET qtd_atual_kg = qtd_atual_kg - ? WHERE ingrediente = ?", (qtd_usada_total, ing))
                    executar_query("DELETE FROM fila_producao WHERE id = ?", (lote_atual['ID'],))
                    st.rerun()
                else:
                    st.warning("⚠️ **Bloqueio Industrial:** Para fechar o lote integral, todas as checagens precisam estar marcadas.")

    st.markdown("<br><h3 style='text-align: center; color:#94a3b8;'>📖 Caderno de Produção (Sumário do Turno)</h3>", unsafe_allow_html=True)
    col_pag1, col_pag2 = st.columns(2)
    with col_pag1:
        with st.container(border=True):
            st.markdown("<h4 style='text-align: center; color: #cbd5e1;'>Página 1: Próximos (A Fazer) ⏳</h4><hr style='margin-top:0;'>", unsafe_allow_html=True)
            if len(fila_producao) > 1:
                for idx, lote in enumerate(fila_producao[1:]): 
                    st.markdown(f"**{idx+2}º** - {lote['Receita']} <span style='color:#60a5fa;'>({lote['Meta_Kg']*lote['Batidas']}kg)</span>", unsafe_allow_html=True)
                    st.markdown("---")
    with col_pag2:
        with st.container(border=True):
            st.markdown("<h4 style='text-align: center; color: #cbd5e1;'>Página 2: Já Finalizados ✅</h4><hr style='margin-top:0;'>", unsafe_allow_html=True)
            if hist_concluidos:
                for lote in hist_concluidos[:10]: 
                    st.markdown(f"✅ **{lote['Receita']}** <span style='color:#94a3b8;'>({lote['Meta']}kg)</span> 📦 {lote['Caixas']} cxs", unsafe_allow_html=True)
                    st.markdown("---")

# ==========================================
# 🚀 6. MOTOR PRINCIPAL (ROTEADOR DE ACESSOS)
# ==========================================
aplicar_css_premium()

if "autenticado" not in st.session_state:
    st.session_state.update({"autenticado": False, "usuario_logado": None, "perfil": None})

if not st.session_state["autenticado"]:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.info("### 🔒 Identificação Obrigatória")
        login_input = st.text_input("Usuário de Acesso:")
        senha_input = st.text_input("Senha Digital:", type="password")
        
        if st.button("Autenticar no Sistema"):
            usuario_validado = carregar_dados_tabela(f"SELECT nome, perfil FROM usuarios WHERE login='{login_input.lower().strip()}' AND senha='{senha_input}'")
            
            if usuario_validado:
                st.session_state.update({"autenticado": True, "usuario_logado": usuario_validado[0][0], "perfil": usuario_validado[0][1]})
                st.rerun()
            else:
                st.error("❌ Credenciais inválidas. Verifique seu login e senha com o RH.")
else:
    st.sidebar.markdown(f"**👤 {st.session_state['usuario_logado']}**<br>🛡️ Cargo: {st.session_state['perfil']}", unsafe_allow_html=True)
    st.sidebar.markdown("---")
    if st.sidebar.button("🔄 Atualizar Tela"): st.rerun()
    if st.sidebar.button("🚪 Encerrar Turno (Sair)"):
        st.session_state.update({"autenticado": False, "usuario_logado": None, "perfil": None})
        st.rerun()

    matriz_receitas = carregar_receitas()
    fila_raw = carregar_dados_tabela("SELECT id, receita, meta_kg, status, instrucao, batidas_total FROM fila_producao ORDER BY id ASC")
    fila = [{"ID": l[0], "Receita": l[1], "Meta_Kg": l[2], "Status": l[3], "Instrucao": l[4] if l[4] else "", "Batidas": l[5] if l[5] else 1} for l in fila_raw if l[1]]
    
    # O MOTOR DE REDIRECIONAMENTO NÍVEL SaaS
    if st.session_state["perfil"] == "Operador":
        linhas_hist = carregar_dados_tabela("SELECT id, receita, meta_kg, caixas, peseiro, batedor, obs, data_hora FROM historico ORDER BY id DESC")
        hist_formatado = [{"ID": l[0], "Receita": l[1], "Meta": l[2], "Caixas": l[3], "Peseiro": l[4], "Batedor": l[5], "Obs": l[6], "Data": l[7]} for l in linhas_hist]
        painel_fabrica(matriz_receitas, fila, hist_formatado, st.session_state["usuario_logado"])
    else:
        estoque_atual = carregar_estoque()
        renderizar_painel_adm(matriz_receitas, fila, estoque_atual, st.session_state["perfil"])