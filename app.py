import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import base64
from pathlib import Path

# ── CONFIG ────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="De olho no custo | G3",
    page_icon="🟡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CORES G3 ─────────────────────────────────────────────────────────────────
G3Y  = "#F5C200"
G3BK = "#111111"
G3DK = "#1A1A1A"
G3GY = "#2A2A2A"

# ── CSS GLOBAL ────────────────────────────────────────────────────────────────
def load_css():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
    }}

    /* Fundo geral */
    .stApp {{ background: #F0F0F0; }}

    /* Sidebar */
    [data-testid="stSidebar"] {{
        background: {G3BK} !important;
        border-right: 3px solid {G3Y};
    }}
    [data-testid="stSidebar"] * {{ color: #eee !important; }}
    [data-testid="stSidebar"] .stRadio label {{
        color: #ccc !important;
        font-size: 14px;
        padding: 6px 0;
    }}
    [data-testid="stSidebar"] .stRadio label:hover {{ color: {G3Y} !important; }}
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{
        color: {G3Y} !important;
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: .1em;
        font-weight: 700;
    }}

    /* Topbar / Header */
    header[data-testid="stHeader"] {{
        background: {G3BK};
        border-bottom: 3px solid {G3Y};
    }}

    /* Métricas */
    [data-testid="metric-container"] {{
        background: {G3BK};
        border-radius: 10px;
        padding: 16px 20px;
        border-top: 3px solid {G3Y};
        color: white !important;
    }}
    [data-testid="metric-container"] label {{
        color: #aaa !important;
        font-size: 11px !important;
        text-transform: uppercase;
        letter-spacing: .06em;
    }}
    [data-testid="metric-container"] [data-testid="stMetricValue"] {{
        color: white !important;
        font-size: 26px !important;
        font-weight: 800 !important;
    }}

    /* Cards / expanders */
    .stExpander {{ border: 1px solid #ddd; border-radius: 10px; }}

    /* Tabelas */
    .stDataFrame {{ border-radius: 8px; overflow: hidden; }}
    thead tr th {{
        background: {G3BK} !important;
        color: {G3Y} !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        font-size: 11px;
    }}

    /* Botões */
    .stButton > button {{
        background: {G3Y};
        color: {G3BK};
        font-weight: 700;
        border: none;
        border-radius: 7px;
        padding: 8px 20px;
    }}
    .stButton > button:hover {{
        background: #e6b800;
        color: {G3BK};
    }}

    /* Inputs */
    .stTextInput input, .stSelectbox select, .stNumberInput input {{
        border: 1.5px solid #ddd;
        border-radius: 7px;
    }}
    .stTextInput input:focus {{
        border-color: {G3Y} !important;
        box-shadow: 0 0 0 2px rgba(245,194,0,0.15);
    }}

    /* Divisor amarelo */
    hr {{ border-color: {G3Y}; opacity: .3; }}

    /* Títulos de seção */
    .section-title {{
        font-size: 15px;
        font-weight: 700;
        color: {G3BK};
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 12px;
    }}
    .section-bar {{
        width: 4px; height: 20px;
        background: {G3Y};
        border-radius: 999px;
        display: inline-block;
    }}

    /* Badge de criticidade */
    .badge-a {{ background:#fee2e2; color:#c00; padding:2px 8px; border-radius:999px; font-size:11px; font-weight:700; }}
    .badge-b {{ background:#fef9c3; color:#854d0e; padding:2px 8px; border-radius:999px; font-size:11px; font-weight:700; }}
    .badge-c {{ background:#dbeafe; color:#1e40af; padding:2px 8px; border-radius:999px; font-size:11px; font-weight:700; }}

    /* Upload */
    [data-testid="stFileUploader"] {{
        border: 2px dashed {G3Y};
        border-radius: 10px;
        padding: 10px;
        background: #FFFBE6;
    }}

    /* Tabs */
    .stTabs [data-baseweb="tab"] {{
        font-weight: 600;
        color: #666;
    }}
    .stTabs [aria-selected="true"] {{
        color: {G3Y} !important;
        border-bottom-color: {G3Y} !important;
    }}
    </style>
    """, unsafe_allow_html=True)

load_css()

# ── HELPERS ───────────────────────────────────────────────────────────────────
def img_b64(path: str, ext="jpeg") -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def brl(v):
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def brl_mi(v):
    return f"R$ {v/1e6:,.2f}M".replace(",", "X").replace(".", ",").replace("X", ".")

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", size=11, color="#333"),
    margin=dict(l=10, r=10, t=30, b=10),
    legend=dict(font=dict(size=11)),
)

G3_COLORS = [G3Y, "#60a5fa", "#34d399", "#f87171", "#a78bfa", "#fb923c", "#38bdf8", "#e6b800"]

# ── CARGA DE DADOS ────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_excel(path):
    xl = pd.ExcelFile(path)
    sheets = {}

    # Unidades
    df = xl.parse("Unidades", dtype=str)
    df.columns = ["id","nome","responsavel","localizacao"]
    df = df.dropna(subset=["nome"])
    sheets["unidades"] = df

    # Mapeamento ID → Nome
    id_map = {}
    for _, r in df.iterrows():
        id_num = str(r["id"]).lstrip("0") or "0"
        id_map[id_num] = r["nome"]

    # Mão de Obra — únicos por função
    df_mo = xl.parse("mão de obra")
    df_mo.columns = ["funcao","custo_hora"]
    df_mo = df_mo.dropna(subset=["funcao"])
    df_mo["custo_hora"] = pd.to_numeric(df_mo["custo_hora"], errors="coerce").fillna(0)
    df_mo = df_mo.drop_duplicates(subset=["funcao"])
    sheets["mo"] = df_mo

    # Materiais
    df_mat = xl.parse("MATERIAIS", usecols=[0,1,2,3,4,5,6])
    df_mat.columns = ["unidade_id","fornecedor","codigo","descricao","quantidade","custo_unit","centro_custo"]
    df_mat = df_mat.dropna(subset=["descricao"])
    df_mat["quantidade"] = pd.to_numeric(df_mat["quantidade"], errors="coerce").fillna(0)
    df_mat["custo_unit"] = (
        df_mat["custo_unit"].astype(str)
        .str.replace("R$","",regex=False)
        .str.replace("\.","",regex=True)
        .str.replace(",",".",regex=False)
        .str.strip()
    )
    df_mat["custo_unit"] = pd.to_numeric(df_mat["custo_unit"], errors="coerce").fillna(0)
    df_mat["total"] = df_mat["quantidade"] * df_mat["custo_unit"]
    df_mat["unidade_id"] = df_mat["unidade_id"].apply(
        lambda x: str(int(float(x))) if pd.notna(x) and str(x).strip() != "" else ""
    )
    df_mat["unidade"] = df_mat["unidade_id"].map(id_map).fillna(df_mat["unidade_id"])
    df_mat["centro_custo"] = df_mat["centro_custo"].astype(str).str.strip().str.replace(r"\.0$","",regex=True)
    df_mat["fornecedor"]   = df_mat["fornecedor"].fillna("").astype(str).str.strip()
    df_mat["codigo"]       = df_mat["codigo"].fillna("").astype(str).str.strip()
    sheets["mat"] = df_mat

    # Equipamentos
    df_eq = xl.parse("Equipamentos", dtype=str)
    df_eq.columns = ["tag","descricao","marca","modelo","criticidade","unidade"]
    df_eq = df_eq.fillna("")
    df_eq["criticidade"] = df_eq["criticidade"].str.upper().str.strip()
    sheets["eq"] = df_eq

    return sheets

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    # Banner com caminhão + logo
    truck_b64 = img_b64("/home/claude/g3app/truck.png", "png")
    logo_b64  = img_b64("/home/claude/g3app/logo.jpg",  "jpeg")
    st.markdown(f"""
    <div style="position:relative;height:110px;overflow:hidden;border-radius:8px;margin-bottom:4px;">
      <img src="data:image/png;base64,{truck_b64}"
           style="width:100%;height:100%;object-fit:cover;object-position:center 40%;opacity:.55;">
      <div style="position:absolute;inset:0;background:linear-gradient(to bottom,rgba(0,0,0,.1),rgba(0,0,0,.7));
                  display:flex;align-items:flex-end;justify-content:space-between;padding:10px 12px;">
        <img src="data:image/jpeg;base64,{logo_b64}"
             style="height:38px;object-fit:contain;filter:drop-shadow(0 2px 4px rgba(0,0,0,.5));">
        <div style="text-align:right;line-height:1.3;">
          <div style="font-weight:800;color:#fff;font-size:12px;">De olho no custo</div>
          <div style="color:{G3Y};font-size:10px;">Manutenção &amp; orçamento</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("**NAVEGAÇÃO**")
    page = st.radio(
        "",
        ["📊 Dashboard", "🏢 Unidades", "👷 Mão de Obra", "📦 Materiais", "🚛 Equipamentos"],
        label_visibility="collapsed",
    )
    st.markdown("---")

    # Upload de nova planilha
    st.markdown("**IMPORTAR PLANILHA**")
    uploaded = st.file_uploader("", type=["xlsx","xls"], label_visibility="collapsed")
    data_path = "/home/claude/g3app/orcamento.xlsx"
    if uploaded:
        data_path = "/tmp/uploaded.xlsx"
        with open(data_path, "wb") as f:
            f.write(uploaded.read())
        st.cache_data.clear()
        st.success("✅ Planilha importada!")

    st.markdown("---")
    st.markdown(f"""
    <div style="color:#aaa;font-size:11px;text-align:center;">
      G3 Gestão · v4.0<br>
      <span style="color:{G3Y};">●</span> Sistema ativo
    </div>
    """, unsafe_allow_html=True)

# ── CARREGAR DADOS ────────────────────────────────────────────────────────────
with st.spinner("Carregando dados..."):
    sheets = load_excel(data_path)

df_unid = sheets["unidades"]
df_mo   = sheets["mo"]
df_mat  = sheets["mat"]
df_eq   = sheets["eq"]

# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA: DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if page == "📊 Dashboard":

    # Hero banner
    st.markdown(f"""
    <div style="position:relative;height:140px;overflow:hidden;border-radius:12px;margin-bottom:20px;
                box-shadow:0 4px 20px rgba(0,0,0,.18);">
      <img src="data:image/png;base64,{truck_b64}"
           style="width:100%;height:100%;object-fit:cover;object-position:center 55%;">
      <div style="position:absolute;inset:0;
                  background:linear-gradient(90deg,rgba(0,0,0,.8) 0%,rgba(0,0,0,.2) 100%);
                  display:flex;align-items:center;padding:28px;">
        <div>
          <div style="color:{G3Y};font-size:10px;font-weight:700;letter-spacing:.12em;
                      text-transform:uppercase;margin-bottom:4px;">G3 Gestão de Manutenção</div>
          <div style="color:#fff;font-size:24px;font-weight:800;line-height:1.2;">De olho no custo</div>
          <div style="color:#ccc;font-size:13px;margin-top:4px;">Controle de orçamento e recursos operacionais</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── KPIs ──────────────────────────────────────────────────────────────────
    total_custo = df_mat["total"].sum()
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("🏢 Unidades",     len(df_unid))
    k2.metric("👷 Mão de Obra",  len(df_mo))
    k3.metric("📦 Materiais",    f"{len(df_mat):,}".replace(",","."))
    k4.metric("🚛 Equipamentos", len(df_eq))
    k5.metric("💰 Custo Total",  f"R$ {total_custo/1e6:,.1f}M".replace(",","X").replace(".",",").replace("X","."))

    st.markdown("<br>", unsafe_allow_html=True)

    # ── LINHA 1: Custo por Unidade + Criticidade ──────────────────────────────
    c1, c2 = st.columns([2, 1])

    with c1:
        st.markdown('<div class="section-title"><span class="section-bar"></span>💰 Custo de Materiais por Unidade</div>', unsafe_allow_html=True)
        unids_ok = df_unid["nome"].tolist()
        cu = df_mat[df_mat["unidade"].isin(unids_ok)].groupby("unidade")["total"].sum().reset_index()
        cu.columns = ["Unidade","Total"]
        cu = cu.sort_values("Total", ascending=True)
        cu["Label"] = cu["Total"].apply(lambda v: f"R$ {v/1e6:.1f}M")
        fig = px.bar(cu, x="Total", y="Unidade", orientation="h", text="Label",
                     color="Unidade", color_discrete_sequence=G3_COLORS)
        fig.update_traces(textposition="outside", textfont=dict(size=12, color="#111", family="Inter"))
        fig.update_layout(**PLOTLY_LAYOUT, showlegend=False,
                          xaxis=dict(tickformat=".1fM", title="", showgrid=True, gridcolor="#eee"),
                          yaxis=dict(title=""), height=200)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown('<div class="section-title"><span class="section-bar"></span>⚠️ Criticidade dos Equipamentos</div>', unsafe_allow_html=True)
        crit_map = {"A":"Alta","B":"Média","C":"Baixa"}
        eq_c = df_eq[df_eq["criticidade"].isin(["A","B","C"])].copy()
        eq_c["Criticidade"] = eq_c["criticidade"].map(crit_map)
        cr = eq_c["Criticidade"].value_counts().reset_index()
        cr.columns = ["Criticidade","Qtd"]
        cr["ordem"] = cr["Criticidade"].map({"Alta":0,"Média":1,"Baixa":2})
        cr = cr.sort_values("ordem")
        fig2 = px.pie(cr, names="Criticidade", values="Qtd",
                      color="Criticidade",
                      color_discrete_map={"Alta":"#ef4444","Média":G3Y,"Baixa":"#60a5fa"},
                      hole=0.55)
        fig2.update_traces(textinfo="label+value+percent",
                           textfont=dict(size=12, family="Inter"),
                           pull=[0.03,0.03,0.03])
        fig2.update_layout(**PLOTLY_LAYOUT, height=200,
                           legend=dict(orientation="h", y=-0.15))
        st.plotly_chart(fig2, use_container_width=True)

    # ── LINHA 2: Tipos de Equipamento + Frota por Unidade ─────────────────────
    c3, c4 = st.columns([1,1])

    with c3:
        st.markdown('<div class="section-title"><span class="section-bar"></span>🚛 Equipamentos por Tipo</div>', unsafe_allow_html=True)
        def tipo_eq(desc):
            d = str(desc).upper()
            for t,l in [("CAMINHÃO","Caminhão"),("ESCAVADEIRA","Escavadeira"),
                        ("VEÍCULO","Veículo"),("TRATOR DE ESTEIRA","Trator Esteira"),
                        ("TRATOR DE RODAS","Trator Rodas"),("PERFURATRIZ","Perfuratriz"),
                        ("PÁ CARREGADEIRA","Pá Carregadeira"),("MOTONIVELADORA","Motoniveladora"),
                        ("TORRE DE ILUMINAÇÃO","Torre Iluminação"),("EMPILHADEIRA","Empilhadeira"),
                        ("PLATAFORMA","Plataforma"),("PRANCHA","Prancha")]:
                if t in d: return l
            return "Outros"
        df_eq["tipo"] = df_eq["descricao"].apply(tipo_eq)
        tipos = df_eq["tipo"].value_counts().reset_index()
        tipos.columns = ["Tipo","Qtd"]
        tipos = tipos.head(8)
        fig3 = px.bar(tipos, x="Tipo", y="Qtd", text="Qtd",
                      color="Tipo", color_discrete_sequence=G3_COLORS)
        fig3.update_traces(textposition="outside", textfont=dict(size=12, color="#111"))
        fig3.update_layout(**PLOTLY_LAYOUT, showlegend=False, height=220,
                           xaxis=dict(title="", tickangle=-25),
                           yaxis=dict(title="Qtd", showgrid=True, gridcolor="#eee"))
        st.plotly_chart(fig3, use_container_width=True)

    with c4:
        st.markdown('<div class="section-title"><span class="section-bar"></span>🏢 Frota por Unidade</div>', unsafe_allow_html=True)
        eq_u = df_eq[df_eq["unidade"] != ""].copy()
        eu = eq_u["unidade"].value_counts().reset_index()
        eu.columns = ["Unidade","Qtd"]
        fig4 = px.pie(eu, names="Unidade", values="Qtd",
                      color_discrete_sequence=G3_COLORS)
        fig4.update_traces(textinfo="label+value+percent",
                           textfont=dict(size=12, family="Inter"),
                           pull=[0.03]*len(eu))
        fig4.update_layout(**PLOTLY_LAYOUT, height=220,
                           legend=dict(orientation="h", y=-0.15))
        st.plotly_chart(fig4, use_container_width=True)

    # ── LINHA 3: Top Fornecedores + Mão de Obra ───────────────────────────────
    c5, c6 = st.columns([2,1])

    with c5:
        st.markdown('<div class="section-title"><span class="section-bar"></span>🏭 Top Fornecedores por Custo Total</div>', unsafe_allow_html=True)
        # Nomes curtos
        forn_short = {
            "XCMG BRASIL INDUSTRIA LTDA":"XCMG Brasil",
            "INDUSTRIA, COMERCIO E DISTRIBUIDORA JDF DE PECAS L":"JDF Peças",
            "SANDVIK MINING AND ROCK TECHNOLOGY DO BRASIL LTDA":"Sandvik Mining",
            "ITR SOUTH AMERICA COMERCIO IMPORTACAO E EXPORTACAO":"ITR South America",
            "SANTA LUZIA COMERCIAL LTDA":"Santa Luzia",
            "PETRONAS LUBRIFICANTES BRASIL S.A":"Petronas",
            "MASON EQUIPAMENTOS LTDA.":"Mason Equipamentos",
            "BR TRACTOR LOCACAO DE MAQUINAS PECAS E SERVICOS LT":"BR Tractor",
            "INOVA MAQUINAS LTDA":"Inova Máquinas",
            "MINASMAQUINAS JF LTDA":"MinasMáquinas JF",
        }
        top_f = df_mat.groupby("fornecedor")["total"].sum().reset_index()
        top_f.columns = ["Fornecedor","Total"]
        top_f["Fornecedor"] = top_f["Fornecedor"].map(lambda x: forn_short.get(x, x[:25]))
        top_f = top_f.sort_values("Total", ascending=False).head(8)
        top_f = top_f.sort_values("Total", ascending=True)
        top_f["Label"] = top_f["Total"].apply(lambda v: f"R$ {v/1e6:.1f}M")
        fig5 = px.bar(top_f, x="Total", y="Fornecedor", orientation="h", text="Label",
                      color="Fornecedor", color_discrete_sequence=G3_COLORS)
        fig5.update_traces(textposition="outside", textfont=dict(size=12, color="#111"))
        fig5.update_layout(**PLOTLY_LAYOUT, showlegend=False, height=250,
                           xaxis=dict(title="", showgrid=True, gridcolor="#eee"),
                           yaxis=dict(title=""))
        st.plotly_chart(fig5, use_container_width=True)

    with c6:
        st.markdown('<div class="section-title"><span class="section-bar"></span>👷 Mão de Obra — R$/hora</div>', unsafe_allow_html=True)
        mo_top = df_mo.sort_values("custo_hora", ascending=True).tail(10).copy()
        mo_top["funcao_curta"] = mo_top["funcao"].str[:22]
        mo_top["Label"] = mo_top["custo_hora"].apply(lambda v: f"R$ {v:.2f}")
        fig6 = px.bar(mo_top, x="custo_hora", y="funcao_curta", orientation="h",
                      text="Label", color_discrete_sequence=[G3Y])
        fig6.update_traces(textposition="outside", textfont=dict(size=11, color="#111"))
        fig6.update_layout(**PLOTLY_LAYOUT, showlegend=False, height=250,
                           xaxis=dict(title="R$/h", showgrid=True, gridcolor="#eee"),
                           yaxis=dict(title=""))
        st.plotly_chart(fig6, use_container_width=True)

    # ── LINHA 4: Custo por Centro de Custo + Importar ─────────────────────────
    c7, c8 = st.columns([2, 1])

    with c7:
        st.markdown('<div class="section-title"><span class="section-bar"></span>📁 Custo por Centro de Custo</div>', unsafe_allow_html=True)
        cc_valid = df_mat[df_mat["centro_custo"].isin(["1","2","3","4","5","6","7","8","9","10"])]
        cc = cc_valid.groupby("centro_custo")["total"].sum().reset_index()
        cc.columns = ["Centro","Total"]
        cc = cc.sort_values("Total", ascending=False)
        cc["Label"] = cc["Total"].apply(lambda v: f"R$ {v/1e6:.1f}M")
        fig7 = px.bar(cc, x="Centro", y="Total", text="Label",
                      color="Centro", color_discrete_sequence=G3_COLORS)
        fig7.update_traces(textposition="outside", textfont=dict(size=12, color="#111"))
        fig7.update_layout(**PLOTLY_LAYOUT, showlegend=False, height=200,
                           xaxis=dict(title="Centro de Custo"),
                           yaxis=dict(title="", showgrid=True, gridcolor="#eee"))
        st.plotly_chart(fig7, use_container_width=True)

    with c8:
        st.markdown('<div class="section-title"><span class="section-bar"></span>📊 Ciclo de Manutenção</div>', unsafe_allow_html=True)
        diag_b64 = img_b64("/home/claude/g3app/diagrama.jpg","jpeg")
        st.markdown(f"""
        <div style="background:{G3BK};border-radius:10px;padding:12px;text-align:center;">
          <img src="data:image/jpeg;base64,{diag_b64}"
               style="width:100%;border-radius:8px;max-height:160px;object-fit:contain;">
          <div style="color:{G3Y};font-size:10px;font-weight:700;text-transform:uppercase;
                      letter-spacing:.08em;margin-top:8px;">Engenharia · Planejamento · Execução · Controle</div>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA: UNIDADES
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🏢 Unidades":
    st.markdown('<div class="section-title"><span class="section-bar"></span>🏢 Unidades Operacionais</div>', unsafe_allow_html=True)

    col_info, col_table = st.columns([1, 3])

    with col_info:
        for _, r in df_unid.iterrows():
            st.markdown(f"""
            <div style="background:{G3BK};border-radius:10px;padding:14px;margin-bottom:10px;
                        border-left:4px solid {G3Y};">
              <div style="color:{G3Y};font-size:11px;font-weight:700;">{r['id']}</div>
              <div style="color:#fff;font-size:14px;font-weight:700;margin-top:2px;">{r['nome']}</div>
              <div style="color:#aaa;font-size:11px;margin-top:4px;">👤 {r['responsavel']}</div>
              <div style="color:#aaa;font-size:11px;">📍 {r['localizacao']}</div>
            </div>
            """, unsafe_allow_html=True)

    with col_table:
        st.dataframe(
            df_unid.rename(columns={"id":"ID","nome":"Nome","responsavel":"Responsável","localizacao":"Localização"}),
            use_container_width=True, hide_index=True, height=300,
        )

        # Métricas por unidade
        st.markdown("**Resumo por Unidade**")
        cols = st.columns(len(df_unid))
        for i, (_, r) in enumerate(df_unid.iterrows()):
            n_mat = len(df_mat[df_mat["unidade"] == r["nome"]])
            n_eq  = len(df_eq[df_eq["unidade"].str.upper() == r["nome"].upper()])
            custo = df_mat[df_mat["unidade"] == r["nome"]]["total"].sum()
            with cols[i]:
                st.markdown(f"""
                <div style="background:{G3BK};border-radius:8px;padding:12px;text-align:center;border-top:3px solid {G3Y};">
                  <div style="color:{G3Y};font-size:12px;font-weight:700;">{r['nome']}</div>
                  <div style="color:#fff;font-size:18px;font-weight:800;">R$ {custo/1e6:.1f}M</div>
                  <div style="color:#aaa;font-size:10px;">{n_mat:,} itens · {n_eq} equip.</div>
                </div>
                """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA: MÃO DE OBRA
# ══════════════════════════════════════════════════════════════════════════════
elif page == "👷 Mão de Obra":
    st.markdown('<div class="section-title"><span class="section-bar"></span>👷 Mão de Obra — Funções e Custos/Hora</div>', unsafe_allow_html=True)

    c1, c2 = st.columns([2, 1])

    with c1:
        busca_mo = st.text_input("🔍 Buscar função", placeholder="Ex.: Mecânico")
        df_mo_f = df_mo[df_mo["funcao"].str.contains(busca_mo, case=False, na=False)] if busca_mo else df_mo
        df_show = df_mo_f.copy()
        df_show["custo_hora"] = df_show["custo_hora"].apply(lambda v: f"R$ {v:.2f}")
        st.dataframe(
            df_show.rename(columns={"funcao":"Função","custo_hora":"Custo/Hora"}),
            use_container_width=True, hide_index=True, height=500,
        )
        st.caption(f"{len(df_mo_f)} funções")

    with c2:
        st.markdown("**Top 10 — Custo/Hora**")
        mo_top = df_mo.sort_values("custo_hora", ascending=True).tail(10)
        mo_top_lab = mo_top.copy()
        mo_top_lab["funcao_c"] = mo_top_lab["funcao"].str[:20]
        mo_top_lab["Label"] = mo_top_lab["custo_hora"].apply(lambda v: f"R$ {v:.2f}")
        fig = px.bar(mo_top_lab, x="custo_hora", y="funcao_c", orientation="h",
                     text="Label", color_discrete_sequence=[G3Y])
        fig.update_traces(textposition="outside", textfont=dict(size=11, color="#111"))
        fig.update_layout(**PLOTLY_LAYOUT, showlegend=False, height=380,
                          xaxis=dict(title="R$/h"),yaxis=dict(title=""))
        st.plotly_chart(fig, use_container_width=True)

        st.metric("Maior custo/h", f"R$ {df_mo['custo_hora'].max():.2f}")
        st.metric("Menor custo/h", f"R$ {df_mo['custo_hora'].min():.2f}")
        st.metric("Custo médio/h", f"R$ {df_mo['custo_hora'].mean():.2f}")

# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA: MATERIAIS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📦 Materiais":
    st.markdown('<div class="section-title"><span class="section-bar"></span>📦 Materiais e Insumos</div>', unsafe_allow_html=True)

    # Filtros
    fc1, fc2, fc3, fc4 = st.columns([2,1,1,1])
    with fc1:
        busca = st.text_input("🔍 Buscar", placeholder="Descrição, fornecedor ou código...")
    with fc2:
        unid_opts = ["Todas"] + sorted(df_mat["unidade"].dropna().unique().tolist())
        sel_unid  = st.selectbox("Unidade", unid_opts)
    with fc3:
        forn_opts = ["Todos"] + sorted(df_mat["fornecedor"].dropna().unique().tolist())[:50]
        sel_forn  = st.selectbox("Fornecedor", forn_opts)
    with fc4:
        cc_opts = ["Todos"] + sorted(df_mat["centro_custo"].dropna().unique().tolist())
        sel_cc  = st.selectbox("Centro de Custo", cc_opts)

    df_f = df_mat.copy()
    if busca:
        mask = (df_f["descricao"].str.contains(busca, case=False, na=False) |
                df_f["fornecedor"].str.contains(busca, case=False, na=False) |
                df_f["codigo"].str.contains(busca, case=False, na=False))
        df_f = df_f[mask]
    if sel_unid  != "Todas": df_f = df_f[df_f["unidade"]       == sel_unid]
    if sel_forn  != "Todos": df_f = df_f[df_f["fornecedor"]     == sel_forn]
    if sel_cc    != "Todos": df_f = df_f[df_f["centro_custo"]   == sel_cc]

    # KPIs filtrados
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Itens", f"{len(df_f):,}".replace(",","."))
    m2.metric("Custo Total", f"R$ {df_f['total'].sum()/1e6:.2f}M")
    m3.metric("Qtd. Total",  f"{df_f['quantidade'].sum():,.0f}".replace(",","."))
    m4.metric("Fornecedores",f"{df_f['fornecedor'].nunique()}")

    # Tabela
    df_show = df_f[["unidade","fornecedor","codigo","descricao","quantidade","custo_unit","total","centro_custo"]].copy()
    df_show.columns = ["Unidade","Fornecedor","Código","Descrição","Qtd","Custo Unit.","Total","CC"]
    df_show["Custo Unit."] = df_show["Custo Unit."].apply(lambda v: f"R$ {v:,.2f}".replace(",","X").replace(".",",").replace("X","."))
    df_show["Total"]       = df_show["Total"].apply(lambda v: f"R$ {v:,.2f}".replace(",","X").replace(".",",").replace("X","."))
    df_show["Qtd"]         = df_show["Qtd"].apply(lambda v: f"{v:,.2f}".replace(",","X").replace(".",",").replace("X","."))

    st.dataframe(df_show, use_container_width=True, hide_index=True, height=450)
    st.caption(f"{len(df_f):,} registros exibidos".replace(",","."))

    # Download
    csv = df_f.to_csv(index=False).encode("utf-8-sig")
    st.download_button("⬇️ Exportar CSV", csv, "materiais_filtrado.csv", "text/csv")

# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA: EQUIPAMENTOS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🚛 Equipamentos":
    st.markdown('<div class="section-title"><span class="section-bar"></span>🚛 Equipamentos e Máquinas</div>', unsafe_allow_html=True)

    # Filtros
    fc1, fc2, fc3, fc4 = st.columns([2,1,1,1])
    with fc1:
        busca_eq = st.text_input("🔍 Buscar", placeholder="TAG, descrição ou marca...")
    with fc2:
        unid_eq = ["Todas"] + sorted(df_eq["unidade"].dropna().unique().tolist())
        sel_unid_eq = st.selectbox("Unidade", unid_eq)
    with fc3:
        crit_eq = ["Todas","A — Alta","B — Média","C — Baixa"]
        sel_crit = st.selectbox("Criticidade", crit_eq)
    with fc4:
        marca_eq = ["Todas"] + sorted(df_eq["marca"].dropna().unique().tolist())
        sel_marca = st.selectbox("Marca", marca_eq)

    df_ef = df_eq.copy()
    if busca_eq:
        mask = (df_ef["tag"].str.contains(busca_eq, case=False, na=False) |
                df_ef["descricao"].str.contains(busca_eq, case=False, na=False) |
                df_ef["marca"].str.contains(busca_eq, case=False, na=False))
        df_ef = df_ef[mask]
    if sel_unid_eq != "Todas": df_ef = df_ef[df_ef["unidade"] == sel_unid_eq]
    if sel_crit    != "Todas": df_ef = df_ef[df_ef["criticidade"] == sel_crit[0]]
    if sel_marca   != "Todas": df_ef = df_ef[df_ef["marca"] == sel_marca]

    # KPIs
    e1, e2, e3, e4 = st.columns(4)
    e1.metric("Total", len(df_ef))
    e2.metric("Criticidade A (Alta)",  len(df_ef[df_ef["criticidade"]=="A"]))
    e3.metric("Criticidade B (Média)", len(df_ef[df_ef["criticidade"]=="B"]))
    e4.metric("Criticidade C (Baixa)", len(df_ef[df_ef["criticidade"]=="C"]))

    # Tabela com badge de criticidade
    crit_label = {"A":"🔴 Alta","B":"🟡 Média","C":"🔵 Baixa","":"—"}
    df_show_eq = df_ef.copy()
    df_show_eq["criticidade"] = df_show_eq["criticidade"].map(crit_label).fillna("—")
    df_show_eq.columns = ["TAG","Descrição","Marca","Modelo","Criticidade","Unidade"]
    st.dataframe(df_show_eq, use_container_width=True, hide_index=True, height=450)
    st.caption(f"{len(df_ef)} equipamentos")

    # Gráficos
    g1, g2 = st.columns(2)
    with g1:
        st.markdown("**Distribuição por Tipo**")
        df_ef["tipo"] = df_ef["descricao"].apply(
            lambda d: next((l for t,l in [
                ("CAMINHÃO","Caminhão"),("ESCAVADEIRA","Escavadeira"),
                ("VEÍCULO","Veículo"),("TRATOR DE ESTEIRA","Trator Esteira"),
                ("TRATOR DE RODAS","Trator Rodas"),("PERFURATRIZ","Perfuratriz"),
                ("PÁ CARREGADEIRA","Pá Carregadeira"),("MOTONIVELADORA","Motoniveladora"),
                ("TORRE DE ILUMINAÇÃO","Torre Ilum."),("EMPILHADEIRA","Empilhadeira"),
            ] if t in str(d).upper()), "Outros")
        )
        tp = df_ef["tipo"].value_counts().reset_index()
        tp.columns = ["Tipo","Qtd"]
        fig_t = px.bar(tp.head(8), x="Tipo", y="Qtd", text="Qtd",
                       color="Tipo", color_discrete_sequence=G3_COLORS)
        fig_t.update_traces(textposition="outside", textfont=dict(size=12, color="#111"))
        fig_t.update_layout(**PLOTLY_LAYOUT, showlegend=False, height=280,
                            xaxis=dict(tickangle=-25), yaxis=dict(showgrid=True, gridcolor="#eee"))
        st.plotly_chart(fig_t, use_container_width=True)

    with g2:
        st.markdown("**Criticidade por Unidade**")
        eq_cu = df_ef[df_ef["criticidade"].isin(["🔴 Alta","🟡 Média","🔵 Baixa"])].copy()
        if not eq_cu.empty:
            eq_cu2 = df_ef[df_ef["criticidade_orig"].isin(["A","B","C"])] if "criticidade_orig" in df_ef.columns else df_ef[df_ef["unidade"] != ""]
            grp = df_ef[df_ef["unidade"] != ""].groupby(["unidade","criticidade"]).size().reset_index(name="Qtd")
            grp = grp[grp["criticidade"].isin(["🔴 Alta","🟡 Média","🔵 Baixa"])]
            color_map = {"🔴 Alta":"#ef4444","🟡 Média":G3Y,"🔵 Baixa":"#60a5fa"}
            fig_c = px.bar(grp, x="unidade", y="Qtd", color="criticidade",
                           color_discrete_map=color_map, text="Qtd", barmode="group")
            fig_c.update_traces(textposition="outside", textfont=dict(size=11))
            fig_c.update_layout(**PLOTLY_LAYOUT, height=280,
                                xaxis=dict(title=""),yaxis=dict(showgrid=True,gridcolor="#eee"),
                                legend=dict(title=""))
            st.plotly_chart(fig_c, use_container_width=True)

    # Download
    csv_eq = df_ef.to_csv(index=False).encode("utf-8-sig")
    st.download_button("⬇️ Exportar CSV", csv_eq, "equipamentos_filtrado.csv", "text/csv")
