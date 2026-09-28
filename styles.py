import streamlit as st

CUSTOM_CSS = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

.stApp {
    background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
}

.main .block-container {
    padding-top: 2rem;
}

.sms-card {
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    backdrop-filter: blur(10px);
}

.sms-title {
    font-size: 2rem;
    font-weight: 800;
    color: #ffffff;
    margin-bottom: 0.2rem;
}

.sms-subtitle {
    color: #a0aec0;
    font-size: 0.95rem;
    margin-bottom: 1.5rem;
}

.metric-box {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 14px;
    padding: 1.2rem;
    color: white;
    text-align: center;
}

.metric-box h1 {
    font-size: 2.2rem;
    margin: 0;
}

.metric-box p {
    margin: 0;
    opacity: 0.85;
}

.stButton>button {
    border-radius: 10px;
    font-weight: 600;
    border: none;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 0.5rem 1.2rem;
}

.stButton>button:hover {
    opacity: 0.9;
    transform: translateY(-1px);
}

section[data-testid="stSidebar"] {
    background: rgba(10, 15, 25, 0.95);
}

section[data-testid="stSidebar"] * {
    color: #e2e8f0;
}

.login-box {
    max-width: 420px;
    margin: 4rem auto;
    background: rgba(255,255,255,0.07);
    padding: 2.5rem;
    border-radius: 20px;
    border: 1px solid rgba(255,255,255,0.15);
}

.badge-role {
    display: inline-block;
    padding: 0.2rem 0.8rem;
    border-radius: 20px;
    background: linear-gradient(135deg, #43cea2, #185a9d);
    color: white;
    font-size: 0.8rem;
    font-weight: 700;
}

.status-present {
    color: #48bb78;
    font-weight: 700;
}

.status-absent {
    color: #f56565;
    font-weight: 700;
}
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