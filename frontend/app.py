import os

import re
import logging

import requests

import streamlit as st

# ============================================================

# TKD INTELLIGENCE — PROFESSIONAL STREAMLIT FRONTEND

# Existing FastAPI API and session-based memory are preserved.

# No database is required.

# ============================================================

try:
    API_URL = st.secrets["TAEKWONDO_API_URL"]
except Exception:
    API_URL = os.getenv(
        "TAEKWONDO_API_URL",
        "http://127.0.0.1:8000/chat"
    )

REQUEST_TIMEOUT = 120

st.set_page_config(

    page_title="TKD Intelligence AI",

    page_icon="🥋",

    layout="wide",

    initial_sidebar_state="expanded",

)

# -------------------------- THEME ----------------------------

st.markdown(

    """

    <style>

    :root {

        --bg: #0a1220;

        --panel: #111e30;

        --panel2: #17273d;

        --line: rgba(148, 163, 184, .17);

        --text: #f1f5fb;

        --muted: #9aabc1;

        --blue: #60a5fa;

        --cyan: #67e8f9;

    }

    .stApp {

        background:

          radial-gradient(ellipse at 82% 0%, rgba(37,99,235,.16), transparent 34%),

          linear-gradient(145deg,#0a1220 0%,#0d1728 55%,#101b2d 100%);

        color: var(--text);

    }

    [data-testid="stHeader"] {background: rgba(10,18,32,.86);}

    [data-testid="stSidebar"] {

        background: #0c1728;

        border-right: 1px solid var(--line);

    }

    .block-container {max-width: 1280px; padding-top: 1.65rem; padding-bottom: 3rem;}

    h1,h2,h3,p,label {color: var(--text);}

    .brand-row {display:flex;align-items:center;gap:11px;margin:.2rem 0 .25rem;}

    .brand-icon {

        display:flex;align-items:center;justify-content:center;

        width:43px;height:43px;border-radius:13px;

        background:linear-gradient(135deg,#2563eb,#0891b2);

        font-size:1.4rem;

    }

    .brand-name {font-weight:850;letter-spacing:.105em;color:#f8fbff;font-size:.94rem;}

    .brand-sub {font-size:.64rem;letter-spacing:.16em;color:#8295af;margin-top:3px;}

    .eyebrow {font-size:.72rem;letter-spacing:.17em;text-transform:uppercase;color:var(--cyan);font-weight:800;}

    .hero-title {font-size:clamp(2.15rem,4vw,3.45rem);font-weight:850;line-height:1.07;letter-spacing:-.045em;color:#f8fbff;margin:.45rem 0 .7rem;}

    .hero-copy {max-width:760px;color:var(--muted);font-size:1rem;line-height:1.65;}

    .section-title {font-size:.78rem;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:#cfe2ff;margin:1.65rem 0 .85rem;}

    .agent-card {

        min-height:164px;height:100%;padding:1.15rem;

        border:1px solid #293b54;border-radius:17px;

        background:linear-gradient(150deg,rgba(26,42,65,.98),rgba(16,29,47,.98));

        box-shadow:0 12px 28px rgba(0,0,0,.15);

    }

    .agent-icon {font-size:1.65rem;margin-bottom:.65rem;}

    .agent-name {font-weight:780;color:#f1f5f9;font-size:.98rem;margin-bottom:.35rem;}

    .agent-desc {font-size:.82rem;color:#9fb0c7;line-height:1.52;}

    .panel {

        border:1px solid #293b54;border-radius:15px;

        background:rgba(18,32,51,.85);padding:1rem 1.1rem;

    }

    .status {

        display:inline-flex;align-items:center;gap:7px;padding:7px 11px;

        border:1px solid rgba(52,211,153,.28);border-radius:999px;

        background:rgba(16,185,129,.09);color:#6ee7b7;

        font-size:.7rem;font-weight:800;letter-spacing:.07em;

    }

    .status-dot {height:7px;width:7px;border-radius:50%;background:#34d399;}

    .stButton>button {

        min-height:2.7rem;border-radius:11px;

        border:1px solid #345273;background:#172b45;

        color:#edf4ff;font-weight:650;transition:.18s ease;

    }

    .stButton>button:hover {border-color:#67e8f9;background:#1d3b5d;color:#fff;}

    .stButton>button:focus {box-shadow:0 0 0 2px rgba(96,165,250,.25);}

    /* Premium fixed chat composer */

    [data-testid="stBottom"] {

        background: linear-gradient(180deg, rgba(10,18,32,.94), rgba(10,18,32,.99)) !important;

        border-top: 1px solid rgba(96,165,250,.12);

        backdrop-filter: blur(18px);

        padding: 0 !important;

    }

    [data-testid="stBottom"] > div {

        max-width: 100%;

        padding: .25rem .65rem .35rem !important;

        margin: 0 auto !important;

    }

    [data-testid="stChatInput"] {

        background: transparent !important;

        border: 0 !important;

        padding: 0 !important;

    }

    [data-testid="stChatInput"] > div {

        background: linear-gradient(145deg, #17283e, #101d30) !important;

        border: 1px solid #385675 !important;

        border-radius: 18px !important;

        box-shadow: 0 10px 30px rgba(0,0,0,.24), inset 0 1px 0 rgba(255,255,255,.035);

        padding: .12rem .35rem !important;

        transition: border-color .18s ease, box-shadow .18s ease;

    }

    [data-testid="stChatInput"] > div:focus-within {

        border-color: #67e8f9 !important;

        box-shadow: 0 0 0 2px rgba(103,232,249,.13), 0 12px 32px rgba(0,0,0,.28);

    }

    [data-testid="stChatInput"] textarea,

    .stChatInput textarea {

        min-height: 42px !important;

        max-height: 150px !important;

        padding: .55rem .7rem !important;

        background: transparent !important;

        color: #f8fbff !important;

        border: 0 !important;

        border-radius: 12px !important;

        box-shadow: none !important;

        font-size: .96rem !important;

        line-height: 1.5 !important;

    }

    [data-testid="stChatInput"] textarea::placeholder {

        color: #8fa5c1 !important;

        opacity: 1;

    }

    [data-testid="stChatInput"] button {

        background: linear-gradient(135deg,#2563eb,#0891b2) !important;

        color: white !important;

        border: 0 !important;

        border-radius: 12px !important;

        min-width: 42px;

        min-height: 42px;

        margin: .1rem;

    }

    [data-testid="stChatInput"] button:hover {

        background: linear-gradient(135deg,#1d4ed8,#0e7490) !important;

        box-shadow: 0 0 0 3px rgba(103,232,249,.12);

    }

    [data-testid="stChatMessage"] {

        border:1px solid rgba(148,163,184,.14);border-radius:16px;

        background:rgba(17,30,48,.78);padding:.8rem 1rem;margin-bottom:.8rem;

    }

    /* Readable assistant responses: spacing, wrapping and wide tables */

    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] {

        color: #e8f0fb;

        line-height: 1.72;

        overflow-wrap: anywhere;

        word-break: normal;

    }

    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p {

        margin: .45rem 0 .8rem;

        line-height: 1.72;

    }

    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h1,

    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h2,

    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h3 {

        margin: 1.15rem 0 .55rem;

        line-height: 1.3;

        color: #f5f8ff;

    }

    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] ul,

    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] ol {

        padding-left: 1.45rem;

        margin: .35rem 0 .9rem;

    }

    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] li {

        margin: .28rem 0;

        padding-left: .12rem;

    }

    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] table {

        display: block;

        width: 100%;

        overflow-x: auto;

        border-collapse: collapse;

        white-space: normal;

    }

    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] th {

        background: #1a2d46;

        color: #f4f8ff;

    }

    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] th,

    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] td {

        padding: .55rem .7rem;

        border: 1px solid #30445e;

        vertical-align: top;

    }

    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] pre {

        overflow-x: auto;

        border: 1px solid #30445e;

        border-radius: 10px;

        background: #0b1626;

    }

    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] blockquote {

        border-left: 3px solid #38bdf8;

        color: #b9c9dd;

        background: rgba(56,189,248,.06);

        padding: .35rem .8rem;

        border-radius: 0 8px 8px 0;

    }

    [data-testid="stCaptionContainer"] {color:#91a4bf;}

    div[data-baseweb="select"]>div {background:#111e30;border-color:#30445e;}

    [data-testid="stRadio"] label {color:#dbe7f6;}

    hr {border-color:#293b54;}

    footer {visibility:hidden;}

    .small-muted {color:#8295af;font-size:.76rem;line-height:1.55;}

    @media(max-width:750px) {

        .block-container {padding:1rem 1rem 2rem;}

        .hero-title {font-size:2.15rem;}

        .agent-card {min-height:145px;}

    }

    </style>

    """,

    unsafe_allow_html=True,

)

# ----------------------- SESSION STATE ----------------------

defaults = {

    "messages": [],

    "pending_question": None,

    "user_level": "Beginner",

    # Use a dedicated key for the radio widget. Do not modify it

    # directly after the radio widget has been instantiated.

    "page_selector": "Dashboard",

}

for key, value in defaults.items():

    if key not in st.session_state:

        st.session_state[key] = value

def reset_chat():

    st.session_state.messages = []

    st.session_state.pending_question = None

def open_assistant_with_question(question):

    """Callback runs before Streamlit instantiates the page selector."""

    st.session_state.page_selector = "AI Assistant"

    st.session_state.pending_question = question

def open_new_conversation():

    """Reset the chat and navigate using the widget's callback."""

    reset_chat()

    st.session_state.page_selector = "AI Assistant"

def clean_response(text):

    """

    Clean common LLM formatting glitches before displaying or saving an answer.

    Only obvious repeated tokens/lines are removed; normal sentences are kept.

    """

    text = str(text or "")

    # Normalize HTML paragraph and line-break tags.

    text = re.sub(r"<br\s\*/?>", "\n", text, flags=re.IGNORECASE)

    text = re.sub(r"</p\s\*>", "\n", text, flags=re.IGNORECASE)

    text = re.sub(r"<p\s\*>", "", text, flags=re.IGNORECASE)

    # Collapse obvious repeated English or Korean tokens.

    for _ in range(2):

        text = re.sub(

            r"(?iu)\b([a-z]{2,})(?:[ \t]+\1){3,}\b",

            r"\1",

            text,

        )

        text = re.sub(

            r"([가-힣]{1,12})(?:[ \t]+\1){3,}",

            r"\1",

            text,

        )

    # Remove exact duplicate consecutive lines without flattening Markdown.

    cleaned_lines = []

    previous_normalized = None

    for line in text.splitlines():

        normalized = re.sub(r"\s+", " ", line).strip()

        if normalized and normalized == previous_normalized:

            continue

        cleaned_lines.append(line.rstrip())

        previous_normalized = normalized if normalized else None

    text = "\n".join(cleaned_lines)

    text = re.sub(r"[ \t]+([.,;:])", r"\1", text)

    text = re.sub(r"\n[ \t]+", "\n", text)

    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()

def render_message_content(content):

    """Render Markdown safely and consistently inside chat messages."""

    st.markdown(clean_response(content), unsafe_allow_html=False)

def get_recent_history():

    return [

        {"role": item["role"], "content": clean_response(item["content"])}

        for item in st.session_state.messages[-6:]

        if item.get("role") in ("user", "assistant")

    ]

def ask_assistant(question):

    question = (question or "").strip()

    if not question:

        return

    history = get_recent_history()

    st.session_state.messages.append({"role": "user", "content": question})

    with st.chat_message("user", avatar="🙂"):

        st.markdown(question)

    with st.chat_message("assistant", avatar="🥋"):

        with st.spinner("Your question is being routed to the right specialist..."):

            try:

                response = requests.post(

                    API_URL,

                    json={

                        "question": question,

                        "user_level": st.session_state.user_level,

                        "chat_history": history,

                    },

                    timeout=REQUEST_TIMEOUT,

                )

                response.raise_for_status()

                payload = response.json()

                answer = clean_response(payload.get("answer", "No answer received."))

                category = payload.get("category", "unknown")

                render_message_content(answer)

                st.caption(f"Specialist agent · {str(category).replace('_', ' ').title()}")

                st.session_state.messages.append(

                    {

                        "role": "assistant",

                        "content": answer,

                        "category": category,

                    }

                )

            except requests.exceptions.ConnectionError:

                error = "The AI service is unreachable. Please check that the FastAPI backend is running."

                st.error(error)

                st.session_state.messages.append({"role": "assistant", "content": error})

            except requests.exceptions.Timeout:

                error = "The request timed out. Please try again."

                st.warning(error)

                st.session_state.messages.append({"role": "assistant", "content": error})

            except requests.exceptions.HTTPError:

                error = "The AI service returned an error. Check the FastAPI terminal for details."

                st.error(error)

                st.session_state.messages.append({"role": "assistant", "content": error})

            except (ValueError, requests.exceptions.RequestException) as exc:

                logging.exception("Unexpected frontend API response error")
                error = "We could not process that request. Please try again in a moment."

                st.error(error)

                st.session_state.messages.append({"role": "assistant", "content": error})

def show_header():

    left, right = st.columns([5, 1])

    with left:

        st.markdown(

            '<div class="eyebrow">Your intelligent Taekwondo companion</div>'

            '<div class="hero-title">Train smarter.<br>Compete stronger.</div>'

            '<div class="hero-copy">Practical guidance on techniques, official rules, '

            'athletic development and competition preparation — all in one place.</div>',

            unsafe_allow_html=True,

        )

    with right:

        st.markdown(

            '<div style="text-align:right;padding-top:.5rem">'

            '<span class="status"><span class="status-dot"></span> AI READY</span></div>',

            unsafe_allow_html=True,

        )

# ---------------------------- SIDEBAR ------------------------

with st.sidebar:

    st.markdown(

        '<div class="brand-row"><div class="brand-icon">🥋</div>'

        '<div><div class="brand-name">TKD INTELLIGENCE AI</div>'

        '<div class="brand-sub">TAEKWONDO AI PLATFORM</div></div></div>',

        unsafe_allow_html=True,

    )

    st.markdown('<div class="section-title">Workspace</div>', unsafe_allow_html=True)

    st.radio(

        "Navigate",

        ["Dashboard", "AI Assistant", "Athlete Workspace", "Coach Workspace", "Referee Workspace", "About"],

        key="page_selector",

        label_visibility="collapsed",

    )

    st.divider()

    st.markdown('<div class="section-title">Athlete preferences</div>', unsafe_allow_html=True)

    st.selectbox(

        "Experience level",

        ["Beginner", "Intermediate", "Advanced", "Professional"],

        key="user_level",

    )

    st.caption("Used to tailor guidance and training recommendations.")

    st.divider()

    st.markdown('<div class="section-title">Specialist agents</div>', unsafe_allow_html=True)

    st.markdown(

        """

        <div class="panel">⚖️ <b>Rules & Refereeing</b><br><span class="small-muted">WT regulations and match decisions</span></div><br>

        <div class="panel">🥋 <b>Training & Techniques</b><br><span class="small-muted">Skills, drills and Poomsae</span></div><br>

        <div class="panel">💪 <b>Fitness & Conditioning</b><br><span class="small-muted">Strength, stamina and recovery</span></div><br>

        <div class="panel">🏆 <b>Competition Strategy</b><br><span class="small-muted">Tournament and match preparation</span></div>

        """,

        unsafe_allow_html=True,

    )

    st.divider()

    st.button(

        "＋  New conversation",

        use_container_width=True,

        on_click=open_new_conversation,

    )

    if st.button("Clear conversation", use_container_width=True):

        reset_chat()

        st.rerun()

    st.markdown(

        '<div class="small-muted" style="margin-top:1rem">Session-only chat memory. '

        'Your conversation resets when the session is cleared or expires.</div>',

        unsafe_allow_html=True,

    )

# -------------------------- DASHBOARD ------------------------

active_page = st.session_state.page_selector

if active_page == "Dashboard":

    show_header()

    st.markdown(

        '<div class="section-title">Your specialist workspaces</div>',

        unsafe_allow_html=True,

    )

    agent_cards = [

        ("⚖️", "Rules & Refereeing", "Understand WT rules, scoring, penalties and referee decisions."),

        ("🥋", "Training & Techniques", "Improve kicks, stances, combinations, terminology and Poomsae."),

        ("💪", "Fitness & Conditioning", "Build strength, stamina, flexibility and recovery."),

        ("🏆", "Competition Strategy", "Prepare for tournaments, develop tactics and review performance."),

    ]

    cols = st.columns(4)

    for col, (icon, title, desc) in zip(cols, agent_cards):

        with col:

            st.markdown(

                f'<div class="agent-card"><div class="agent-icon">{icon}</div>'

                f'<div class="agent-name">{title}</div><div class="agent-desc">{desc}</div></div>',

                unsafe_allow_html=True,

            )

    st.markdown(

        '<div class="section-title">Start with a question</div>',

        unsafe_allow_html=True,

    )

    prompts = [

        "Give me five drills to improve my Dollyo Chagi.",

        "Explain the Gam-jeom penalty in WT Kyorugi.",

        "Create a weekly Taekwondo fitness plan.",

        "Give me a 7-day tournament preparation strategy.",

    ]

    prompt_cols = st.columns(2)

    for i, prompt in enumerate(prompts):

        with prompt_cols[i % 2]:

            st.button(

                prompt,

                key=f"dashboard_prompt_{i}",

                use_container_width=True,

                on_click=open_assistant_with_question,

                args=(prompt,),

            )

    st.markdown(

        '<div class="panel" style="margin-top:1.2rem"><b style="color:#f1f5fb">'

        'One assistant. Four specialist agents.</b><br>'

        '<span class="small-muted">Ask naturally. The AI supervisor selects the most relevant specialist '

        'and uses recent conversation context for follow-up questions.</span></div>',

        unsafe_allow_html=True,

    )

    if st.session_state.messages:

        st.markdown(

            '<div class="section-title">Recent conversation</div>',

            unsafe_allow_html=True,

        )

        for message in st.session_state.messages[-4:]:

            role_label = "You" if message["role"] == "user" else "TKD AI"

            preview = clean_response(message["content"])[:240]

            st.markdown(f"**{role_label}:** {preview}")

# ------------------------- AI ASSISTANT -----------------------

elif active_page == "AI Assistant":

    show_header()

    st.markdown(

        '<div class="section-title">AI assistant workspace</div>',

        unsafe_allow_html=True,

    )

    if not st.session_state.messages:

        st.markdown(

            '<div class="panel"><b style="color:#f1f5fb">Welcome to your Taekwondo AI assistant.</b><br>'

            '<span class="small-muted">Ask about rules, techniques, fitness or competition preparation. '

            'You can ask follow-up questions without repeating the context.</span></div>',

            unsafe_allow_html=True,

        )

    else:

        for message in st.session_state.messages:

            avatar = "🥋" if message["role"] == "assistant" else "🙂"

            with st.chat_message(message["role"], avatar=avatar):

                render_message_content(message["content"])

                if message["role"] == "assistant" and message.get("category"):

                    category_name = str(message["category"]).replace("_", " ").title()

                    st.caption(f"Specialist agent · {category_name}")

    pending = st.session_state.pending_question

    if pending:

        st.session_state.pending_question = None

        ask_assistant(pending)

    typed_question = st.chat_input("Message TKD Intelligence…  (Enter to send · Shift + Enter for a new line)")

    if typed_question:

        ask_assistant(typed_question)

    if st.session_state.messages:

        transcript = ["TKD INTELLIGENCE — CONVERSATION", ""]

        for item in st.session_state.messages:

            transcript.extend(

                [

                    "You:" if item["role"] == "user" else "TKD AI:",

                    clean_response(item["content"]),

                    "",

                ]

            )

        st.download_button(

            "Download conversation",

            data="\n".join(transcript),

            file_name="tkd_intelligence_conversation.txt",

            mime="text/plain",

        )

# ------------------------- ROLE WORKSPACES ---------------------

elif active_page in ("Athlete Workspace", "Coach Workspace", "Referee Workspace"):
    show_header()

    workspace_content = {
        "Athlete Workspace": {
            "icon": "🥋",
            "subtitle": "Build your skills, fitness and competition readiness.",
            "focus": [
                ("Technique development", "Work on kicking accuracy, speed, balance and combinations."),
                ("Fitness planning", "Structure strength, stamina, flexibility and recovery sessions."),
                ("Competition preparation", "Prepare your mindset, tactics and training schedule before events."),
            ],
            "prompts": [
                ("Technique improvement", "Create a 4-week plan to improve my Taekwondo kicking technique."),
                ("Weekly training plan", "Create a balanced weekly Taekwondo training plan for my experience level."),
                ("Competition readiness", "Give me a practical checklist to prepare for my next Taekwondo competition."),
                ("Fitness and recovery", "Create a Taekwondo-specific conditioning and recovery session."),
            ],
        },
        "Coach Workspace": {
            "icon": "🧑‍🏫",
            "subtitle": "Plan structured sessions and support student development.",
            "focus": [
                ("Class planning", "Create structured sessions with warm-up, skill work and cool-down."),
                ("Student development", "Adapt drills and progressions for different experience levels."),
                ("Performance support", "Plan measurable goals and review student progress through practice."),
            ],
            "prompts": [
                ("Class session plan", "Create a 60-minute Taekwondo class plan for mixed-level students."),
                ("Beginner curriculum", "Create a 4-week beginner Taekwondo training progression."),
                ("Drill library", "Suggest partner and individual drills for improving kicking technique."),
                ("Student assessment", "Create a practical skill assessment checklist for Taekwondo students."),
            ],
        },
        "Referee Workspace": {
            "icon": "⚖️",
            "subtitle": "Strengthen rule knowledge and practise match-officiating scenarios.",
            "focus": [
                ("Rules learning", "Review competition rules, scoring and penalties."),
                ("Match scenarios", "Practise decision-making using realistic referee situations."),
                ("Referee development", "Build consistency, positioning and communication skills."),
            ],
            "prompts": [
                ("Penalty scenarios", "Give me five WT Kyorugi Gam-jeom scenarios and explain the correct decisions."),
                ("Scoring review", "Explain valid scoring actions in WT Kyorugi with practical examples."),
                ("Referee positioning", "Explain referee positioning and movement during a Kyorugi match."),
                ("Knowledge quiz", "Quiz me with 10 Taekwondo referee rules questions, one at a time."),
            ],
        },
    }

    workspace = workspace_content[active_page]
    st.markdown(
        f'<div class="section-title">{active_page}</div>'
        f'<div class="panel"><div style="font-size:2rem">{workspace["icon"]}</div>'
        f'<h3 style="margin:.35rem 0">{active_page}</h3>'
        f'<span class="small-muted">{workspace["subtitle"]}</span></div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-title">Workspace focus</div>', unsafe_allow_html=True)
    focus_cols = st.columns(3)
    for col, (title, description) in zip(focus_cols, workspace["focus"]):
        with col:
            st.markdown(
                f'<div class="agent-card"><div class="agent-name">{title}</div>'
                f'<div class="agent-desc">{description}</div></div>',
                unsafe_allow_html=True,
            )

    st.markdown('<div class="section-title">Quick actions</div>', unsafe_allow_html=True)
    prompt_cols = st.columns(2)
    for index, (label, prompt) in enumerate(workspace["prompts"]):
        with prompt_cols[index % 2]:
            st.button(
                label,
                key=f"{active_page.lower().replace(' ', '_')}_{index}",
                help=prompt,
                use_container_width=True,
                on_click=open_assistant_with_question,
                args=(prompt,),
            )

    st.caption(
        "Quick actions open the existing AI Assistant. Your current specialist agents "
        "and session-based conversation memory continue to handle the questions."
    )


# ------------------------------- ABOUT ------------------------

else:

    show_header()

    st.markdown(

        '<div class="section-title">About TKD Intelligence</div>',

        unsafe_allow_html=True,

    )

    st.markdown(

        '<div class="panel"><h3 style="margin-top:0">Built for the Taekwondo community</h3>'

        '<span class="small-muted">TKD Intelligence is an AI-powered assistant designed to support '

        'athletes, coaches and referees with practical Taekwondo knowledge.</span></div>',

        unsafe_allow_html=True,

    )

    st.markdown(

        '<div class="section-title">What the platform offers</div>',

        unsafe_allow_html=True,

    )

    about_items = [

        ("Rules & Refereeing", "Answers questions about official WT competition rules using the connected rules knowledge base."),

        ("Training & Techniques", "Explains Taekwondo terminology, techniques, drills and practice plans."),

        ("Fitness & Conditioning", "Provides general strength, stamina, flexibility and recovery guidance."),

        ("Competition Strategy", "Helps athletes prepare for tournaments and think through match strategies."),

    ]

    for name, desc in about_items:

        st.markdown(

            f'<div class="panel" style="margin-bottom:.7rem"><b style="color:#f1f5fb">{name}</b><br>'

            f'<span class="small-muted">{desc}</span></div>',

            unsafe_allow_html=True,

        )

    st.caption(

        "Competition-critical decisions should always be checked against applicable official rules and qualified officials."

    )


    st.markdown(
        '<div class="section-title">Contact & support</div>',
        unsafe_allow_html=True,
    )
    contact_left, contact_right = st.columns(2)
    with contact_left:
        st.markdown(
            '<div class="panel"><b style="color:#f1f5fb">Email support</b><br>'
            '<span class="small-muted">Questions, feedback and support</span><br>'
            '<a href="mailto:dharanidhar2321@gmail.com" style="color:#67e8f9">'
            'dharanidhar2321@gmail.com</a></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="panel" style="margin-top:.8rem"><b style="color:#f1f5fb">WhatsApp</b><br>'
            '<span class="small-muted">Contact the developer</span><br>'
            '<a href="https://wa.me/917995141576" target="_blank" '
            'style="color:#67e8f9">+91 79951 41576</a></div>',
            unsafe_allow_html=True,
        )
    with contact_right:
        st.markdown(
            '<div class="panel"><b style="color:#f1f5fb">LinkedIn</b><br>'
            '<span class="small-muted">Connect with the developer</span><br>'
            '<a href="https://www.linkedin.com/in/dharanidharkola/" target="_blank" '
            'style="color:#67e8f9">Dharanidhar Kola</a></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="panel" style="margin-top:.8rem"><b style="color:#f1f5fb">TKD Intelligence</b><br>'
            '<span class="small-muted">AI-powered Taekwondo assistance for athletes, coaches and referees.</span>'
            '</div>',
            unsafe_allow_html=True,
        )


# ------------------------------ FOOTER ------------------------

st.markdown(

    '<div style="text-align:center;color:#64748b;font-size:.72rem;padding:2.2rem 0 .5rem">'

    'TKD INTELLIGENCE · AI-POWERED TAEKWONDO ASSISTANCE</div>',

    unsafe_allow_html=True,

)
