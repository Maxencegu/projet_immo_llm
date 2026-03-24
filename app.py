import streamlit as st
from dotenv import load_dotenv

load_dotenv(override=True)

# --- Configuration de la page ---
st.set_page_config(
    page_title="ImmoBot - Expert Immobilier",
    page_icon="🏠",
    layout="centered",
    initial_sidebar_state="expanded",
)

# --- CSS personnalisé ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Header */
    .header-card {
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 50%, #06b6d4 100%);
        padding: 2rem 2rem;
        border-radius: 16px;
        margin-bottom: 0.5rem;
        color: white;
        box-shadow: 0 8px 32px rgba(59, 130, 246, 0.3);
        position: relative;
        overflow: hidden;
    }
    .header-card::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 300px;
        height: 300px;
        background: rgba(255,255,255,0.05);
        border-radius: 50%;
    }
    .header-card h1 {
        margin: 0;
        font-size: 2rem;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    .header-card p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        font-size: 0.95rem;
    }

    /* Stats bar */
    .stats-bar {
        display: flex;
        gap: 1.5rem;
        margin-top: 1rem;
    }
    .stat-item {
        display: flex;
        align-items: center;
        gap: 0.4rem;
        font-size: 0.82rem;
        opacity: 0.85;
        color: white;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #0f172a;
        border-right: 1px solid #1e293b;
    }
    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h4 {
        color: #e2e8f0 !important;
    }

    /* Tool cards sidebar */
    .tool-card {
        background: linear-gradient(135deg, #1e293b, #1e3a5f);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 0.8rem 1rem;
        margin-bottom: 0.6rem;
        transition: border-color 0.2s;
    }
    .tool-card:hover {
        border-color: #3b82f6;
    }
    .tool-card .tool-name {
        color: #e2e8f0;
        font-weight: 600;
        font-size: 0.88rem;
    }
    .tool-card .tool-desc {
        color: #94a3b8;
        font-size: 0.78rem;
        margin-top: 2px;
    }

    /* Chat area */
    .stChatMessage {
        border-radius: 12px !important;
        padding: 0.8rem !important;
    }

    /* Chat input */
    .stChatInput {
        border-color: #334155 !important;
    }
    .stChatInput > div {
        border-radius: 12px !important;
        border-color: #334155 !important;
    }

    /* Welcome message */
    .welcome-box {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        margin: 2rem 0;
    }
    .welcome-box h3 {
        color: #e2e8f0;
        margin: 0.8rem 0 0.5rem 0;
        font-size: 1.2rem;
    }
    .welcome-box p {
        color: #94a3b8;
        font-size: 0.9rem;
        margin: 0;
    }

    /* Quick action chips */
    .chips-container {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        justify-content: center;
        margin-top: 1.2rem;
    }
    .chip {
        background: #0f172a;
        border: 1px solid #334155;
        color: #94a3b8;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.8rem;
    }

    /* Masquer UI Streamlit par défaut */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Sidebar buttons */
    section[data-testid="stSidebar"] .stButton > button {
        background: #1e293b;
        color: #94a3b8;
        border: 1px solid #334155;
        border-radius: 8px;
        font-size: 0.8rem;
        text-align: left;
        padding: 0.5rem 0.8rem;
        transition: all 0.2s;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: #334155;
        color: #e2e8f0;
        border-color: #3b82f6;
    }
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("""
<div class="header-card">
    <h1>🏠 ImmoBot</h1>
    <p>Votre expert immobilier intelligent en Ile-de-France</p>
    <div class="stats-bar">
        <div class="stat-item">📊 2 820 biens en base</div>
        <div class="stat-item">📍 8 departements couverts</div>
        <div class="stat-item">🤖 4 outils IA</div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.markdown("# 🏠 ImmoBot")
    st.caption("Expert immobilier IA")

    st.markdown("---")
    st.markdown("#### Outils disponibles")

    st.markdown("""
<div class="tool-card">
    <div class="tool-name">🔍 Recherche RAG</div>
    <div class="tool-desc">Guides, reglementation, infos agence</div>
</div>
<div class="tool-card">
    <div class="tool-name">🏠 Recherche filtree</div>
    <div class="tool-desc">Biens par ville, prix, surface, DPE, equipements</div>
</div>
<div class="tool-card">
    <div class="tool-name">📋 Frais de notaire</div>
    <div class="tool-desc">Calcul exact par tranche (ancien / neuf)</div>
</div>
<div class="tool-card">
    <div class="tool-name">💰 Simulation de pret</div>
    <div class="tool-desc">Mensualites, cout total, taux d'endettement</div>
</div>
""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### Essayez")

    examples = [
        ("🏘️", "T3 a Boulogne < 400 000 euros"),
        ("📋", "Frais de notaire pour 350 000 euros"),
        ("💰", "Pret de 300 000 euros sur 25 ans a 3,5%"),
        ("📖", "Etapes pour acheter un appartement"),
        ("⚡", "Bien classe F, puis-je le louer ?"),
    ]
    for icon, ex in examples:
        if st.button(f"{icon}  {ex}", key=ex, use_container_width=True):
            st.session_state["pending_question"] = ex

    st.markdown("---")
    st.caption("Créé avec LangChain et LangGraph")

# --- Initialisation de la session ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Message de bienvenue ---
if not st.session_state.messages:
    st.markdown("""
    <div class="welcome-box">
        <div style="font-size: 2.5rem;">🏠</div>
        <h3>Bienvenue sur ImmoBot !</h3>
        <p>Posez-moi vos questions sur l'immobilier en Ile-de-France :<br>
        recherche de biens, simulation de pret, frais de notaire, reglementation...</p>
        <div class="chips-container">
            <span class="chip">🔍 Recherche de biens</span>
            <span class="chip">💰 Simulation de pret</span>
            <span class="chip">📋 Frais de notaire</span>
            <span class="chip">📖 Guides & reglementation</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- Affichage de l'historique ---
for msg in st.session_state.messages:
    avatar = "🏠" if msg["role"] == "assistant" else "👤"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# --- Gestion de l'input ---
prompt = st.chat_input("Posez votre question sur l'immobilier...")

if "pending_question" in st.session_state:
    prompt = st.session_state.pop("pending_question")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🏠"):
        with st.spinner("Recherche en cours..."):
            from src.agent import answer_question
            history = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages[:-1]
            ]
            answer = answer_question(prompt, history)
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
