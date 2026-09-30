import streamlit as st
import os
import sqlite3
import pandas as pd
import json
from datetime import datetime, timedelta

# ==========================================
# ⚙️ 1. CONFIGURAÇÃO GERAL
# ==========================================
st.set_page_config(page_title="App Mestre Gil - ERP Industrial", page_icon="🏭", layout="wide")
DB_NAME = "fabrica_gelado.db"

# ==========================================
# 🗄️️ 2. BANCO DE DADOS & SEGURANÇA
# ==========================================
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS fila_producao (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        receita TEXT, 
        meta_kg REAL, 
        status TEXT, 
        instrucao TEXT DEFAULT '', 
        batidas_total INTEGER DEFAULT 1
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS historico (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        receita TEXT, 
        meta_kg REAL, 
        caixas INTEGER, 
        peseiro TEXT, 
        batedor TEXT, 
        obs TEXT, 
        data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS receitas (
        nome TEXT PRIMARY KEY, 
        ingredientes TEXT, 
        und_nome TEXT DEFAULT 'Caixa 5L', 
        und_peso REAL DEFAULT 2.5, 
        modo_preparo TEXT DEFAULT '', 
        sku TEXT DEFAULT ''
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS estoque (
        ingrediente TEXT PRIMARY KEY, 
        custo_kg REAL DEFAULT 0.0, 
        qtd_atual_kg REAL DEFAULT 0.0
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS tabela_nutricional (
        receita TEXT PRIMARY KEY, 
        dados_json TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        login TEXT PRIMARY KEY, 
        nome TEXT, 
        senha TEXT, 
        perfil TEXT
    )''')
    
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
            "ingredientes": json.loads(l[1]), 
            "und_nome": l[2], 
            "und_peso": l[3],
            "modo_preparo": l[4] if l[4] else "1. Adicionar líquidos no tanque.\n2. Incorporar sólidos sob agitação.\n3. Homogeneizar até textura uniforme.",
            "sku": l[5] if l[5] else "S/N"
        }
    return receitas_db

def carregar_estoque():
    linhas = carregar_dados_tabela("SELECT ingrediente, custo_kg, qtd_atual_kg FROM estoque")
    return {l[0]: {"custo_kg": l[1], "qtd_atual_kg": l[2]} for l in linhas}

init_db()

# ==========================================
# 🎨 3. DESIGN EXECUTIVO POLIDO (CSS REFINADO)
# ==========================================
def aplicar_css_premium():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;900&display=swap');
        
        * {
            font-family: 'Inter', sans-serif;
        }

        .block-container {
            padding-top: 1.8rem !important;
            padding-bottom: 2rem !important;
        }

        [data-testid="stSidebar"] {
            background-color: #0b1120 !important;
            border-right: 1px solid #1e293b !important;
        }
        
        [data-testid="stSidebar"] .stRadio > div {
            gap: 6px !important;
        }
        [data-testid="stSidebar"] .stRadio label {
            background: #111827 !important;
            border: 1px solid #1f2937 !important;
            padding: 10px 14px !important;
            border-radius: 8px !important;
            cursor: pointer !important;
            transition: all 0.2s ease !important;
            display: flex !important;
            align-items: center !important;
            width: 100% !important;
            margin: 0 !important;
        }
        [data-testid="stSidebar"] .stRadio label > div:first-child {
            display: none !important;
        }
        [data-testid="stSidebar"] .stRadio label div[data-testid="stMarkdownContainer"] p {
            font-size: 0.92rem !important;
            font-weight: 600 !important;
            color: #cbd5e1 !important;
            margin: 0 !important;
        }
        [data-testid="stSidebar"] .stRadio label:hover {
            background: #1e293b !important;
            border-color: #38bdf8 !important;
            transform: translateX(4px) !important;
        }
        [data-testid="stSidebar"] .stRadio label:has(input:checked) {
            background: linear-gradient(90deg, #1e293b 0%, #0f172a 100%) !important;
            border-color: #38bdf8 !important;
            border-left: 4px solid #38bdf8 !important;
            box-shadow: 0 4px 12px rgba(56, 189, 248, 0.15) !important;
        }
        [data-testid="stSidebar"] .stRadio label:has(input:checked) p {
            color: #38bdf8 !important;
            font-weight: 800 !important;
        }

        .stButton button[kind="secondary"], .stButton button:not([kind="primary"]) {
            background: #1e293b !important;
            color: #f1f5f9 !important;
            border: 1px solid #334155 !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            transition: all 0.2s ease;
        }
        .stButton button[kind="secondary"]:hover, .stButton button:not([kind="primary"]):hover {
            background: #334155 !important;
            border-color: #64748b !important;
            color: white !important;
        }
        
        .stButton button[kind="primary"] { 
            background: linear-gradient(135deg, #10b981 0%, #047857 100%) !important; 
            color: white !important; 
            font-weight: 800 !important; 
            border-radius: 8px !important; 
            border: none !important; 
            padding: 0.75rem 1.2rem !important; 
            font-size: 1rem !important; 
            box-shadow: 0 4px 14px rgba(16, 185, 129, 0.3) !important;
            transition: all 0.2s ease;
        }
        .stButton button[kind="primary"]:hover { 
            background: linear-gradient(135deg, #059669 0%, #065f46 100%) !important; 
            transform: translateY(-2px);
            box-shadow: 0 6px 18px rgba(16, 185, 129, 0.45) !important;
        }

        .btn-cancelar button {
            background: #dc2626 !important; 
            color: white !important;
            border: none !important;
        }
        .btn-cancelar button:hover {
            background: #b91c1c !important;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: #0b1120;
            padding: 6px;
            border-radius: 10px;
            border: 1px solid #1e293b;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 6px;
            color: #94a3b8;
            font-weight: 600;
            padding: 8px 16px;
            border: none !important;
        }
        .stTabs [aria-selected="true"] {
            background-color: #1e293b !important;
            color: #38bdf8 !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
        }

        .ficha-box { 
            background: linear-gradient(180deg, #111827 0%, #0f172a 100%);
            border: 1px solid #2563eb; 
            border-radius: 12px; 
            padding: 22px; 
            margin-bottom: 20px; 
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
        }
        .passo-passo-box { 
            background-color: #030712; 
            border-left: 4px solid #10b981; 
            padding: 14px; 
            border-radius: 6px; 
            font-family: monospace; 
            color: #34d399; 
            font-size: 0.95rem;
        }

        .anvisa-table { width: 100%; max-width: 500px; border-collapse: collapse; font-family: Arial, sans-serif; background-color: white !important; color: black !important; margin: 0 auto; border: 2px solid black; }
        .anvisa-table th, .anvisa-table td { color: black !important; background-color: white !important; border-bottom: 1px solid black; padding: 6px 4px; text-align: left; font-size: 14px; }
        .anvisa-table th { font-weight: 900; border-bottom: 2px solid black; }
        .anvisa-header { text-align: center; font-weight: 900; font-size: 20px; padding: 10px 0; border-bottom: 5px solid black; }
        .anvisa-sub { font-size: 12px; font-weight: bold; border-bottom: 1px solid black; padding: 4px; }

        @media print {
            header, footer, [data-testid="stSidebar"], .stButton, nav, #MainMenu {
                display: none !important;
            }
            body, .stApp {
                background: white !important;
                color: black !important;
            }
            .print-area {
                width: 100% !important;
                margin: 0 !important;
                padding: 10px !important;
                color: black !important;
                background: white !important;
                border: 2px solid black !important;
            }
            .print-area * {
                color: black !important;
            }
        }
        </style>
    """, unsafe_allow_html=True)

# ==========================================
# ⚙️ 4. TERMINAL DA FÁBRICA (OPERADOR / PESEIRO)
# ==========================================
def painel_fabrica(matriz_receitas, fila_producao, hist_concluidos, usuario):
    equipe_fabrica = [u[0] for u in carregar_dados_tabela("SELECT nome FROM usuarios WHERE perfil IN ('Operador', 'Gerente', 'Mestre')")]

    st.subheader("📋 Painel do Operador - Fila de Produção Ativa")
    
    if not fila_producao:
        st.success("🎉 Fábrica 100% limpa! Nenhuma ordem pendente no momento.")
        return

    lote_atual = fila_producao[0]
    rec_dados = matriz_receitas.get(lote_atual["Receita"], {"ingredientes": {"Base": 1.0}, "und_nome": "Und", "und_peso": 1.0, "modo_preparo": "Seguir procedimento padrão.", "sku": "S/N"})
    
    batidas_planejadas = lote_atual.get("Batidas", 1)
    peso_por_batida = lote_atual['Meta_Kg']
    peso_total_lote = peso_por_batida * batidas_planejadas

    st.markdown(f"""
        <div class="ficha-box notranslate" translate="no">
            <h3 style="margin: 0; color: #38bdf8; text-align: center; text-transform: uppercase; letter-spacing: 1px;">📋 FICHA DE PRODUÇÃO EM ANDAMENTO</h3>
            <h1 style="margin: 8px 0; color: #f8fafc; text-align: center; font-size: 2.2rem;">[{rec_dados['sku']}] {lote_atual['Receita']}</h1>
            <div style="display: flex; justify-content: space-between; font-size: 1.05rem; font-weight: 700; margin-top: 10px; background: #0f172a; padding: 10px 16px; border-radius: 8px; border: 1px solid #1e293b;">
                <span style="color: #34d399;">🎯 LOTE TOTAL: {peso_total_lote} KG ({batidas_planejadas} Batida(s) de {peso_por_batida}kg)</span>
                <span style="color: #cbd5e1;">📦 Rendimento Estimado: ~{int(peso_total_lote / rec_dados['und_peso'])} {rec_dados['und_nome']}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    if lote_atual["Instrucao"]:
        st.warning(f"🔔 **INSTRUÇÃO DE ENVASE DA GERÊNCIA:** {lote_atual['Instrucao']}")

    with st.form(key=f"fechamento_{lote_atual['ID']}", border=True):
        st.markdown("### 1. PESAGEM DE INGREDIENTES (VALORES POR BATIDA)")
        ingredientes = rec_dados["ingredientes"]
        soma_proporcoes = sum(ingredientes.values()) if sum(ingredientes.values()) > 0 else 1
        
        chaves_checkboxes = []
        for ing, prop in ingredientes.items():
            val_por_batida = (prop / soma_proporcoes) * peso_por_batida
            txt_val = f"{(val_por_batida * 1000):.1f} g".replace(".0 g", " g") if val_por_batida < 1.0 else f"{val_por_batida:.3f} kg"
            
            ratio_check = max(1.5, batidas_planejadas * 0.5)
            col_nome, col_tripla, col_peso = st.columns([2, ratio_check, 1.2])
            with col_nome: st.markdown(f"<div class='notranslate' translate='no' style='font-size: 1.1em; font-weight: 700; padding-top: 12px; color: #f8fafc;'>• {ing}</div>", unsafe_allow_html=True)
            with col_tripla:
                cols_b = st.columns(batidas_planejadas)
                for b in range(1, batidas_planejadas + 1):
                    k = f"chk_{lote_atual['ID']}_{ing}_{b}"
                    chaves_checkboxes.append(k)
                    with cols_b[b-1]: st.checkbox(f"{b}ª", key=k)
            with col_peso: st.markdown(f"<div style='font-size: 20px; font-weight: 900; color: #34d399; text-align: right; background-color: #0b1120; padding: 8px 12px; border-radius: 6px; border: 1px solid #1e293b;'>{txt_val}</div>", unsafe_allow_html=True)
            st.divider()

        st.markdown("### 2. PASSO A PASSO OPERACIONAL (POP)")
        st.markdown(f"<div class='passo-passo-box notranslate' translate='no'>{rec_dados['modo_preparo'].replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)

        st.markdown("### 3. CONTROLE & AUDITORIA DE FECHAMENTO")
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

        submit_form = st.form_submit_button("✅ Concluir Lote e Baixar Estoque", type="primary")
        
        if submit_form:
            autorizado = True
            if batidas_realizadas < batidas_planejadas:
                validador = carregar_dados_tabela(f"SELECT perfil FROM usuarios WHERE senha='{senha_autorizacao}' AND perfil IN ('Mestre', 'Gerente')")
                if not validador: autorizado = False

            if not autorizado:
                st.error("❌ **Acesso Negado:** Assinatura eletrônica inválida ou sem privilégio de Gerente/Mestre.")
            else:
                if all(st.session_state.get(k, False) for k in chaves_checkboxes) or batidas_realizadas < batidas_planejadas:
                    peso_efetivo_lote = peso_por_batida * batidas_realizadas
                    executar_query("INSERT INTO historico (receita, meta_kg, caixas, peseiro, batedor, obs) VALUES (?, ?, ?, ?, ?, ?)", (lote_atual['Receita'], peso_efetivo_lote, cx, pes, bat, obs + f" [Batidas Feitas: {batidas_realizadas}/{batidas_planejadas}]"))
                    for ing, prop in ingredientes.items():
                        qtd_usada_total = ((prop / soma_proporcoes) * peso_por_batida) * batidas_realizadas
                        executar_query("UPDATE estoque SET qtd_atual_kg = qtd_atual_kg - ? WHERE ingrediente = ?", (qtd_usada_total, ing))
                    executar_query("DELETE FROM fila_producao WHERE id = ?", (lote_atual['ID'],))
                    st.rerun()
                else:
                    st.warning("⚠️ **Atenção:** Marque todas as pesagens para confirmar que foram pesadas.")

    st.markdown("<br><h3 style='text-align: center; color:#94a3b8;'>📖 Caderno de Produção do Turno</h3>", unsafe_allow_html=True)
    col_pag1, col_pag2 = st.columns(2)
    with col_pag1:
        with st.container(border=True):
            st.markdown("<h4 style='text-align: center; color: #cbd5e1;'>Próximos na Fila ⏳</h4><hr style='margin-top:0;'>", unsafe_allow_html=True)
            if len(fila_producao) > 1:
                for idx, lote in enumerate(fila_producao[1:]): 
                    st.markdown(f"**{idx+2}º** - {lote['Receita']} <span style='color:#38bdf8;'>({lote['Meta_Kg']*lote['Batidas']}kg)</span>", unsafe_allow_html=True)
                    st.divider()
            else:
                st.caption("Nenhum outro lote na fila.")
    with col_pag2:
        with st.container(border=True):
            st.markdown("<h4 style='text-align: center; color: #cbd5e1;'>Finalizados Recentemente ✅</h4><hr style='margin-top:0;'>", unsafe_allow_html=True)
            if hist_concluidos:
                for lote in hist_concluidos[:8]: 
                    st.markdown(f"✅ **{lote['Receita']}** <span style='color:#94a3b8;'>({lote['Meta']}kg)</span> 📦 {lote['Caixas']} cxs", unsafe_allow_html=True)
                    st.divider()

# ==========================================
# 🚀 5. MOTOR PRINCIPAL COM NAVEGAÇÃO LATERAL
# ==========================================
aplicar_css_premium()

if "autenticado" not in st.session_state:
    st.session_state.update({"autenticado": False, "usuario_logado": None, "perfil": None})

if not st.session_state["autenticado"]:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        with st.form("login_form", border=True):
            st.markdown("""
                <div style="text-align: center; margin-bottom: 20px;">
                    <h2 style="color: #38bdf8; margin: 0;">🏭 ERP MESTRE GIL</h2>
                    <p style="color: #94a3b8; font-size: 0.9rem; margin-top: 4px;">Controle Operacional & Inteligência Industrial</p>
                </div>
            """, unsafe_allow_html=True)
            login_input = st.text_input("Usuário:")
            senha_input = st.text_input("Senha Digital:", type="password")
            if st.form_submit_button("Entrar no Sistema", type="primary", use_container_width=True):
                usuario_validado = carregar_dados_tabela(f"SELECT nome, perfil FROM usuarios WHERE login='{login_input.lower().strip()}' AND senha='{senha_input}'")
                if usuario_validado:
                    st.session_state.update({
                        "autenticado": True, 
                        "usuario_logado": usuario_validado[0][0], 
                        "perfil": usuario_validado[0][1]
                    })
                    st.rerun()
                else:
                    st.error("❌ Credenciais inválidas.")
else:
    cor_badge = "#f59e0b" if st.session_state['perfil'] in ["Mestre", "Gerente"] else "#3b82f6"
    st.sidebar.markdown(f"""
        <div class="notranslate" translate="no" style="background: linear-gradient(180deg, #111827 0%, #1e293b 100%); padding: 16px; border-radius: 12px; border: 1px solid #334155; margin-bottom: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
            <div style="font-size: 1.15rem; font-weight: 800; color: #38bdf8; text-align: center; letter-spacing: 0.5px;">🏭 MESTRE GIL</div>
            <div style="font-size: 0.75rem; color: #94a3b8; text-align: center; margin-bottom: 12px;">SISTEMA INDUSTRIAL ERP</div>
            <div style="background: {cor_badge}; color: #0f172a; padding: 4px 8px; border-radius: 6px; text-align: center; font-weight: 800; font-size: 0.78rem; text-transform: uppercase;">
                NÍVEL: {st.session_state['perfil']}
            </div>
            <div style="text-align: center; margin-top: 10px; font-size: 0.95rem; font-weight: 600; color: #f8fafc;">
                👤 {st.session_state['usuario_logado']}
            </div>
        </div>
    """, unsafe_allow_html=True)

    matriz_receitas = carregar_receitas()
    estoque_atual = carregar_estoque()
    fila_raw = carregar_dados_tabela("SELECT id, receita, meta_kg, status, instrucao, batidas_total FROM fila_producao ORDER BY id ASC")
    fila = [{"ID": l[0], "Receita": l[1], "Meta_Kg": l[2], "Status": l[3], "Instrucao": l[4] if l[4] else "", "Batidas": l[5] if l[5] else 1} for l in fila_raw if l[1]]
    linhas_hist = carregar_dados_tabela("SELECT id, receita, meta_kg, caixas, peseiro, batedor, obs, data_hora FROM historico ORDER BY id DESC")
    hist_formatado = [{"ID": l[0], "Receita": l[1], "Meta": l[2], "Caixas": l[3], "Peseiro": l[4], "Batedor": l[5], "Obs": l[6], "Data": l[7]} for l in linhas_hist]

    opcoes_menu = ["🏭 Linha de Produção"]
    if st.session_state["perfil"] in ["Mestre", "Gerente"]:
        opcoes_menu.append("📋 Gestão da Fila")
    if st.session_state["perfil"] in ["Mestre", "Gerente", "Financeiro"]:
        opcoes_menu.append("📦 Controle de Estoque")
    if st.session_state["perfil"] in ["Mestre", "Gerente"]:
        opcoes_menu.append("📝 Montar Ficha Técnica")
        opcoes_menu.append("🖨️ Imprimir Ficha / POP")
        opcoes_menu.append("🧪 Motor Físico-Químico")
    if st.session_state["perfil"] in ["Mestre", "Financeiro"]:
        opcoes_menu.append("💰 Precificação (CMV)")
    if st.session_state["perfil"] in ["Mestre", "Gerente", "Financeiro"]:
        opcoes_menu.append("📊 Dashboards & BI")
    if st.session_state["perfil"] in ["Mestre", "Financeiro"]:
        opcoes_menu.append("🍎 Rotulagem Anvisa")
    if st.session_state["perfil"] in ["Mestre", "Gerente"]:
        opcoes_menu.append("👥 Gestão de RH")
    if st.session_state["perfil"] == "Mestre":
        opcoes_menu.append("🛠️ Painel Mestre / Configurações")

    menu_selecionado = st.sidebar.radio("Navegação do Sistema:", opcoes_menu)

    st.sidebar.divider()
    col_s1, col_s2 = st.sidebar.columns(2)
    with col_s1:
        if st.button("🔄 Sync", use_container_width=True): st.rerun()
    with col_s2:
        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.update({"autenticado": False, "usuario_logado": None, "perfil": None})
            st.rerun()

    if menu_selecionado == "🏭 Linha de Produção":
        painel_fabrica(matriz_receitas, fila, hist_formatado, st.session_state["usuario_logado"])

    elif menu_selecionado == "📋 Gestão da Fila":
        st.title("📋 Gestão da Fila de Produção")
        col1, col2 = st.columns([1.2, 1])
        with col1:
            st.subheader("⚙️ Enviar Ordem de Produção")
            if not matriz_receitas:
                st.warning("Cadastre receitas na Ficha Técnica primeiro.")
            else:
                with st.form("form_ordem", border=True):
                    lista_produtos = [f"[{v['sku']}] {k}" for k, v in matriz_receitas.items()]
                    selecao = st.selectbox("Selecione o Produto (SKU):", lista_produtos)
                    receita_escolhida = selecao.split("] ")[1] if "] " in selecao else selecao
                    
                    c_meta, c_batidas = st.columns(2)
                    with c_meta: meta_escolhida = st.number_input("Peso por Batida (kg):", min_value=1.0, value=150.0, step=1.0)
                    with c_batidas: batidas_qtd = st.number_input("Quantas Batidas?", min_value=1, value=1, step=1)
                    
                    instrucao_envase = st.text_input("Instruções de Envase (Opcional):", placeholder="Ex: 36 caixas de 4,1kg por batida")
                    if st.form_submit_button("🚀 Enviar para a Fábrica", type="primary"):
                        executar_query("INSERT INTO fila_producao (receita, meta_kg, status, instrucao, batidas_total) VALUES (?, ?, 'Pendente', ?, ?)", (receita_escolhida, meta_escolhida, instrucao_envase, batidas_qtd))
                        st.rerun()
        with col2:
            st.subheader("📋 Ordens Pendentes")
            if not fila:
                st.success("Tudo limpo! Nenhuma ordem pendente.")
            else:
                for idx, lote in enumerate(fila):
                    with st.container(border=True):
                        st.markdown(f"**#{idx + 1} | {lote['Receita']}**")
                        st.caption(f"🎯 {lote['Batidas']} Batidas de {lote['Meta_Kg']}kg (Total: {lote['Meta_Kg']*lote['Batidas']} kg)")
                        c_prio, c_canc = st.columns(2)
                        with c_prio:
                            if idx > 0 and st.button("⬆️ Priorizar", key=f"prio_{lote['ID']}", use_container_width=True):
                                fila.remove(lote)
                                fila.insert(0, lote)
                                executar_query("DELETE FROM fila_producao")
                                for l in fila: 
                                    executar_query("INSERT INTO fila_producao (receita, meta_kg, status, instrucao, batidas_total) VALUES (?, ?, ?, ?, ?)", (l["Receita"], l["Meta_Kg"], l["Status"], l["Instrucao"], l["Batidas"]))
                                st.rerun()
                        with c_canc:
                            st.markdown('<div class="btn-cancelar">', unsafe_allow_html=True)
                            if st.button("🗑️ Cancelar", key=f"canc_{lote['ID']}", use_container_width=True):
                                executar_query("DELETE FROM fila_producao WHERE id = ?", (lote['ID'],))
                                st.rerun()
                            st.markdown('</div>', unsafe_allow_html=True)

    elif menu_selecionado == "📦 Controle de Estoque":
        st.title("📦 Controle de Estoque e Insumos")
        c_lancamento, c_tabela = st.columns([1, 1.5])
        with c_lancamento:
            st.subheader("📥 Lançar Entrada (Compra)")
            ingredientes_unicos = set(ing for rec in matriz_receitas.values() for ing in rec["ingredientes"].keys())
            for ing in ingredientes_unicos:
                if ing not in estoque_atual: 
                    executar_query("INSERT INTO estoque (ingrediente, custo_kg, qtd_atual_kg) VALUES (?, 0.0, 0.0)", (ing,))
            
            with st.form("form_entrada", border=True):
                opcoes_ingredientes = sorted(list(estoque_atual.keys())) if estoque_atual else ["Nenhum cadastrado"]
                ing_selecionado = st.selectbox("Selecione o Insumo:", opcoes_ingredientes)
                qtd_comprada = st.number_input("Quantidade Comprada (Kg):", min_value=0.1, value=10.0, step=1.0)
                custo_atual_db = estoque_atual.get(ing_selecionado, {}).get("custo_kg", 0.0) if estoque_atual else 0.0
                novo_custo = st.number_input("Preço Pago (R$ por Kg):", min_value=0.0, value=float(custo_atual_db), step=0.5)
                
                if st.form_submit_button("➕ Registrar no Estoque", type="primary"):
                    if estoque_atual:
                        qtd_antiga = estoque_atual.get(ing_selecionado, {}).get("qtd_atual_kg", 0.0)
                        nova_qtd_total = qtd_antiga + qtd_comprada
                        executar_query("UPDATE estoque SET qtd_atual_kg = ?, custo_kg = ? WHERE ingrediente = ?", (nova_qtd_total, novo_custo, ing_selecionado))
                        st.success(f"Entrada registrada com sucesso!")
                        st.rerun()
        with c_tabela:
            st.subheader("📦 Posição Atual e Ajustes")
            df_estoque = pd.DataFrame([{"Insumo": k, "Custo (R$/Kg)": v["custo_kg"], "Estoque (Kg)": v["qtd_atual_kg"]} for k, v in carregar_estoque().items()])
            if not df_estoque.empty:
                df_editado = st.data_editor(df_estoque, hide_index=True, use_container_width=True)
                if st.button("💾 Salvar Ajuste Manual"):
                    for _, row in df_editado.iterrows(): 
                        executar_query("UPDATE estoque SET custo_kg = ?, qtd_atual_kg = ? WHERE ingrediente = ?", (float(row["Custo (R$/Kg)"]), float(row["Estoque (Kg)"]), row["Insumo"]))
                    st.success("Estoque ajustado!")
                    st.rerun()
            else:
                st.info("Estoque vazio.")

    elif menu_selecionado == "📝 Montar Ficha Técnica":
        st.title("📝 Montar Ficha Técnica & Formulação")
        
        if "receita_em_edicao" not in st.session_state:
            st.session_state["receita_em_edicao"] = None

        ed_rec = st.session_state["receita_em_edicao"]
        if ed_rec and ed_rec in matriz_receitas:
            dados_ed = matriz_receitas[ed_rec]
            v_sku = dados_ed["sku"]
            v_nome = ed_rec
            v_und = dados_ed["und_nome"]
            v_peso = dados_ed["und_peso"]
            v_modo = dados_ed["modo_preparo"]
            itens_lista = [{"Ingrediente": k, "Quantidade": float(v)} for k, v in dados_ed["ingredientes"].items()]
            while len(itens_lista) < 12:
                itens_lista.append({"Ingrediente": "", "Quantidade": 0.0})
            df_inicial = pd.DataFrame(itens_lista)
            st.info(f"✏️ **Modo de Edição Ativo:** Editando a receita **{ed_rec}**")
            if st.button("❌ Cancelar Edição"):
                st.session_state["receita_em_edicao"] = None
                st.rerun()
        else:
            v_sku = ""
            v_nome = ""
            v_und = "Caixa 5L"
            v_peso = 2.500
            v_modo = ""
            df_inicial = pd.DataFrame([{"Ingrediente": "", "Quantidade": 0.0} for _ in range(12)])

        with st.form("form_nova_receita", border=True):
            st.markdown("### ➕ Dados da Ficha Técnica")
            c1, c2 = st.columns([1, 3])
            with c1: sku = st.text_input("SKU (Ex: GELATO-01):", value=v_sku)
            with c2: nome = st.text_input("Nome Comercial da Fórmula:", value=v_nome)
            c3, c4 = st.columns(2)
            with c3: und_nome = st.text_input("Tipo Embalagem (Ex: Caixa 5L):", value=v_und)
            with c4: und_peso = st.number_input("Peso por Embalagem (kg):", value=float(v_peso), format="%.3f")
            modo_preparo = st.text_area("Procedimento Operacional Padrão (POP):", value=v_modo, placeholder="1. Adicionar líquidos no tanque...\n2. Incorporar pós...")
            
            st.markdown("**Composição de Ingredientes na Base:**")
            df_ing = st.data_editor(df_inicial, num_rows="dynamic", use_container_width=True)
            
            botao_label = "💾 Atualizar Ficha Técnica" if ed_rec else "💾 Salvar Ficha Técnica"
            if st.form_submit_button(botao_label, type="primary"):
                formula = {}
                for _, r in df_ing.iterrows():
                    ing_str = str(r["Ingrediente"]).strip() if pd.notna(r.get("Ingrediente")) else ""
                    qtd_raw = r.get("Quantidade")
                    try:
                        qtd_val = float(qtd_raw) if pd.notna(qtd_raw) and str(qtd_raw).strip() != "" else 0.0
                    except (ValueError, TypeError):
                        qtd_val = 0.0
                    
                    if ing_str != "" and qtd_val > 0:
                        formula[ing_str] = qtd_val

                if nome and und_nome and formula and sku:
                    if ed_rec and ed_rec != nome:
                        executar_query("DELETE FROM receitas WHERE nome = ?", (ed_rec,))
                    executar_query("INSERT OR REPLACE INTO receitas (nome, ingredientes, und_nome, und_peso, modo_preparo, sku) VALUES (?, ?, ?, ?, ?, ?)", (nome, json.dumps(formula), und_nome, und_peso, modo_preparo, sku.upper()))
                    st.session_state["receita_em_edicao"] = None
                    st.success("Ficha Técnica salva com sucesso!")
                    st.rerun()
                else: 
                    st.error("Preencha SKU, Nome e pelo menos um ingrediente com quantidade válida.")

        if matriz_receitas:
            st.markdown("---")
            st.subheader("📚 Fórmulas Cadastradas")
            for rec, dados in matriz_receitas.items():
                with st.expander(f"📖 [{dados['sku']}] {rec} ({dados['und_nome']})"):
                    st.json(dados["ingredientes"])
                    st.info(dados["modo_preparo"])
                    c_ed, c_ex = st.columns([1, 1])
                    with c_ed:
                        if st.button(f"✏️ Editar Fórmula", key=f"edit_{rec}"):
                            st.session_state["receita_em_edicao"] = rec
                            st.rerun()
                    with c_ex:
                        if st.button(f"🗑 Excluir Fórmula", key=f"del_{rec}"):
                            executar_query("DELETE FROM receitas WHERE nome = ?", (rec,))
                            if st.session_state.get("receita_em_edicao") == rec:
                                st.session_state["receita_em_edicao"] = None
                            st.rerun()

    elif menu_selecionado == "🖨️ Imprimir Ficha / POP":
        st.title("🖨️ Impressão de Ficha Técnica / Procedimento Padrão (POP)")
        if matriz_receitas:
            c_sel, c_peso = st.columns([2, 1])
            with c_sel:
                rec_sel = st.selectbox("Selecione a Fórmula para Impressão:", list(matriz_receitas.keys()))
            d = matriz_receitas[rec_sel]
            with c_peso:
                peso_lote_print = st.number_input("Peso Total da Batida (kg):", min_value=1.0, value=150.0, step=5.0)
            
            soma_p = sum(d["ingredientes"].values()) if sum(d["ingredientes"].values()) > 0 else 1
            linhas_html_tabela = ""
            for ing, q in d["ingredientes"].items():
                peso_calc = (q / soma_p) * peso_lote_print
                txt_p = f"{peso_calc*1000:.0f} g" if peso_calc < 1.0 else f"{peso_calc:.3f} kg"
                # Blindagem contra duplicidade por tradução automática: translate="no" e class="notranslate"
                linhas_html_tabela += f"<tr class='notranslate' translate='no'><td class='notranslate' translate='no' style='border: 1px solid black; padding: 8px;'><b>{ing}</b></td><td class='notranslate' translate='no' style='border: 1px solid black; padding: 8px; text-align: right;'><b>{txt_p}</b></td></tr>"
            
            st.components.v1.html("""
                <button onclick="window.print()" style="
                    background: #10b981;
                    color: white;
                    font-size: 16px;
                    font-weight: bold;
                    padding: 12px 24px;
                    border: none;
                    border-radius: 8px;
                    cursor: pointer;
                    width: 100%;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.2);
                ">
                    🖨️ ENVIAR DIRETO PARA A IMPRESSORA (IMPRIMIR AGORA)
                </button>
            """, height=65)

            st.markdown(f"""
                <div class="print-area notranslate" translate="no" style="background-color: white; color: black; padding: 25px; border-radius: 8px; border: 2px solid #000; margin-top: 15px;">
                    <div style="text-align: center; border-bottom: 3px solid black; padding-bottom: 10px; margin-bottom: 15px;">
                        <h2 style="margin: 0; color: black; text-transform: uppercase;">ORDEM DE PRODUÇÃO / FICHA TÉCNICA</h2>
                        <h1 style="margin: 5px 0; color: black;">[{d['sku']}] {rec_sel}</h1>
                        <p style="margin: 0; font-size: 14px; color: black;">Data/Hora de Emissão: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 16px; margin-bottom: 15px; color: black;">
                        <span><b>Lote Programado:</b> {peso_lote_print:.1f} kg</span>
                        <span><b>Embalagem Padrão:</b> {d['und_nome']} ({d['und_peso']} kg)</span>
                        <span><b>Rendimento Estimado:</b> ~{int(peso_lote_print / d['und_peso'])} unidades</span>
                    </div>
                    <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px; color: black;">
                        <thead>
                            <tr style="background-color: #e2e8f0; color: black;">
                                <th style="border: 1px solid black; padding: 8px; text-align: left;">Insumo / Ingrediente</th>
                                <th style="border: 1px solid black; padding: 8px; text-align: right;">Peso Calculado</th>
                            </tr>
                        </thead>
                        <tbody>
                            {linhas_html_tabela}
                        </tbody>
                    </table>
                    <div style="border: 1px solid black; padding: 12px; border-radius: 4px; margin-bottom: 25px; color: black;">
                        <h3 style="margin-top: 0; color: black;">Procedimento Operacional Padrão (POP):</h3>
                        <p style="white-space: pre-line; margin-bottom: 0; color: black;">{d['modo_preparo']}</p>
                    </div>
                    <div style="display: flex; justify-content: space-around; margin-top: 40px; padding-top: 20px; border-top: 1px dashed black; color: black;">
                        <div style="text-align: center;">__________________________________<br><b>Assinatura do Peseiro</b></div>
                        <div style="text-align: center;">__________________________________<br><b>Assinatura do Batedor</b></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Cadastre fórmulas primeiro.")

    elif menu_selecionado == "🧪 Motor Físico-Químico":
        st.title("🧪 Motor de Balanceamento Físico-Químico")
        st.markdown("Balanceamento industrial de sólidos e açúcares para caldas de gelados.")
        
        c1, c2, c3, c4 = st.columns(4)
        with c1: gordura = st.number_input("% Gordura Desejada:", value=8.0, step=0.5)
        with c2: sng = st.number_input("% Sólidos Não Gordurosos (SNG):", value=10.0, step=0.5)
        with c3: acucar = st.number_input("% Açúcares Totais (POD):", value=16.0, step=0.5)
        with c4: est = st.number_input("% Estabilizantes/Neutros:", value=0.5, step=0.1)
        
        solidos_totais = gordura + sng + acucar + est
        agua = 100.0 - solidos_totais
        
        st.markdown("---")
        st.subheader("📊 Diagnóstico da Calda:")
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Sólidos Totais", f"{solidos_totais:.1f}%")
        col_m2.metric("Água Livre", f"{agua:.1f}%")
        col_m3.metric("PAC Estimado", f"{acucar * 1.0:.1f}")
        
        if solidos_totais < 32:
            st.warning("⚠️ Calda com baixo teor de sólidos. Risco de formação de cristais de gelo.")
        elif solidos_totais > 42:
            st.warning("⚠️ Calda muito pesada em sólidos. Textura pode ficar arenosa.")
        else:
            st.success("✅ Calda com proporção de sólidos ideal para gelados industriais.")

    elif menu_selecionado == "💰 Precificação (CMV)":
        st.title("💰 Precificação de Produtos & Lucro Real (CMV)")
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
        else:
            st.info("Cadastre receitas primeiro.")

    elif menu_selecionado == "📊 Dashboards & BI":
        st.title("📊 Relatório de Fechamento Industrial & BI")
        df_hist = pd.read_sql_query("SELECT receita as 'Produto', meta_kg as 'Kg Produzido', caixas as 'Unid. Envasadas', batedor as 'Operador', data_hora as 'Data' FROM historico ORDER BY data_hora DESC", sqlite3.connect(DB_NAME))
        if not df_hist.empty:
            df_hist['Data_Formatada'] = pd.to_datetime(df_hist['Data']).dt.date
            filtro_data = st.radio("Selecione o Período:", ["Hoje", "Últimos 7 Dias", "Este Mês", "Todo o Histórico"], horizontal=True)
            hoje = datetime.now().date()
            
            if filtro_data == "Hoje": df_filtrado = df_hist[df_hist['Data_Formatada'] == hoje]
            elif filtro_data == "Últimos 7 Dias": df_filtrado = df_hist[df_hist['Data_Formatada'] >= (hoje - timedelta(days=7))]
            elif filtro_data == "Este Mês": df_filtrado = df_hist[df_hist['Data_Formatada'] >= hoje.replace(day=1)]
            else: df_filtrado = df_hist

            with st.container(border=True):
                c1, c2, c3 = st.columns(3)
                c1.metric("Volume Produzido (Kg)", f"{df_filtrado['Kg Produzido'].sum():.1f} kg")
                c2.metric("Total Envasado (Unidades)", int(df_filtrado['Unid. Envasadas'].sum()))
                c3.metric("Lotes Finalizados", len(df_filtrado))
            
            st.dataframe(df_filtrado.drop(columns=['Data_Formatada']), use_container_width=True)
        else:
            st.info("Nenhuma produção registrada ainda.")

    elif menu_selecionado == "🍎 Rotulagem Anvisa":
        st.title("🍎 Rotulagem Nutricional Oficial (Anvisa)")
        if matriz_receitas:
            rec_selec = st.selectbox("Selecione o Produto:", list(matriz_receitas.keys()))
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
            if st.button("💾 Gerar Tabela Anvisa", type="primary"):
                val = df_ed["Valor/100g"].tolist()
                j = json.dumps({"porcao_g": porcao, "medida_caseira": caseira, "energia": val[0], "carbo": val[1], "acucar_tot":0, "acucar_add": val[2], "prot": val[3], "gord_tot": val[4], "gord_sat":0, "gord_trans":0, "fibra":0, "sodio": val[5]})
                executar_query("INSERT OR REPLACE INTO tabela_nutricional (receita, dados_json) VALUES (?, ?)", (rec_selec, j))
                st.success("Tabela salva com sucesso.")
                st.rerun()
            if d_salvos:
                st.markdown("<br><div style='background-color: white; padding: 20px; border-radius: 8px;'><table class='anvisa-table'><tr><td colspan='2' class='anvisa-header'>INFORMAÇÃO NUTRICIONAL</td></tr></table></div>", unsafe_allow_html=True)
        else:
            st.info("Cadastre receitas primeiro.")

    elif menu_selecionado == "👥 Gestão de RH":
        st.title("👥 Gestão de Usuários & Equipe")
        with st.form("form_rh", border=True):
            c1, c2, c3, c4 = st.columns(4)
            with c1: n_nome = st.text_input("Nome:")
            with c2: n_login = st.text_input("Login:")
            with c3: n_senha = st.text_input("Senha:", type="password")
            with c4: n_perfil = st.selectbox("Perfil:", ["Operador", "Financeiro", "Gerente", "Mestre"])
            if st.form_submit_button("➕ Cadastrar Colaborador", type="primary"):
                if n_nome and n_login and n_senha:
                    executar_query("INSERT INTO usuarios (login, nome, senha, perfil) VALUES (?, ?, ?, ?)", (n_login.lower().strip(), n_nome, n_senha, n_perfil))
                    st.success("Usuário Cadastrado com sucesso!")
                    st.rerun()
        st.dataframe(pd.DataFrame([{"Login": u[0], "Nome": u[1], "Perfil": u[2]} for u in carregar_dados_tabela("SELECT login, nome, perfil FROM usuarios")]), use_container_width=True)

    elif menu_selecionado == "🛠️ Painel Mestre / Configurações":
        st.title("🛠️ Painel Mestre - Controle & Manutenção Geral")
        st.caption("Acesso irrestrito a todas as tabelas, banco de dados, backups e ações de limpeza.")

        t_cfg1, t_cfg2, t_cfg3, t_cfg4 = st.tabs([
            "🧹 Manutenção Rápida", 
            "🗃 Editor de Banco de Dados", 
            "💾 Backup / Download", 
            "💻 Console SQL"
        ])

        with t_cfg1:
            st.subheader("Ações de Limpeza Operacional")
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                with st.container(border=True):
                    st.markdown("#### 🗑️ Limpar Fila de Produção")
                    st.write("Remove todas as ordens pendentes da fila da fábrica.")
                    if st.button("Executar Limpeza da Fila", type="primary"):
                        executar_query("DELETE FROM fila_producao")
                        st.success("Fila de produção esvaziada!")
                        st.rerun()
            with col_b2:
                with st.container(border=True):
                    st.markdown("#### 📜 Resetar Histórico de Produção")
                    st.write("Apaga todos os registros de lotes já finalizados.")
                    senha_confirm = st.text_input("Digite sua senha para confirmar o reset:", type="password", key="pwd_reset_hist")
                    if st.button("Resetar Histórico", key="btn_reset_hist"):
                        if senha_confirm == "mestre123":
                            executar_query("DELETE FROM historico")
                            st.success("Histórico de produção zerado!")
                            st.rerun()
                        else:
                            st.error("Senha incorreta.")

        with t_cfg2:
            st.subheader("Visualizar e Modificar Dados das Tabelas")
            tabela_escolhida = st.selectbox("Selecione a Tabela do Sistema:", ["receitas", "estoque", "fila_producao", "historico", "usuarios", "tabela_nutricional"])
            dados_tabela = pd.read_sql_query(f"SELECT * FROM {tabela_escolhida}", sqlite3.connect(DB_NAME))
            
            st.write(f"Total de registros em `{tabela_escolhida}`: **{len(dados_tabela)}**")
            df_edit_direto = st.data_editor(dados_tabela, num_rows="dynamic", use_container_width=True, key=f"editor_raw_{tabela_escolhida}")
            
            if st.button(f"💾 Gravar Alterações em {tabela_escolhida}"):
                conn = sqlite3.connect(DB_NAME)
                df_edit_direto.to_sql(tabela_escolhida, conn, if_exists="replace", index=False)
                conn.close()
                st.success(f"Tabela {tabela_escolhida} salva com sucesso!")
                st.rerun()

        with t_cfg3:
            st.subheader("Exportação Completa de Dados")
            st.write("Baixe o backup completo das suas fórmulas e estoque em formato JSON para restaurar ou guardar com segurança.")
            
            backup_dict = {
                "receitas": carregar_receitas(),
                "estoque": carregar_estoque(),
                "data_backup": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            json_str = json.dumps(backup_dict, indent=2, ensure_ascii=False)
            
            st.download_button(
                label="📥 Baixar Arquivo de Backup Completo (JSON)",
                data=json_str,
                file_name=f"backup_mestre_gil_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                mime="application/json"
            )

        with t_cfg4:
            st.subheader("Execução Direta de Comandos SQL")
            st.warning("⚠️ Atenção: Comandos SQL afetam o banco de dados diretamente.")
            query_sql = st.text_area("Instrução SQL:", placeholder="Ex: UPDATE estoque SET custo_kg = 15.0 WHERE ingrediente = 'Leite em Pó'")
            if st.button("Executar Comando SQL"):
                if query_sql.strip():
                    try:
                        executar_query(query_sql)
                        st.success("Comando executado com sucesso no banco de dados!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro na execução do SQL: {e}")
