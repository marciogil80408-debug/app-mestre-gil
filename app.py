import streamlit as st
import os
import sqlite3
import pandas as pd
import json
from datetime import datetime

# ==========================================
# ⚙️ 1. CONFIGURAÇÃO GERAL
# ==========================================
st.set_page_config(page_title="App Mestre Gil - ERP", page_icon="🏭", layout="wide")
DB_NAME = "fabrica_gelado.db"

# ==========================================
# 🗄️ 2. MÓDULO DE BANCO DE DADOS
# ==========================================
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS fila_producao (id INTEGER PRIMARY KEY AUTOINCREMENT, receita TEXT, meta_kg REAL, status TEXT, instrucao TEXT DEFAULT '', batidas_total INTEGER DEFAULT 1)''')
    c.execute('''CREATE TABLE IF NOT EXISTS historico (id INTEGER PRIMARY KEY AUTOINCREMENT, receita TEXT, meta_kg REAL, caixas INTEGER, peseiro TEXT, batedor TEXT, obs TEXT, data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS receitas (nome TEXT PRIMARY KEY, ingredientes TEXT, und_nome TEXT DEFAULT 'Caixa 5L', und_peso REAL DEFAULT 2.5, modo_preparo TEXT DEFAULT '', sku TEXT DEFAULT '')''')
    c.execute('''CREATE TABLE IF NOT EXISTS estoque (ingrediente TEXT PRIMARY KEY, custo_kg REAL DEFAULT 0.0, qtd_atual_kg REAL DEFAULT 0.0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS tabela_nutricional (receita TEXT PRIMARY KEY, dados_json TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios (login TEXT PRIMARY KEY, nome TEXT, senha TEXT, perfil TEXT)''')
    
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
            "modo_preparo": l[4] if l[4] else "1. Adicionar líquidos no tanque.\n2. Incorporar sólidos sob agitação.",
            "sku": l[5] if l[5] else "S/N"
        }
    return receitas_db

def carregar_estoque():
    linhas = carregar_dados_tabela("SELECT ingrediente, custo_kg, qtd_atual_kg FROM estoque")
    return {l[0]: {"custo_kg": l[1], "qtd_atual_kg": l[2]} for l in linhas}

init_db()

# ==========================================
# 🎨 3. MÓDULO DE ESTILIZAÇÃO CSS CLEAN
# ==========================================
def aplicar_css_premium():
    st.markdown("""
        <style>
        /* Botões Padrões Industriais */
        .stButton button[kind="secondary"] { border-radius: 8px; font-weight: bold; transition: all 0.3s ease; }
        
        /* 🔥 BOTÃO GIGANTE VERDE: "SINAL VERDE" */
        .stButton button[kind="primary"] {
            background: linear-gradient(135deg, #10b981, #059669) !important; color: white !important;
            font-weight: 900 !important; border-radius: 8px !important; border: none !important;
            padding: 0.8rem !important; font-size: 1.1em !important; box-shadow: 0 4px 10px rgba(16, 185, 129, 0.4) !important;
        }
        .stButton button[kind="primary"]:hover { background: linear-gradient(135deg, #059669, #047857) !important; transform: translateY(-2px); }

        /* LAPIDAÇÃO DA LOGO E CHECKBOXES DA FÁBRICA */
        [data-testid="stImage"] img { border-radius: 15px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3); }
        input[type="checkbox"] { transform: scale(1.5); cursor: pointer; }
        [data-testid="stCheckbox"] span[data-baseweb="checkbox"] > div { border: 2px solid #60a5fa !important; border-radius: 4px !important; }
        
        /* Design Clean para os Painéis */
        .ficha-box { background-color: rgba(30, 41, 59, 0.5); border: 2px solid #3b82f6; border-radius: 12px; padding: 25px; margin-bottom: 25px; }
        .passo-passo-box { background-color: rgba(17, 24, 39, 0.7); border-left: 4px solid #10b981; padding: 15px; border-radius: 6px; font-family: monospace; color: #34d399; }
        
        /* Tabela Anvisa Branca Oficial */
        .anvisa-table { width: 100%; max-width: 500px; border-collapse: collapse; font-family: Arial, sans-serif; background-color: white !important; color: black !important; margin: 0 auto; border: 2px solid black; }
        .anvisa-table th, .anvisa-table td, .anvisa-table span, .anvisa-table div { color: black !important; background-color: white !important; }
        .anvisa-table th, .anvisa-table td { border-bottom: 1px solid black; padding: 6px 4px; text-align: left; font-size: 14px; }
        .anvisa-table th { font-weight: 900; border-bottom: 2px solid black; }
        .anvisa-header { text-align: center; font-weight: 900; font-size: 20px; padding: 10px 0; border-bottom: 5px solid black; }
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
    st.markdown("Bem-vindo ao centro de comando. Selecione um módulo abaixo:")
    
    abas_disponiveis = []
    if perfil in ["Mestre", "Gerente"]: abas_disponiveis.append("🏭 Gestão da Fila")
    if perfil in ["Mestre", "Gerente", "Financeiro"]: abas_disponiveis.append("📦 Estoque")
    if perfil in ["Mestre", "Financeiro"]: abas_disponiveis.append("💰 Precificação (CMV)")
    if perfil in ["Mestre", "Gerente", "Financeiro"]: abas_disponiveis.append("📊 Dashboards")
    if perfil == "Mestre": abas_disponiveis.append("🔐 Cofre P&D")
    if perfil in ["Mestre", "Financeiro"]: abas_disponiveis.append("🍎 Anvisa")
    if perfil in ["Mestre", "Gerente"]: abas_disponiveis.append("👥 RH")

    tabs = st.tabs(abas_disponiveis)
    tab_idx = 0

    if "🏭 Gestão da Fila" in abas_disponiveis:
        with tabs[tab_idx]:
            col1, col2 = st.columns([1.2, 1])
            
            with col1:
                st.subheader("⚙️ Enviar Ordem de Produção")
                if not matriz_receitas:
                    st.info("Cadastre receitas no Cofre de P&D primeiro.")
                else:
                    # Uso de st.form para organizar visualmente o envio da ordem
                    with st.form("form_ordem", border=True):
                        lista_produtos = [f"[{v['sku']}] {k}" for k, v in matriz_receitas.items()]
                        selecao = st.selectbox("Selecione o Produto (SKU):", lista_produtos)
                        receita_escolhida = selecao.split("] ")[1] if "] " in selecao else selecao
                        
                        c_meta, c_batidas = st.columns(2)
                        with c_meta: meta_escolhida = st.number_input("Peso por Batida (kg):", min_value=1.0, value=150.0, step=1.0)
                        with c_batidas: batidas_qtd = st.number_input("Quantas Batidas?", min_value=1, value=1, step=1)
                        
                        instrucao_envase = st.text_input("Instruções (Opcional):", placeholder="Ex: Rende 30 caixas")
                        
                        submit_ordem = st.form_submit_button("🚀 Enviar para a Fábrica", type="primary")
                        if submit_ordem:
                            executar_query("INSERT INTO fila_producao (receita, meta_kg, status, instrucao, batidas_total) VALUES (?, ?, 'Pendente', ?, ?)", (receita_escolhida, meta_escolhida, instrucao_envase, batidas_qtd))
                            st.rerun()
            
            with col2:
                st.subheader("📋 Status da Fábrica")
                if not fila_producao:
                    st.success("Tudo limpo! Nenhuma ordem pendente.")
                else:
                    for idx, lote in enumerate(fila_producao):
                        with st.container(border=True):
                            st.markdown(f"**#{idx + 1} | {lote['Receita']}**")
                            st.caption(f"🎯 {lote['Batidas']} Batidas de {lote['Meta_Kg']}kg")
                            if idx > 0:
                                if st.button(f"⬆️ Priorizar Lote #{idx+1}", key=f"prio_{lote['ID']}"):
                                    fila_producao.remove(lote)
                                    fila_producao.insert(0, lote)
                                    executar_query("DELETE FROM fila_producao")
                                    for l in fila_producao: executar_query("INSERT INTO fila_producao (receita, meta_kg, status, instrucao, batidas_total) VALUES (?, ?, ?, ?, ?)", (l["Receita"], l["Meta_Kg"], l["Status"], l["Instrucao"], l["Batidas"]))
                                    st.rerun()
        tab_idx += 1

    if "📦 Estoque" in abas_disponiveis:
        with tabs[tab_idx]:
            st.subheader("📦 Gestão de Estoque e Preços")
            ingredientes_unicos = set()
            for rec in matriz_receitas.values():
                for ing in rec["ingredientes"].keys(): ingredientes_unicos.add(ing)
            for ing in ingredientes_unicos:
                if ing not in estoque_atual: executar_query("INSERT INTO estoque (ingrediente, custo_kg, qtd_atual_kg) VALUES (?, 0.0, 0.0)", (ing,))
            
            df_estoque = pd.DataFrame([{"Insumo": k, "Custo (R$/Kg)": v["custo_kg"], "Estoque (Kg)": v["qtd_atual_kg"]} for k, v in carregar_estoque().items()])
            df_editado = st.data_editor(df_estoque, hide_index=True, use_container_width=True)
            if st.button("💾 Salvar Estoque", type="primary"):
                for _, row in df_editado.iterrows(): executar_query("UPDATE estoque SET custo_kg = ?, qtd_atual_kg = ? WHERE ingrediente = ?", (float(row["Custo (R$/Kg)"]), float(row["Estoque (Kg)"]), row["Insumo"]))
                st.success("Estoque atualizado!")
                st.rerun()
        tab_idx += 1

    if "💰 Precificação (CMV)" in abas_disponiveis:
        with tabs[tab_idx]:
            st.subheader("💰 Precificação de Produtos (CMV)")
            if matriz_receitas:
                rec_fin = st.selectbox("Selecione o Produto:", list(matriz_receitas.keys()))
                dados = matriz_receitas[rec_fin]
                st.caption(f"Embalagem padrão: {dados['und_nome']} ({dados['und_peso']} kg)")
                
                soma = sum(dados["ingredientes"].values()) if sum(dados["ingredientes"].values()) > 0 else 1
                custo_total = 0.0
                detalhes = []

                for ing, prop in dados["ingredientes"].items():
                    c_bd = estoque_atual.get(ing, {}).get("custo_kg", 0.0)
                    qtd = (prop / soma) * dados["und_peso"]
                    custo_ing = qtd * c_bd
                    custo_total += custo_ing
                    detalhes.append({"Ingrediente": ing, "Qtd": f"{qtd*1000:.0f}g" if qtd < 1 else f"{qtd:.2f}kg", "Custo": f"R$ {custo_ing:.2f}"})

                c1, c2 = st.columns([1, 1])
                with c1:
                    st.dataframe(pd.DataFrame(detalhes), hide_index=True, use_container_width=True)
                    st.info(f"**Custo Físico Total:** R$ {custo_total:.2f}")
                with c2:
                    with st.container(border=True):
                        preco = st.number_input("Preço de Venda Praticado (R$):", min_value=0.0, value=custo_total*2 if custo_total>0 else 10.0)
                        lucro = preco - custo_total
                        margem = (lucro / preco * 100) if preco > 0 else 0
                        st.metric("Lucro Limpo por Und", f"R$ {lucro:.2f}")
                        st.metric("Margem de Lucro", f"{margem:.1f}%")
                        if margem < 30: st.error("🚨 Margem Perigosa")
                        else: st.success("✅ Margem Saudável")
            else: st.info("Cadastre receitas primeiro.")
        tab_idx += 1

    if "📊 Dashboards" in abas_disponiveis:
        with tabs[tab_idx]:
            st.subheader("📊 Fechamento e Resultados")
            df_hist = pd.read_sql_query("SELECT receita, meta_kg, caixas, batedor, data_hora FROM historico", sqlite3.connect(DB_NAME))
            if not df_hist.empty:
                df_hist['Data_Curta'] = pd.to_datetime(df_hist['data_hora']).dt.strftime('%Y-%m-%d')
                df_hoje = df_hist[df_hist['Data_Curta'] == datetime.now().strftime("%Y-%m-%d")]
                
                with st.container(border=True):
                    st.markdown("### 🏆 Turno de Hoje")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Kg Batidos", f"{df_hoje['meta_kg'].sum():.1f} kg")
                    c2.metric("Unidades Envasadas", int(df_hoje['caixas'].sum()))
                    c3.metric("Lotes Fechados", len(df_hoje))
                
                st.markdown("### 📈 Histórico Geral")
                st.dataframe(df_hist.drop(columns=['Data_Curta']), use_container_width=True)
        tab_idx += 1
            
    if "🔐 Cofre P&D" in abas_disponiveis:
        with tabs[tab_idx]:
            st.subheader("🔐 Cofre de Formulações (P&D)")
            
            with st.form("form_nova_receita", border=True):
                st.markdown("### ➕ Nova Formulação")
                c1, c2 = st.columns([1, 3])
                with c1: sku = st.text_input("SKU (Ex: ACAI-01):")
                with c2: nome = st.text_input("Nome Comercial do Sabor:")
                
                c3, c4 = st.columns(2)
                with c3: und_nome = st.text_input("Tipo Embalagem (Ex: Caixa 5L):")
                with c4: und_peso = st.number_input("Peso (kg):", value=2.500, format="%.3f")
                
                modo_preparo = st.text_area("Procedimento Operacional Padrão:")
                
                st.markdown("**Matriz de Ingredientes (Proporções):**")
                df_vazio = pd.DataFrame([{"Ingrediente": "", "Quantidade": 0.0} for _ in range(12)])
                df_ing = st.data_editor(df_vazio, num_rows="dynamic", use_container_width=True)
                
                if st.form_submit_button("💾 Blindar Formulação", type="primary"):
                    formula = {str(r["Ingrediente"]).strip(): float(r["Quantidade"]) for _, r in df_ing.iterrows() if str(r["Ingrediente"]).strip() != "" and float(r["Quantidade"]) > 0}
                    if nome and und_nome and formula and sku:
                        executar_query("INSERT OR REPLACE INTO receitas (nome, ingredientes, und_nome, und_peso, modo_preparo, sku) VALUES (?, ?, ?, ?, ?, ?)", (nome, json.dumps(formula), und_nome, und_peso, modo_preparo, sku.upper()))
                        st.success("Formulação salva no cofre!")
                        st.rerun()
                    else: st.error("Preencha SKU, Nome e ingredientes.")

            if matriz_receitas:
                st.markdown("### 📚 Arquivo Geral")
                for rec, dados in matriz_receitas.items():
                    with st.expander(f"📖 [{dados['sku']}] {rec}"):
                        st.json(dados["ingredientes"])
                        st.info(dados["modo_preparo"])
                        if st.button(f"🗑️ Excluir", key=f"del_{rec}"):
                            executar_query("DELETE FROM receitas WHERE nome = ?", (rec,))
                            st.rerun()
        tab_idx += 1

    if "🍎 Anvisa" in abas_disponiveis:
        with tabs[tab_idx]:
            st.subheader("🍎 Geração de Rotulagem Nutricional")
            if matriz_receitas:
                rec_selec = st.selectbox("Selecione a Formulação:", list(matriz_receitas.keys()))
                salvos = carregar_dados_tabela(f"SELECT dados_json FROM tabela_nutricional WHERE receita = '{rec_selec}'")
                d_salvos = json.loads(salvos[0][0]) if salvos else {}
                
                c1, c2 = st.columns(2)
                with c1: porcao = st.number_input("Porção (g):", value=d_salvos.get("porcao_g", 60.0))
                with c2: caseira = st.text_input("Medida Caseira:", value=d_salvos.get("medida_caseira", "1 bola"))
                
                df_nutri = pd.DataFrame([
                    {"Nutriente": "Energia (kcal)", "Valor/100g": d_salvos.get("energia", 0.0)},
                    {"Nutriente": "Carboidratos (g)", "Valor/100g": d_salvos.get("carbo", 0.0)},
                    {"Nutriente": "Açúcares Adicionados (g)", "Valor/100g": d_salvos.get("acucar_add", 0.0)},
                    {"Nutriente": "Proteínas (g)", "Valor/100g": d_salvos.get("prot", 0.0)},
                    {"Nutriente": "Gorduras Totais (g)", "Valor/100g": d_salvos.get("gord_tot", 0.0)},
                    {"Nutriente": "Sódio (mg)", "Valor/100g": d_salvos.get("sodio", 0.0)},
                ])
                df_ed = st.data_editor(df_nutri, hide_index=True, use_container_width=True)
                
                if st.button("💾 Gerar Rótulo", type="primary"):
                    val = df_ed["Valor/100g"].tolist()
                    j = json.dumps({"porcao_g": porcao, "medida_caseira": caseira, "energia": val[0], "carbo": val[1], "acucar_tot":0, "acucar_add": val[2], "prot": val[3], "gord_tot": val[4], "gord_sat":0, "gord_trans":0, "fibra":0, "sodio": val[5]})
                    executar_query("INSERT OR REPLACE INTO tabela_nutricional (receita, dados_json) VALUES (?, ?)", (rec_selec, j))
                    st.success("Tabela gerada.")
                    st.rerun()

                if d_salvos:
                    st.markdown("<br><div style='background-color: white; padding: 20px; border-radius: 8px;'><table class='anvisa-table'><tr><td colspan='2' class='anvisa-header'>INFORMAÇÃO NUTRICIONAL</td></tr></table></div>", unsafe_allow_html=True)
        tab_idx += 1

    if "👥 RH" in abas_disponiveis:
        with tabs[tab_idx]:
            st.subheader("👥 Gestão de Acessos")
            with st.form("form_rh", border=True):
                c1, c2, c3, c4 = st.columns(4)
                with c1: n_nome = st.text_input("Nome:")
                with c2: n_login = st.text_input("Login:")
                with c3: n_senha = st.text_input("Senha:", type="password")
                with c4: n_perfil = st.selectbox("Perfil:", ["Operador", "Financeiro", "Gerente", "Mestre"])
                
                if st.form_submit_button("➕ Cadastrar", type="primary"):
                    if n_nome and n_login and n_senha:
                        executar_query("INSERT INTO usuarios (login, nome, senha, perfil) VALUES (?, ?, ?, ?)", (n_login.lower().strip(), n_nome, n_senha, n_perfil))
                        st.success("Usuário Cadastrado!")
                        st.rerun()
            st.dataframe(pd.DataFrame([{"Login": u[0], "Nome": u[1], "Perfil": u[2]} for u in carregar_dados_tabela("SELECT login, nome, perfil FROM usuarios")]), use_container_width=True)

# ==========================================
# ⚙️ 5. MÓDULO: TERMINAL DA FÁBRICA
# ==========================================
def painel_fabrica(matriz_receitas, fila_producao, hist_concluidos, usuario):
    equipe_fabrica = [u[0] for u in carregar_dados_tabela("SELECT nome FROM usuarios WHERE perfil IN ('Operador', 'Gerente', 'Mestre')")]

    if not fila_producao:
        st.success("🎉 Fábrica Limpa! Todas as ordens foram concluídas.")
        return

    lote_atual = fila_producao[0]
    rec_dados = matriz_receitas.get(lote_atual["Receita"], {"ingredientes": {"Base": 1.0}, "und_nome": "Und", "und_peso": 1.0, "modo_preparo": "Siga o POP.", "sku": "S/N"})
    
    peso_por_batida = lote_atual['Meta_Kg']
    batidas = lote_atual['Batidas']

    st.markdown(f"""
        <div class="ficha-box">
            <h2 style="margin: 0; color: #60a5fa; text-align: center; text-transform: uppercase;">📋 FICHA DE PRODUÇÃO</h2>
            <h1 style="margin: 5px 0; color: #f8fafc; text-align: center; font-size: 2.2rem;">[{rec_dados['sku']}] {lote_atual['Receita']}</h1>
            <div style="text-align: center; font-size: 1.1rem; font-weight: bold; color: #34d399;">
                🎯 LOTE: {peso_por_batida * batidas} KG ({batidas} Batidas de {peso_por_batida}kg)
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    if lote_atual["Instrucao"]: st.warning(f"🔔 **GERÊNCIA:** {lote_atual['Instrucao']}")

    with st.form(key=f"fechamento_{lote_atual['ID']}", border=True):
        st.markdown(f"### 1. PESAGEM (Valores para **UMA ÚNICA** batida)")
        soma_prop = sum(rec_dados["ingredientes"].values()) if sum(rec_dados["ingredientes"].values()) > 0 else 1
        
        chaves = []
        for ing, prop in rec_dados["ingredientes"].items():
            val = (prop / soma_prop) * peso_por_batida
            txt = f"{(val * 1000):.1f} g" if val < 1.0 else f"{val:.3f} kg"
            
            c1, c2, c3 = st.columns([2, max(1.5, batidas*0.5), 1.2])
            with c1: st.markdown(f"<div style='font-weight: bold; padding-top: 10px; font-size: 1.1em;'>• {ing}</div>", unsafe_allow_html=True)
            with c2:
                cols = st.columns(batidas)
                for b in range(1, batidas + 1):
                    k = f"chk_{lote_atual['ID']}_{ing}_{b}"
                    chaves.append(k)
                    with cols[b-1]: st.checkbox(f"{b}x", key=k)
            with c3: st.markdown(f"<div style='font-size: 20px; font-weight: 900; color: #34d399; text-align: right; background-color: rgba(15,23,42,0.5); padding: 5px; border-radius: 6px;'>{txt}</div>", unsafe_allow_html=True)
            st.divider()

        st.markdown("### 2. PROCEDIMENTO")
        st.info(rec_dados['modo_preparo'])

        st.markdown("### 3. AUDITORIA")
        c1, c2 = st.columns(2)
        with c1: pes = st.selectbox("Peseiro:", equipe_fabrica, index=equipe_fabrica.index(usuario) if usuario in equipe_fabrica else 0)
        with c2: bat = st.selectbox("Batedor:", equipe_fabrica)
        
        obs = st.text_input("Ocorrências:")
        b_real = st.number_input(f"Batidas reais feitas:", min_value=1, max_value=batidas, value=batidas)
        cx = st.number_input(f"Embalagens finalizadas:", min_value=0, step=1)
        
        senha_auth = ""
        if b_real < batidas:
            st.error("🚨 Desvio detectado. Assinatura do Gerente exigida:")
            senha_auth = st.text_input("Senha Gerencial:", type="password")

        if st.form_submit_button("✅ GRAVAR E CONCLUIR LOTE", type="primary"):
            auth = True
            if b_real < batidas:
                v = carregar_dados_tabela(f"SELECT perfil FROM usuarios WHERE senha='{senha_auth}' AND perfil IN ('Mestre', 'Gerente')")
                if not v: auth = False

            if not auth: st.error("❌ Assinatura inválida.")
            else:
                if all(st.session_state.get(k, False) for k in chaves) or b_real < batidas:
                    peso_real = peso_por_batida * b_real
                    executar_query("INSERT INTO historico (receita, meta_kg, caixas, peseiro, batedor, obs) VALUES (?, ?, ?, ?, ?, ?)", (lote_atual['Receita'], peso_real, cx, pes, bat, obs))
                    executar_query("DELETE FROM fila_producao WHERE id = ?", (lote_atual['ID'],))
                    st.rerun()
                else: st.warning("⚠️ Marque todas as pesagens.")

# ==========================================
# 🚀 6. MOTOR DE LOGIN
# ==========================================
aplicar_css_premium()

if "autenticado" not in st.session_state: st.session_state.update({"autenticado": False, "usuario_logado": None, "perfil": None})

if not st.session_state["autenticado"]:
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, col2, _ = st.columns([1, 1.5, 1])
    with col2:
        with st.form("login_form", border=True):
            st.markdown("<h3 style='text-align:center;'>🔒 Acesso ao Sistema</h3>", unsafe_allow_html=True)
            login_in = st.text_input("Usuário:")
            senha_in = st.text_input("Senha:", type="password")
            if st.form_submit_button("Entrar", type="primary"):
                user = carregar_dados_tabela(f"SELECT nome, perfil FROM usuarios WHERE login='{login_in.lower().strip()}' AND senha='{senha_in}'")
                if user:
                    st.session_state.update({"autenticado": True, "usuario_logado": user[0][0], "perfil": user[0][1]})
                    st.rerun()
                else: st.error("Credenciais inválidas.")
else:
    st.sidebar.markdown(f"👤 **{st.session_state['usuario_logado']}**\n\n🛡️ Perfil: {st.session_state['perfil']}")
    st.sidebar.divider()
    if st.sidebar.button("🔄 Sincronizar"): st.rerun()
    if st.sidebar.button("🚪 Sair"):
        st.session_state.update({"autenticado": False, "usuario_logado": None, "perfil": None})
        st.rerun()

    matriz = carregar_receitas()
    fila_raw = carregar_dados_tabela("SELECT id, receita, meta_kg, status, instrucao, batidas_total FROM fila_producao ORDER BY id ASC")
    fila = [{"ID": l[0], "Receita": l[1], "Meta_Kg": l[2], "Status": l[3], "Instrucao": l[4], "Batidas": l[5]} for l in fila_raw if l[1]]
    
    if st.session_state["perfil"] == "Operador":
        hist = [{"ID": l[0], "Receita": l[1], "Meta": l[2], "Caixas": l[3]} for l in carregar_dados_tabela("SELECT id, receita, meta_kg, caixas FROM historico ORDER BY id DESC")]
        painel_fabrica(matriz, fila, hist, st.session_state["usuario_logado"])
    else:
        renderizar_painel_adm(matriz, fila, carregar_estoque(), st.session_state["perfil"])
