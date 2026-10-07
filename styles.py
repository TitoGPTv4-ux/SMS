import streamlit as st

CUSTOM_CSS = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

html { font-size: 17px; }

.stApp {
    background: #ffffff;
    color: #0b1220;
}

.main .block-container {
    padding-top: 2rem;
}

.stApp p, .stApp li, .stApp label, .stApp span,
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
.stApp [data-testid="stMarkdownContainer"],
.stApp [data-testid="stWidgetLabel"] * {
    color: #0b1220;
}

.stApp h3 { font-size: 1.5rem; font-weight: 800; }

.sms-card {
    background: #f1f5f9;
    border: 1px solid #94a3b8;
    border-left: 8px solid #667eea;
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}

.sms-title {
    font-size: 2.2rem;
    font-weight: 800;
    color: #000000 !important;
    margin-bottom: 0.2rem;
}

.sms-subtitle {
    color: #1e293b !important;
    font-size: 1.1rem;
    margin-bottom: 1.5rem;
}

.metric-box {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 14px;
    padding: 1.2rem;
    text-align: center;
}

.metric-box, .metric-box * { color: #ffffff !important; }

.metric-box h1 {
    font-size: 2.4rem;
    margin: 0;
}

.metric-box p {
    margin: 0;
    opacity: 1;
    font-size: 1.05rem;
    font-weight: 600;
}

.stButton>button,
[data-testid="stFormSubmitButton"]>button,
[data-testid="stDownloadButton"]>button {
    border-radius: 10px;
    font-weight: 700;
    font-size: 1.05rem;
    border: none;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 0.5rem 1.2rem;
}

.stButton>button, .stButton>button *,
[data-testid="stFormSubmitButton"]>button, [data-testid="stFormSubmitButton"]>button *,
[data-testid="stDownloadButton"]>button, [data-testid="stDownloadButton"]>button * {
    color: #ffffff !important;
}

.stButton>button:hover,
[data-testid="stFormSubmitButton"]>button:hover,
[data-testid="stDownloadButton"]>button:hover {
    opacity: 0.9;
    transform: translateY(-1px);
}

section[data-testid="stSidebar"] {
    background: #e2e8f0;
    border-right: 1px solid #94a3b8;
}

section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #0b1220 !important;
    font-weight: 600;
}

section[data-testid="stSidebar"] .badge-role { color: #ffffff !important; }

.stTextInput input, .stNumberInput input, .stTextArea textarea,
.stDateInput input, .stTimeInput input {
    background: #ffffff !important;
    color: #000000 !important;
    border: 1.5px solid #475569 !important;
    font-size: 1.05rem;
}

div[data-baseweb="select"] > div {
    background: #ffffff !important;
    color: #000000 !important;
    border: 1.5px solid #475569 !important;
}

div[data-baseweb="select"] * { color: #000000 !important; }

div[data-baseweb="popover"] ul,
div[data-baseweb="popover"] li {
    background: #ffffff !important;
    color: #000000 !important;
}

button[data-baseweb="tab"] p {
    color: #0b1220 !important;
    font-size: 1.1rem;
    font-weight: 700;
}

button[data-baseweb="tab"][aria-selected="true"] p { color: #5b3fd1 !important; }

.login-box {
    max-width: 420px;
    margin: 4rem auto;
    background: #f1f5f9;
    padding: 2.5rem;
    border-radius: 20px;
    border: 1px solid #94a3b8;
}

.badge-role {
    display: inline-block;
    padding: 0.2rem 0.8rem;
    border-radius: 20px;
    background: linear-gradient(135deg, #43cea2, #185a9d);
    color: #ffffff !important;
    font-size: 0.85rem;
    font-weight: 700;
}

.status-present { color: #15803d !important; font-weight: 800; }
.status-absent { color: #b91c1c !important; font-weight: 800; }
</style>
"""

def apply_styles():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

def page_header(title, subtitle=""):
    st.markdown(f"""
        <div class="sms-card">
            <div class="sms-title">{title}</div>
            <div class="sms-subtitle">{subtitle}</div>
        </div>
    """, unsafe_allow_html=True)

def metric_box(value, label):
    st.markdown(f"""
        <div class="metric-box">
            <h1>{value}</h1>
            <p>{label}</p>
        </div>
    """, unsafe_allow_html=True)