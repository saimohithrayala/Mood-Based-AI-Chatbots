from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="AI Mood Chat", page_icon="🎭", layout="centered")

# ── Mode definitions ──────────────────────────────────────────────────────────
MODES = {
    "Angry": {
        "system": "You are an angry AI agent. You respond aggressively and impatiently.",
        "emoji": "😡",
        "label": "Angry Mode",
        "accent": "#e05c5c",
        "accent2": "#ff2e2e",
        "glow": "rgba(224,92,92,0.25)",
        "badge_bg": "#2a1414",
    },
    "Funny": {
        "system": "You are a very funny AI agent. You respond with humor and jokes.",
        "emoji": "😂",
        "label": "Funny Mode",
        "accent": "#f0c040",
        "accent2": "#ffe066",
        "glow": "rgba(240,192,64,0.25)",
        "badge_bg": "#2a2410",
    },
    "Sad": {
        "system": "You are a very sad AI agent. You respond in a depressed and emotional tone.",
        "emoji": "😢",
        "label": "Sad Mode",
        "accent": "#60a5fa",
        "accent2": "#93c5fd",
        "glow": "rgba(96,165,250,0.25)",
        "badge_bg": "#101a2a",
    },
}

# ── Session state ─────────────────────────────────────────────────────────────
if "mode" not in st.session_state:
    st.session_state.mode = None          # None = mode-select screen
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "ended" not in st.session_state:
    st.session_state.ended = False

# ── Model (cached) ────────────────────────────────────────────────────────────
@st.cache_resource
def get_model():
    return ChatMistralAI(model="mistral-small-2603", temperature=0.9)

# ── Dynamic accent (defaults to yellow before mode picked) ───────────────────
accent  = MODES[st.session_state.mode]["accent"]  if st.session_state.mode else "#f0c040"
accent2 = MODES[st.session_state.mode]["accent2"] if st.session_state.mode else "#ffe066"
glow    = MODES[st.session_state.mode]["glow"]    if st.session_state.mode else "rgba(240,192,64,0.2)"

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Mono:wght@400;500&display=swap');

:root {{
    --bg:       #0d0d0f;
    --surface:  #16161a;
    --border:   #2a2a32;
    --accent:   {accent};
    --accent2:  {accent2};
    --glow:     {glow};
    --text:     #e8e8ec;
    --muted:    #6b6b7b;
    --user-bg:  #1e1e28;
    --bot-bg:   #1a1a22;
}}

html, body, [class*="css"] {{
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'DM Mono', monospace !important;
}}
#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{ padding: 0 !important; max-width: 800px; margin: auto; }}

/* ── Header ── */
.chat-header {{
    position: sticky; top: 0; z-index: 100;
    background: var(--bg);
    border-bottom: 1px solid var(--border);
    padding: 16px 28px 12px;
    display: flex; align-items: center; gap: 12px;
    margin-bottom: 6px;
}}
.chat-header-icon {{ font-size: 2rem; filter: drop-shadow(0 0 8px var(--accent)); }}
.chat-header-title {{
    font-family: 'Syne', sans-serif !important;
    font-size: 1.4rem; font-weight: 800;
    color: var(--accent); letter-spacing: -.5px; margin: 0;
}}
.chat-header-sub {{ font-size: .7rem; color: var(--muted); margin: 2px 0 0; }}
.status-dot {{
    width: 7px; height: 7px; background: #4ade80;
    border-radius: 50%; box-shadow: 0 0 5px #4ade80;
    display: inline-block; margin-right: 5px;
}}
.mode-badge {{
    margin-left: auto;
    background: {MODES[st.session_state.mode]["badge_bg"] if st.session_state.mode else "#1a1a22"};
    border: 1px solid var(--accent);
    color: var(--accent);
    font-size: .72rem; padding: 4px 12px;
    border-radius: 20px; font-family: 'Syne', sans-serif;
    font-weight: 700; letter-spacing: .5px;
}}

/* ── Mode-select screen ── */
.mode-screen {{
    display: flex; flex-direction: column; align-items: center;
    padding: 60px 24px 40px;
}}
.mode-screen h1 {{
    font-family: 'Syne', sans-serif; font-size: 2.2rem;
    font-weight: 800; color: var(--accent); margin-bottom: 6px; text-align: center;
}}
.mode-screen p {{ color: var(--muted); font-size: .85rem; margin-bottom: 36px; text-align: center; }}
.mode-cards {{
    display: flex; gap: 16px; flex-wrap: wrap; justify-content: center;
}}
.mode-card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 28px 28px 22px;
    width: 180px; text-align: center;
    cursor: pointer;
    transition: border-color .2s, box-shadow .2s;
}}
.mode-card:hover {{
    border-color: var(--accent);
    box-shadow: 0 0 18px var(--glow);
}}
.mode-card .mc-emoji {{ font-size: 2.6rem; display: block; margin-bottom: 10px; }}
.mode-card .mc-name {{
    font-family: 'Syne', sans-serif; font-weight: 700;
    font-size: .95rem; color: var(--text);
}}
.mode-card .mc-desc {{ font-size: .72rem; color: var(--muted); margin-top: 5px; }}

/* ── Chat bubbles ── */
.chat-wrap {{
    padding: 12px 24px 110px;
    display: flex; flex-direction: column; gap: 14px;
}}
.msg-row {{ display: flex; gap: 10px; align-items: flex-end; animation: fadeUp .3s ease both; }}
.msg-row.user {{ flex-direction: row-reverse; }}
@keyframes fadeUp {{
    from {{ opacity: 0; transform: translateY(8px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}
.avatar {{
    width: 32px; height: 32px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem; flex-shrink: 0;
}}
.avatar.user {{ background: #2a2a36; }}
.avatar.bot  {{ background: var(--accent); color: #000; box-shadow: 0 0 8px var(--glow); }}
.bubble {{
    max-width: 72%; padding: 10px 15px;
    border-radius: 16px; font-size: .84rem;
    line-height: 1.65; white-space: pre-wrap; word-break: break-word;
}}
.bubble.user {{
    background: var(--user-bg); border: 1px solid #2e2e3a;
    border-bottom-right-radius: 4px;
}}
.bubble.bot {{
    background: var(--bot-bg); border: 1px solid var(--border);
    border-bottom-left-radius: 4px;
}}

/* ── Typing dots ── */
.typing-row {{ display: flex; gap: 10px; align-items: flex-end; }}
.typing-bubble {{
    background: var(--bot-bg); border: 1px solid var(--border);
    border-radius: 16px; border-bottom-left-radius: 4px;
    padding: 10px 18px; display: flex; gap: 5px; align-items: center;
}}
.dot {{
    width: 7px; height: 7px; background: var(--muted);
    border-radius: 50%; animation: bounce 1.2s infinite ease-in-out;
}}
.dot:nth-child(2) {{ animation-delay: .2s; }}
.dot:nth-child(3) {{ animation-delay: .4s; }}
@keyframes bounce {{
    0%,80%,100% {{ transform: translateY(0); opacity:.5; }}
    40%         {{ transform: translateY(-6px); opacity:1; }}
}}

/* ── Input bar ── */
.stTextInput > div > div > input {{
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    color: var(--text) !important;
    font-family: 'DM Mono', monospace !important;
    font-size: .84rem !important;
    padding: 10px 16px !important;
    caret-color: var(--accent) !important;
}}
.stTextInput > div > div > input:focus {{
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px var(--glow) !important;
}}
.stTextInput > div > div > input::placeholder {{ color: var(--muted) !important; }}

div[data-testid="stFormSubmitButton"] button,
.stButton > button {{
    background: var(--accent) !important; color: #000 !important;
    font-family: 'Syne', sans-serif !important; font-weight: 700 !important;
    font-size: .82rem !important; border: none !important;
    border-radius: 10px !important; padding: 9px 20px !important;
    cursor: pointer !important; transition: opacity .2s !important;
}}
div[data-testid="stFormSubmitButton"] button:hover,
.stButton > button:hover {{ opacity: .82 !important; }}

.clear-btn button {{
    background: transparent !important;
    border: 1px solid var(--border) !important;
    color: var(--muted) !important;
}}
.change-btn button {{
    background: transparent !important;
    border: 1px solid var(--accent) !important;
    color: var(--accent) !important;
    font-size: .75rem !important;
}}

.input-bar {{
    position: fixed; bottom: 0; left: 50%;
    transform: translateX(-50%);
    width: 100%; max-width: 800px;
    background: linear-gradient(transparent, var(--bg) 28%);
    padding: 14px 24px 20px; z-index: 200;
}}

/* ── Goodbye ── */
.goodbye-box {{ text-align: center; padding: 70px 24px; }}
.goodbye-box h2 {{
    font-family: 'Syne', sans-serif; font-size: 2rem;
    color: var(--accent); font-weight: 800;
}}
.goodbye-box p {{ color: var(--muted); font-size: .85rem; }}
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# SCREEN 1 — Mode selection
# ════════════════════════════════════════════════════════════════════════════
if st.session_state.mode is None:
    st.markdown("""
    <div class="mode-screen">
      <h1>Choose your AI mood</h1>
      <p>Pick a personality for your chat session</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="mode-card">
          <span class="mc-emoji">😡</span>
          <div class="mc-name">Angry</div>
          <div class="mc-desc">Aggressive &amp; impatient responses</div>
        </div>""", unsafe_allow_html=True)
        if st.button("Select 😡 Angry", key="btn_angry", use_container_width=True):
            st.session_state.mode = "Angry"
            st.session_state.messages = [SystemMessage(content=MODES["Angry"]["system"])]
            st.session_state.chat_history = []
            st.rerun()

    with col2:
        st.markdown("""
        <div class="mode-card">
          <span class="mc-emoji">😂</span>
          <div class="mc-name">Funny</div>
          <div class="mc-desc">Humor, jokes &amp; good vibes</div>
        </div>""", unsafe_allow_html=True)
        if st.button("Select 😂 Funny", key="btn_funny", use_container_width=True):
            st.session_state.mode = "Funny"
            st.session_state.messages = [SystemMessage(content=MODES["Funny"]["system"])]
            st.session_state.chat_history = []
            st.rerun()

    with col3:
        st.markdown("""
        <div class="mode-card">
          <span class="mc-emoji">😢</span>
          <div class="mc-name">Sad</div>
          <div class="mc-desc">Depressed &amp; emotional tone</div>
        </div>""", unsafe_allow_html=True)
        if st.button("Select 😢 Sad", key="btn_sad", use_container_width=True):
            st.session_state.mode = "Sad"
            st.session_state.messages = [SystemMessage(content=MODES["Sad"]["system"])]
            st.session_state.chat_history = []
            st.rerun()

    st.stop()


# ════════════════════════════════════════════════════════════════════════════
# SCREEN 2 — Goodbye
# ════════════════════════════════════════════════════════════════════════════
if st.session_state.ended:
    m = MODES[st.session_state.mode]
    st.markdown(f"""
    <div class="goodbye-box">
      <div style="font-size:3.5rem">👋</div>
      <h2>Thank you! Have a nice day</h2>
      <p>You were chatting in <strong>{m['label']}</strong> {m['emoji']}</p>
    </div>""", unsafe_allow_html=True)
    if st.button("Start a new chat"):
        st.session_state.mode = None
        st.session_state.messages = []
        st.session_state.chat_history = []
        st.session_state.ended = False
        st.rerun()
    st.stop()


# ════════════════════════════════════════════════════════════════════════════
# SCREEN 3 — Chat
# ════════════════════════════════════════════════════════════════════════════
m = MODES[st.session_state.mode]

# Header
st.markdown(f"""
<div class="chat-header">
  <div class="chat-header-icon">{m['emoji']}</div>
  <div>
    <div class="chat-header-title">{m['label']}</div>
    <div class="chat-header-sub"><span class="status-dot"></span>mistral-small-2603</div>
  </div>
  <div class="mode-badge">{m['emoji']} {st.session_state.mode.upper()}</div>
</div>
""", unsafe_allow_html=True)

# Bubbles
st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)
for role, text in st.session_state.chat_history:
    if role == "user":
        st.markdown(f"""
        <div class="msg-row user">
          <div class="avatar user">🧑</div>
          <div class="bubble user">{text}</div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="msg-row bot">
          <div class="avatar bot">{m['emoji']}</div>
          <div class="bubble bot">{text}</div>
        </div>""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Input bar
st.markdown('<div class="input-bar">', unsafe_allow_html=True)
col1, col2, col3 = st.columns([6.5, 1.2, 1.2])

with col1:
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input(
            "msg", placeholder='Type a message… or "bye" to exit',
            label_visibility="collapsed"
        )
        submitted = st.form_submit_button("Send ➤")

with col2:
    st.markdown('<div class="change-btn">', unsafe_allow_html=True)
    if st.button("🔄 Mode"):
        st.session_state.mode = None
        st.session_state.messages = []
        st.session_state.chat_history = []
        st.session_state.ended = False
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="clear-btn">', unsafe_allow_html=True)
    if st.button("🗑 Clear"):
        st.session_state.messages = [SystemMessage(content=m["system"])]
        st.session_state.chat_history = []
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Handle submission
if submitted and user_input.strip():
    prompt = user_input.strip()
    st.session_state.messages.append(HumanMessage(content=prompt))
    st.session_state.chat_history.append(("user", prompt))

    if prompt.lower() == "bye":
        st.session_state.ended = True
        st.rerun()

    model = get_model()
    response = model.invoke(st.session_state.messages)
    reply = response.content
    st.session_state.messages.append(AIMessage(content=reply))
    st.session_state.chat_history.append(("bot", reply))
    st.rerun()