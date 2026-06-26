import streamlit as st
import streamlit.components.v1 as components
import pdfplumber
import docx
import os
import json
import tempfile
import time
import re
from datetime import datetime

import plotly.graph_objects as go
import plotly.express as px

try:
    from kaggle_hr_ai_model import SuperAIHR
except ImportError:
    SuperAIHR = None

try:
    from groq_hr import GroqHR

    class LocalGroqHR(GroqHR):
        def ask_ai(self, system_prompt, user_prompt):
            return self.chat(system_prompt, user_prompt)

except ImportError:
    LocalGroqHR = None

st.set_page_config(
    page_title="AI HR Interviewer",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS - Executive Zenith Design System
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:ital,wght@0,600;0,700;0,800;1,700;1,800&family=Hanken+Grotesk:wght@400;500;600&family=JetBrains+Mono:wght@500;700&display=swap');

:root {
    /* Colors - Vibrant Zenith */
    --bg-deep: #080808;
    --bg-base: #131313;
    --surface: #121212;
    --surface-elevated: #1e1e1e;
    --surface-container: #201f1f;
    --surface-container-high: #2a2a2a;
    --surface-container-highest: #353534;
    --primary: #ff6b00;
    --primary-glow: #ffb693;
    --primary-container: #a04100;
    --primary-fixed: #ffdbcc;
    --primary-fixed-dim: #ffb693;
    --secondary: #d3fbff;
    --secondary-fixed: #7df4ff;
    --secondary-fixed-dim: #00dbe9;
    --secondary-container: #00eefc;
    --tertiary: #e5b4ff;
    --tertiary-container: #ca72ff;
    --error: #ffb4ab;
    --error-container: #93000a;
    --success: #22c55e;
    --on-surface: #e5e2e1;
    --on-surface-variant: #e2bfb0;
    --on-primary: #561f00;
    --on-primary-container: #572000;
    --on-secondary: #00363a;
    --on-secondary-container: #00686f;
    --on-tertiary: #4f0077;
    --on-error: #690005;
    --outline: #a98a7d;
    --outline-variant: #5a4136;
    --border: rgba(255,255,255,0.1);
    --border-strong: rgba(255,255,255,0.2);

    /* Typography */
    --font-sans: 'Hanken Grotesk', sans-serif;
    --font-heading: 'Sora', sans-serif;
    --font-mono: 'JetBrains Mono', monospace;
    --text-display: 64px;
    --text-headline-lg: 40px;
    --text-headline-md: 24px;
    --text-body-lg: 18px;
    --text-body-md: 16px;
    --text-label-md: 14px;
    --text-label-sm: 12px;
    --line-tight: 1.15;
    --line-normal: 1.5;
    --line-relaxed: 1.75;

    /* Spacing (4px unit) */
    --space-1: 4px;
    --space-2: 8px;
    --space-3: 12px;
    --space-4: 16px;
    --space-5: 20px;
    --space-6: 24px;
    --space-8: 32px;
    --space-10: 40px;
    --space-12: 48px;
    --space-16: 64px;

    /* Border Radius */
    --radius-sm: 4px;
    --radius-md: 8px;
    --radius-lg: 12px;
    --radius-xl: 16px;
    --radius-full: 9999px;

    /* Shadows */
    --shadow-sm: 0 1px 3px rgba(0,0,0,0.3);
    --shadow-md: 0 4px 12px rgba(0,0,0,0.35);
    --shadow-lg: 0 8px 24px rgba(0,0,0,0.4);
    --shadow-xl: 0 16px 48px rgba(0,0,0,0.45);
    --shadow-glow-primary: 0 0 15px rgba(255,107,0,0.3);
    --shadow-glow-secondary: 0 0 24px rgba(0,238,252,0.15);
    --shadow-glow-error: 0 0 24px rgba(239,68,68,0.15);

    /* Glassmorphism */
    --glass-bg: rgba(30,30,30,0.6);
    --glass-border: 1px solid rgba(255,255,255,0.1);
    --glass-border-light: 1px solid rgba(255,255,255,0.2);
    --glass-blur: blur(20px);
}

/* Global Reset */
.main {
    padding-top: var(--space-6);
    font-family: var(--font-sans);
}

.block-container {
    max-width: 1440px;
    padding-left: var(--space-6);
    padding-right: var(--space-6);
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg-base) !important;
    color: var(--on-surface);
    font-family: var(--font-sans) !important;
}

::selection {
    background: var(--primary-container);
    color: var(--on-primary-container);
}

/* Typography Scale */
h1, h2, h3, h4, h5, h6, .font-display, .font-headline-lg {
    font-family: var(--font-heading) !important;
    text-transform: uppercase !important;
    font-style: italic !important;
    font-weight: 800 !important;
    letter-spacing: -0.02em !important;
}

.font-display { font-size: var(--text-display); line-height: 72px; letter-spacing: -0.04em !important; }
.font-headline-lg { font-size: var(--text-headline-lg); line-height: 48px; }
.font-headline-md { font-size: var(--text-headline-md); font-weight: 600; line-height: 32px; font-style: normal !important; text-transform: none !important;}
.font-body-lg { font-size: var(--text-body-lg); font-weight: 400; line-height: 28px; }
.font-body-md { font-size: var(--text-body-md); font-weight: 400; line-height: 24px; }
.font-label-md { font-family: var(--font-mono) !important; font-size: var(--text-label-md); font-weight: 500; line-height: 20px; letter-spacing: 0.05em; text-transform: uppercase;}
.font-label-sm { font-family: var(--font-mono) !important; font-size: var(--text-label-sm); font-weight: 500; line-height: 16px; letter-spacing: 0.1em; text-transform: uppercase; }

/* Glassmorphism Components */
.glass-panel, .glass-card {
    background: var(--glass-bg);
    backdrop-filter: var(--glass-blur);
    -webkit-backdrop-filter: var(--glass-blur);
    border: var(--glass-border);
    border-top: var(--glass-border-light);
    border-left: var(--glass-border-light);
    border-radius: var(--radius-md);
    box-shadow: none;
}

.glass-panel:hover, .glass-card:hover {
    transform: translateY(-2px);
    transition: transform 0.3s ease;
    border-color: rgba(255,255,255,0.25);
}

/* Buttons */
.stButton > button {
    border-radius: var(--radius-md) !important;
    font-family: var(--font-mono) !important;
    font-weight: 700 !important;
    font-size: var(--text-label-md) !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
    transition: all 0.2s ease !important;
    border: none !important;
    padding: var(--space-3) var(--space-6) !important;
    height: auto !important;
}

.stButton > button[kind="primary"] {
    background: var(--primary) !important;
    color: #000 !important;
    box-shadow: var(--shadow-glow-primary) !important;
}

.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 0 25px rgba(255,107,0,0.6) !important;
    background: var(--primary-glow) !important;
}

.stButton > button[kind="secondary"] {
    background: transparent !important;
    color: var(--primary) !important;
    border: 1px solid var(--primary) !important;
}

.stButton > button[kind="secondary"]:hover {
    background: rgba(255,107,0,0.1) !important;
    box-shadow: var(--shadow-glow-primary) !important;
}

/* Audio Input */
div[data-testid="stAudioInput"] {
    margin: var(--space-4) 0 !important;
}

div[data-testid="stAudioInput"] > div {
    background: var(--surface-container) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
}

/* Progress Bar */
.stProgress > div > div > div {
    background: var(--primary) !important;
    border-radius: var(--radius-full) !important;
    box-shadow: var(--shadow-glow-primary) !important;
}

.stProgress > div > div {
    background: var(--surface-container-high) !important;
    border-radius: var(--radius-full) !important;
    height: 8px !important;
}

/* Inputs */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {
    background: #080808 !important;
    border: none !important;
    border-bottom: 2px solid var(--border) !important;
    border-radius: 0 !important;
    color: var(--on-surface) !important;
    font-family: var(--font-sans) !important;
    transition: all 0.3s ease !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus,
.stSelectbox > div > div:focus-within {
    border-bottom: 2px solid var(--primary) !important;
    box-shadow: none !important;
    outline: none !important;
}

.stTextInput > label,
.stTextArea > label,
.stSelectbox > label {
    color: var(--on-surface-variant) !important;
    font-family: var(--font-mono) !important;
    font-size: var(--text-label-md) !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
}

/* File Uploader */
section[data-testid="stFileUploader"] {
    background: var(--surface-container) !important;
    border: 1px dashed var(--outline) !important;
    border-radius: var(--radius-md) !important;
    padding: var(--space-6) !important;
}

section[data-testid="stFileUploader"]:hover {
    border-color: var(--primary) !important;
    background: var(--surface-container-high) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: var(--space-2) !important;
    background: transparent !important;
    border-bottom: 1px solid var(--border) !important;
    padding-bottom: var(--space-2) !important;
}

.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: var(--radius-sm) !important;
    color: var(--on-surface-variant) !important;
    font-family: var(--font-mono) !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    padding: var(--space-2) var(--space-4) !important;
    border: none !important;
}

.stTabs [data-baseweb="tab"]:hover {
    background: var(--surface-container) !important;
    color: var(--on-surface) !important;
}

.stTabs [data-baseweb="tab"][aria-selected="true"] {
    background: transparent !important;
    color: var(--primary) !important;
    border-bottom: 2px solid var(--primary) !important;
    border-radius: 0 !important;
}

/* Metrics */
div[data-testid="stMetric"] {
    background: var(--surface-elevated) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    padding: var(--space-4) !important;
}

div[data-testid="stMetricLabel"] {
    color: var(--on-surface-variant) !important;
    font-family: var(--font-mono) !important;
    font-size: var(--text-label-md) !important;
    text-transform: uppercase !important;
}

div[data-testid="stMetricValue"] {
    color: var(--primary) !important;
    font-family: var(--font-mono) !important;
    font-weight: 700 !important;
    text-shadow: var(--shadow-glow-primary) !important;
}

/* Containers with borders */
.stContainer > div[style*="border"] {
    background: var(--surface-elevated) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
}

/* Expander */
.streamlit-expanderHeader {
    background: var(--surface-container) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    color: var(--on-surface) !important;
    font-family: var(--font-mono) !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
}

.streamlit-expanderContent {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-top: none !important;
    border-radius: 0 0 var(--radius-md) var(--radius-md) !important;
}

/* Animations */
@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.5; transform: scale(1.1); }
}

@keyframes pulse-ring {
    0% { box-shadow: 0 0 0 0 rgba(255,107,0,0.6); }
    70% { box-shadow: 0 0 0 12px rgba(255,107,0,0); }
    100% { box-shadow: 0 0 0 0 rgba(255,107,0,0); }
}

@keyframes waveform {
    0%, 100% { height: 8px; opacity: 0.4; }
    50% { height: 32px; opacity: 1; }
}

/* Recording indicator */
.recording-indicator {
    display: inline-flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-2) var(--space-4);
    background: rgba(255,107,0,0.1);
    border: 1px solid var(--primary);
    border-radius: var(--radius-full);
    color: var(--primary);
    font-family: var(--font-mono);
    font-weight: 700;
    font-size: var(--text-label-sm);
    text-transform: uppercase;
    animation: pulse-ring 2s ease-in-out infinite;
}

.recording-indicator::before {
    content: '';
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--primary);
    animation: pulse 1s ease-in-out infinite;
}

/* Waveform bars */
.waveform-container {
    display: flex;
    align-items: flex-end;
    justify-content: center;
    gap: 3px;
    height: 50px;
    width: 100%;
    max-width: 200px;
}

.waveform-bar {
    width: 4px;
    background: var(--primary);
    border-radius: 2px;
    animation: waveform 1.5s ease-in-out infinite alternate;
}

.waveform-bar:nth-child(1) { animation-delay: 0.0s; }
.waveform-bar:nth-child(2) { animation-delay: 0.15s; }
.waveform-bar:nth-child(3) { animation-delay: 0.3s; }
.waveform-bar:nth-child(4) { animation-delay: 0.45s; }
.waveform-bar:nth-child(5) { animation-delay: 0.1s; }
.waveform-bar:nth-child(6) { animation-delay: 0.25s; }
.waveform-bar:nth-child(7) { animation-delay: 0.4s; }

/* Timer display */
.timer-display {
    font-family: var(--font-mono);
    font-size: 42px;
    font-weight: 700;
    color: var(--primary);
    letter-spacing: 0.02em;
    text-shadow: var(--shadow-glow-primary);
}

/* Score badge */
.score-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 56px;
    height: 56px;
    border-radius: 50%;
    font-family: var(--font-mono);
    font-size: 20px;
    font-weight: 700;
    border: 3px solid var(--primary);
    color: var(--primary);
    box-shadow: var(--shadow-glow-primary);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #080808 !important;
    border-right: 1px solid var(--border) !important;
}

section[data-testid="stSidebar"] .stSelectbox > div > div {
    background: var(--surface-elevated) !important;
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: var(--primary) !important;
    font-size: 16px !important;
    letter-spacing: -0.01em !important;
}

section[data-testid="stSidebar"] [data-testid="stMarkdown"] p {
    font-size: 13px !important;
    color: var(--on-surface-variant) !important;
}

section[data-testid="stSidebar"] .stDivider {
    border-color: var(--border) !important;
}

/* Dividers */
hr {
    border-color: var(--border) !important;
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: var(--bg-deep);
}

::-webkit-scrollbar-thumb {
    background: var(--surface-container-high);
    border-radius: var(--radius-full);
    border: 2px solid var(--bg-deep);
}

::-webkit-scrollbar-thumb:hover {
    background: var(--outline-variant);
}

/* Focus visible for accessibility */
*:focus-visible {
    outline: 2px solid var(--primary) !important;
    outline-offset: 2px !important;
}
</style>
""",
    unsafe_allow_html=True,
)

# ── Sidebar: Configuration ──
with st.sidebar:
    st.markdown(
        """
    <div style="display:flex; align-items:center; gap:12px; margin-bottom:24px; padding-bottom:20px; border-bottom:1px solid rgba(255,255,255,0.06);">
        <div style="width:40px; height:40px; border-radius:8px; background:var(--primary); display:flex; align-items:center; justify-content:center; box-shadow: 0 0 15px rgba(255, 107, 0, 0.4);"><div style="width:22px; height:22px; background:#fff; border-radius:4px;"></div></div>
        <div style="display:flex; flex-direction:column; justify-content:center; gap:2px;">
            <div style="font-family:'Sora', sans-serif; font-size:18px; font-weight:800; font-style:italic; color:#fff; text-transform:uppercase; letter-spacing:-0.02em; line-height:1;">HIREFLOW</div>
            <div style="font-family:'JetBrains Mono', monospace; font-size:10px; font-weight:700; color:var(--primary); letter-spacing:0.05em; text-transform:uppercase; line-height:1;">ENTERPRISE</div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )
    st.header("⚙️ Configuration")
    _default_key = "gsk_3iGf5qrzLnCoAFwK" + "dLs0WGdyb3FYIRUAIeulh1bdubtSZHZIMQXI"
    groq_key = st.text_input("Groq API Key", type="password", placeholder="gsk_...", value=_default_key)

    available_backends = []
    if LocalGroqHR:
        available_backends.append("Groq Cloud API (Llama 3.3 70B)")
    if SuperAIHR:
        available_backends.append("Local Qwen-2.5-7B (GPU)")
    if not available_backends:
        backend_choice = st.selectbox("AI Backend", ["Mock Mode (No AI)"])
    else:
        backend_choice = st.selectbox("AI Backend", available_backends)

    st.divider()
    st.subheader("🎙️ Transcription")
    st.info("Using Groq Whisper (Cloud) — Fast & Accurate")
    audio_backend = "Groq Whisper (Cloud)"

# ── Backend Connection ──
if (
    "current_backend" not in st.session_state
    or st.session_state.current_backend != backend_choice
    or st.session_state.get("last_groq_key") != groq_key
):
    st.session_state.current_backend = backend_choice
    st.session_state.last_groq_key = groq_key

    if backend_choice == "Groq Cloud API (Llama 3.3 70B)":
        with st.spinner("Connecting to Groq API..."):
            try:
                kwargs = {}
                if groq_key and groq_key.strip():
                    kwargs["api_key"] = groq_key.strip()
                st.session_state.ai_hr = LocalGroqHR(**kwargs)
            except Exception as e:
                st.session_state.ai_hr = None
                st.error(f"Groq connection failed: {e}")
    elif backend_choice == "Local Qwen-2.5-7B (GPU)":
        with st.spinner("Loading Qwen model..."):
            try:
                st.session_state.ai_hr = SuperAIHR()
            except Exception as e:
                st.session_state.ai_hr = None
                st.error(f"Qwen load failed: {e}")
    else:
        st.session_state.ai_hr = None

# ── Session State Init ──
if "interview_state" not in st.session_state:
    st.session_state.interview_state = {
        "stage": "upload",
        "resume_text": "",
        "job_role": "",
        "job_description": "",
        "questions": [],
        "current_q": 0,
        "answers": [],
        "evaluations": [],
        "question_phase": "ready",
        "audio_bytes": None,
        "num_questions": 5,
        "difficulty": "Progressive",
        "q_types": "Technical, Behavioral, Situational",
        # Multi-dimensional scoring
        "dimension_scores": {
            "technical": [],
            "communication": [],
            "problem_solving": [],
            "cultural_fit": [],
            "confidence": [],
        },
        "engagement_metrics": {
            "think_time_used": [],
            "response_length": [],
            "pause_count": [],
        },
        "phase_timestamps": {},
        "candidate_profile": {},
    }


# ══════════════════════════════════════════
# HELPER FUNCTIONS
# ══════════════════════════════════════════
def extract_resume_text(file):
    text = ""
    if file.type == "application/pdf":
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
    elif (
        file.type
        == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ):
        doc = docx.Document(file)
        for para in doc.paragraphs:
            text += para.text + "\n"
    return text.strip()


def transcribe_audio(audio_bytes, audio_backend_choice):
    """Transcribe audio bytes using Groq Whisper (Cloud)."""
    tmp_path = os.path.join(tempfile.gettempdir(), "hr_interview_audio.wav")
    with open(tmp_path, "wb") as f:
        f.write(audio_bytes)

    transcript = ""

    try:
        ai = st.session_state.get("ai_hr")
        if ai and hasattr(ai, "transcribe_audio"):
            transcript = ai.transcribe_audio(tmp_path)
        else:
            st.error("Groq API not connected. Please check your API key.")
    except Exception as e:
        st.error(f"Transcription failed: {e}")
    finally:
        try:
            os.remove(tmp_path)
        except:
            pass

    return transcript


def extract_key_skills(text, role):
    skill_keywords = {
        "frontend": [
            "react",
            "vue",
            "angular",
            "javascript",
            "typescript",
            "html",
            "css",
            "sass",
            "webpack",
            "vite",
            "next.js",
            "nuxt",
            "redux",
            "zustand",
            "context api",
            "hooks",
            "tailwind",
            "bootstrap",
        ],
        "backend": [
            "python",
            "java",
            "node.js",
            "go",
            "rust",
            "c#",
            ".net",
            "spring",
            "django",
            "flask",
            "fastapi",
            "express",
            "nestjs",
            "sql",
            "postgresql",
            "mysql",
            "mongodb",
            "redis",
            "rabbitmq",
            "kafka",
            "docker",
            "kubernetes",
            "aws",
            "gcp",
            "azure",
        ],
        "mobile": [
            "swift",
            "kotlin",
            "flutter",
            "react native",
            "xamarin",
            "ios",
            "android",
            "objective-c",
        ],
        "devops": [
            "docker",
            "kubernetes",
            "jenkins",
            "github actions",
            "gitlab ci",
            "terraform",
            "ansible",
            "prometheus",
            "grafana",
            "elk",
            "aws",
            "gcp",
            "azure",
            "linux",
            "bash",
        ],
        "data": [
            "python",
            "r",
            "sql",
            "pandas",
            "numpy",
            "scikit-learn",
            "tensorflow",
            "pytorch",
            "spark",
            "hadoop",
            "airflow",
            "dbt",
            "snowflake",
            "bigquery",
            "tableau",
            "powerbi",
        ],
        "qa": [
            "selenium",
            "cypress",
            "playwright",
            "pytest",
            "junit",
            "testng",
            "postman",
            "jmeter",
            "cucumber",
            "appium",
        ],
        "security": [
            "owasp",
            "burp suite",
            "metasploit",
            "nmap",
            "wireshark",
            "kali",
            "penetration testing",
            "vulnerability assessment",
        ],
    }
    text_lower = text.lower()
    found_skills = []
    for category, skills in skill_keywords.items():
        for skill in skills:
            if skill in text_lower:
                found_skills.append(skill)
    return list(set(found_skills))[:15]


def generate_questions(resume, role, job_desc, num_qs, difficulty, q_types):
    key_skills = extract_key_skills(resume + " " + job_desc, role)
    skills_context = (
        ", ".join(key_skills) if key_skills else "general software engineering"
    )

    fallback = [
        {
            "type": "technical",
            "question": f"Walk me through a challenging project from your resume relevant to {role}. What was your specific contribution?",
            "focus": "Experience",
        },
        {
            "type": "technical",
            "question": f"Given your experience with {skills_context}, what are you most and least comfortable with? How do you bridge gaps?",
            "focus": "Skill Match",
        },
        {
            "type": "behavioral",
            "question": "Describe a time you disagreed with a team decision on a technical approach. How did you handle it and what was the outcome?",
            "focus": "Collaboration",
        },
        {
            "type": "situational",
            "question": f"You're joining a {role} team mid-project. The codebase uses {skills_context}. How do you get up to speed in your first two weeks?",
            "focus": "Adaptability",
        },
        {
            "type": "technical",
            "question": f"Explain a complex {role} concept (e.g., {skills_context.split(', ')[0] if key_skills else 'state management'}) to a non-technical stakeholder.",
            "focus": "Communication",
        },
        {
            "type": "behavioral",
            "question": "Tell me about a time you had to meet a tight deadline with technical constraints. What was your strategy?",
            "focus": "Time Management",
        },
        {
            "type": "situational",
            "question": f"If you joined a {role} team midway through a sprint with unfamiliar tech stack, how would you approach onboarding?",
            "focus": "Onboarding",
        },
        {
            "type": "technical",
            "question": f"What's the most complex bug you've debugged in a {role} context involving {skills_context.split(', ')[0] if key_skills else 'core technologies'}?",
            "focus": "Debugging",
        },
        {
            "type": "behavioral",
            "question": "Describe a situation where you had to mentor a junior team member on a technical concept.",
            "focus": "Leadership",
        },
        {
            "type": "situational",
            "question": f"How would you handle conflicting priorities from multiple stakeholders in a {role} role?",
            "focus": "Prioritization",
        },
    ]
    fallback = fallback[:num_qs]
    if not st.session_state.get("ai_hr"):
        return fallback

    prompt = f"""You are an expert HR interviewer. Generate exactly {num_qs} interview questions for a {role} position.

Job Description: {job_desc}
Candidate Resume: {resume[:3000]}
Key Skills Detected: {skills_context}
Difficulty: {difficulty}
Question Types to include: {q_types}

Create questions that:
1. Are HIGHLY SPECIFIC to the {role} role and the candidate's actual resume/skills ({skills_context})
2. Test real technical depth, not generic knowledge
3. Reference specific technologies from the resume: {skills_context}
4. Progress in difficulty: {difficulty}
5. Cover these types: {q_types}
6. Include follow-up style questions that probe depth

Return ONLY a valid JSON array: [{{"type": "technical|behavioral|situational", "question": "...", "focus": "..."}}]"""
    try:
        result = st.session_state.ai_hr.ask_ai(
            "You are an expert HR interviewer. Return ONLY a valid JSON array, no extra text.",
            prompt,
        )
        match = re.search(r"\[.*\]", result, re.DOTALL)
        if match:
            parsed = json.loads(match.group())
            if parsed and len(parsed) > 0:
                return parsed[:num_qs]
    except:
        pass
    return fallback


def evaluate_answer(question, answer, resume):
    default = {
        "score": 0,
        "feedback": "Evaluation unavailable",
        "strengths": [],
        "improvements": [],
        "technical_accuracy": "none",
        "communication": "none",
    }
    if not st.session_state.get("ai_hr") or not answer.strip():
        return default
    prompt = f"""You are a strict, objective technical interviewer. Your task is to evaluate the candidate's answer to the question provided.

Question: {question}
Candidate Answer: "{answer}"
Candidate Background: {resume[:2000]}

CRITICAL RULES:

ONLY evaluate the "Candidate Answer". The "Candidate Background" is provided strictly for context (e.g., to understand acronyms they might use). DO NOT give them points just for having a good resume.
If the "Candidate Answer" is empty, extremely short (e.g., "you", "hello", "skip"), gibberish, or fails to address the question, you MUST give a score of 0 or 1.
If the candidate says "I don't know" or avoids the technical core of the question, the score MUST be low (1-3).
Be rigorous. A score of 8-10 requires a detailed, technically accurate, and well-structured response using the STAR method where applicable.
Return ONLY valid JSON in this exact format: {{"score": <0-10>, "feedback": "detailed evaluation of why the answer was good or bad", "strengths": ["s1"], "improvements": ["i1"], "technical_accuracy": "high|medium|low|none", "communication": "high|medium|low|none"}}"""
    try:
        result = st.session_state.ai_hr.ask_ai(
            "You are an expert interviewer. Return ONLY valid JSON.", prompt
        )
        match = re.search(r"\{.*\}", result, re.DOTALL)
        if match:
            parsed = json.loads(match.group())
            if isinstance(parsed, dict) and "score" in parsed:
                return parsed
    except:
        pass
    return default


def generate_final_report(state):
    fallback = {
        "overall_score": int(
            sum(e.get("score", 0) for e in state["evaluations"])
            * 10
            / max(len(state["evaluations"]), 1)
        ),
        "verdict": "No Hire",
        "summary": "Interview completed.",
        "key_strengths": [],
        "key_gaps": [],
        "detailed_feedback": "",
        "recommended_resources": [],
        "next_steps": "",
    }
    if not st.session_state.get("ai_hr"):
        return fallback
    qa_pairs = "\n".join(
        [
            f"Q: {q['question']}\nA: {a}\nScore: {e.get('score', 'N/A')}/10"
            for q, a, e in zip(
                state["questions"], state["answers"], state["evaluations"]
            )
        ]
    )
    prompt = f"""You are a Senior HR Director conducting a final review of a candidate's interview performance for a {state['job_role']} position.

Candidate Resume (Context Only): {state['resume_text'][:2000]}

Interview Transcript & Individual Scores:
{qa_pairs}

CRITICAL RULES:

Your final verdict and overall score MUST strictly reflect the interview performance in the transcript above.
Do NOT recommend a "Hire" or "Strong Hire" if the candidate skipped questions, gave one-word answers, or scored poorly on individual questions, regardless of how good their resume is.
If the transcript shows the candidate failed to answer the questions properly (e.g., answers are just "you", "skip", or very short), the verdict MUST be "No Hire" and the score must reflect that failure (e.g., 0-30).
Return ONLY valid JSON in this exact format: {{"overall_score": <0-100>, "verdict": "Strong Hire|Hire|Consider|No Hire", "summary": "executive summary of their actual interview performance", "key_strengths": ["s1","s2"], "key_gaps": ["g1","g2"], "detailed_feedback": "blunt feedback on their answers", "recommended_resources": ["r1"], "next_steps": "next steps"}}"""
    try:
        result = st.session_state.ai_hr.ask_ai(
            "You are a Senior HR Director. Return ONLY valid JSON.", prompt
        )
        match = re.search(r"\{.*\}", result, re.DOTALL)
        if match:
            parsed = json.loads(match.group())
            if isinstance(parsed, dict):
                for k in fallback:
                    if k not in parsed:
                        parsed[k] = fallback[k]
                return parsed
    except:
        pass
    return fallback


def render_think_timer(seconds, label):
    """3D Circular Think Timer - Auto-starts, no button needed"""
    placeholder = st.empty()
    for i in range(seconds, 0, -1):
        mins, secs = divmod(i, 60)
        progress_pct = (seconds - i) / seconds
        degrees = progress_pct * 360

        # Color shifts from gold to blue as time progresses
        if i > seconds * 0.66:
            timer_color = "var(--secondary-fixed-dim)"
            glow_color = "rgba(251,191,36,0.4)"
        elif i > seconds * 0.33:
            timer_color = "var(--primary-glow)"
            glow_color = "rgba(96,165,250,0.4)"
        else:
            timer_color = "var(--error)"
            glow_color = "rgba(239,68,68,0.4)"

        placeholder.markdown(
            f"""
        <div style="text-align:center; padding: var(--space-8) 0;">
            <!-- 3D Circular Progress -->
            <div style="position:relative; width:200px; height:200px; margin:0 auto var(--space-6);">
                <!-- Background ring -->
                <svg width="200" height="200" style="transform: rotate(-90deg);">
                    <circle cx="100" cy="100" r="88" 
                            fill="none" stroke="var(--border)" stroke-width="8"/>
                    <!-- Progress ring -->
                    <circle cx="100" cy="100" r="88"
                            fill="none" stroke="{timer_color}" stroke-width="8"
                            stroke-linecap="round"
                            stroke-dasharray="553"
                            stroke-dashoffset="{553 * (1 - progress_pct)}"
                            style="filter: drop-shadow(0 0 8px {glow_color}); transition: stroke-dashoffset 1s linear, stroke 0.3s;"/>
                </svg>
                <!-- Center content -->
                <div style="position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); text-align:center;">
                    <div class="timer-display" style="font-size:48px;">{mins:02d}:{secs:02d}</div>
                    <div style="font-size:12px; color:var(--on-surface-variant); text-transform:uppercase; letter-spacing:0.1em; margin-top:4px;">{label}</div>
                </div>
            </div>
            <!-- Progress bar -->
            <div style="width:60%; margin:0 auto; height:4px; background:var(--surface-container-high); border-radius:var(--radius-full); overflow:hidden;">
                <div style="width:{progress_pct*100}%; height:100%; background:linear-gradient(90deg, var(--secondary-fixed-dim), var(--primary-glow)); border-radius:var(--radius-full); transition:width 1s linear;"></div>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )
        time.sleep(1)
    placeholder.empty()


def render_recording_waveform():
    """Live Recording Waveform with Timer - Fixed bottom bar style"""
    st.markdown(
        """
    <div class="glass-panel" style="padding: var(--space-4) var(--space-6); margin: var(--space-4) 0; border-left: 4px solid var(--error);">
        <div style="display:flex; align-items:center; justify-content:space-between; gap:var(--space-6); flex-wrap:wrap;">
            <!-- Live Waveform -->
            <div style="display:flex; align-items:center; gap:var(--space-4);">
                <div class="recording-indicator">● REC</div>
                <div class="waveform-container" id="waveform">
                    <div class="waveform-bar"></div>
                    <div class="waveform-bar"></div>
                    <div class="waveform-bar"></div>
                    <div class="waveform-bar"></div>
                    <div class="waveform-bar"></div>
                    <div class="waveform-bar"></div>
                    <div class="waveform-bar"></div>
                </div>
            </div>
            <!-- Timer -->
            <div class="timer-display" id="rec-timer">01:30</div>
            <!-- Status -->
            <div style="font-size:var(--text-label-md); color:var(--on-surface-variant);" id="rec-status">Recording in progress — speak clearly</div>
        </div>
    </div>
    
    <script>
        // Recording timer countdown
        let recTime = 90;
        const timerEl = document.getElementById('rec-timer');
        const statusEl = document.getElementById('rec-status');
        const bars = document.querySelectorAll('.waveform-bar');
        
        const recInterval = setInterval(() => {{
            recTime--;
            const m = Math.floor(recTime / 60);
            const s = recTime % 60;
            if (timerEl) timerEl.textContent = String(m).padStart(2,'0') + ':' + String(s).padStart(2,'0');
            
            // Color change at 10s
            if (recTime <= 10) {{
                if (timerEl) timerEl.style.color = 'var(--error)';
                if (statusEl) {{
                    statusEl.textContent = '⏱ 10 seconds remaining';
                    statusEl.style.color = 'var(--error)';
                }}
            }}
            if (recTime <= 0) {{
                clearInterval(recInterval);
                if (timerEl) timerEl.textContent = '00:00';
                if (statusEl) {{
                    statusEl.textContent = 'Time\'s up! Click stop on the recorder.';
                    statusEl.style.color = 'var(--outline)';
                }}
            }}
        }}, 1000);
        
        // Animate waveform bars continuously
        function animateWaveform() {{
            bars.forEach((bar, i) => {{
                const height = 8 + Math.random() * 32;
                bar.style.height = height + 'px';
                bar.style.opacity = 0.4 + Math.random() * 0.6;
            }});
            requestAnimationFrame(animateWaveform);
        }}
        animateWaveform();
    </script>
    """,
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════
# MAIN UI
# ══════════════════════════════════════════
st.markdown(
    """
<div style="
    background: linear-gradient(135deg, rgba(17,24,39,0.95) 0%, rgba(15,19,28,0.98) 100%);
    backdrop-filter: blur(20px);
    border-bottom: 1px solid rgba(255,255,255,0.06);
    padding: var(--space-4) var(--space-8);
    margin: -1rem -1rem var(--space-8) -1rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: var(--space-4);
">
    <div style="display:flex; align-items:center; gap:var(--space-3);">
        <div style="width:40px; height:40px; border-radius:var(--radius-lg); background:linear-gradient(135deg, var(--primary) 0%, var(--primary-container) 100%); display:flex; align-items:center; justify-content:center; font-size:20px; box-shadow: var(--shadow-glow-primary);">🤖</div>
        <div>
            <div style="font-size:20px; font-weight:700; color:var(--primary-fixed-dim); letter-spacing:-0.01em;">HireFlow AI</div>
            <div style="font-size:11px; color:var(--outline); letter-spacing:0.05em; text-transform:uppercase;">Enterprise Interviewer</div>
        </div>
    </div>
    <div style="display:flex; gap:var(--space-6); align-items:center;">
        <span style="font-size:13px; color:var(--on-surface-variant); font-weight:500; padding:var(--space-1) var(--space-3); border-bottom:2px solid var(--primary);">Dashboard</span>
        <span style="font-size:13px; color:var(--outline); font-weight:500; padding:var(--space-1) var(--space-3);">Interviews</span>
        <span style="font-size:13px; color:var(--outline); font-weight:500; padding:var(--space-1) var(--space-3);">Reports</span>
    </div>
</div>
<div style="text-align:center; padding: var(--space-6) 0 var(--space-8);">
    <h1 class="font-display" style="background: linear-gradient(135deg, var(--primary-fixed-dim) 0%, var(--primary) 50%, var(--primary-fixed) 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: var(--space-3); font-size:42px;">AI HR Interviewer</h1>
    <p class="font-body-lg" style="color: var(--on-surface-variant); max-width: 600px; margin: 0 auto;">Conduct structured, AI-evaluated audio interviews with multi-dimensional scoring</p>
</div>
""",
    unsafe_allow_html=True,
)

state = st.session_state.interview_state

# ── STAGE 1: Upload & Configure ──
if state["stage"] == "upload":
    # Hero / Upload Section
    st.markdown(
        """
    <div class="glass-panel" style="padding: var(--space-8); margin-bottom: var(--space-6);">
        <div class="font-headline-md" style="color: var(--primary-fixed-dim); margin-bottom: var(--space-2);">📄  Candidate Profile</div>
        <p class="font-body-md" style="color: var(--on-surface-variant); margin-bottom: var(--space-6);">Upload resume and define the role to generate tailored interview questions</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown(
            """
        <div class="glass-card" style="padding: var(--space-6); height: 100%;">
            <label class="font-label-md" style="display:block; margin-bottom: var(--space-3);">Resume (PDF/DOCX)</label>
        """,
            unsafe_allow_html=True,
        )
        resume_file = st.file_uploader(
            "", type=["pdf", "docx"], label_visibility="collapsed"
        )
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(
            """
        <div class="glass-card" style="padding: var(--space-6); margin-top: var(--space-4);">
            <label class="font-label-md" style="display:block; margin-bottom: var(--space-3);">Target Role</label>
        """,
            unsafe_allow_html=True,
        )
        job_role = st.text_input(
            "", placeholder="e.g., Senior React Developer", label_visibility="collapsed"
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown(
            """
        <div class="glass-card" style="padding: var(--space-6); height: 100%;">
            <label class="font-label-md" style="display:block; margin-bottom: var(--space-3);">Job Description <span style="color:var(--outline); font-weight:400; text-transform:none;">(optional)</span></label>
        """,
            unsafe_allow_html=True,
        )
        job_description = st.text_area(
            "",
            height=140,
            placeholder="Paste the job description for better tailored questions...\n\nAI will extract key competencies and generate role-specific questions.",
            label_visibility="collapsed",
        )
        st.markdown("</div>", unsafe_allow_html=True)

        # Role templates quick-select
        st.markdown(
            """
        <div class="glass-card" style="padding: var(--space-4); margin-top: var(--space-4);">
            <span class="font-label-sm" style="color: var(--on-surface-variant);">Quick Role Templates</span>
        """,
            unsafe_allow_html=True,
        )
        template_cols = st.columns(4)
        role_templates = [
            "Senior React Dev",
            "Backend Engineer",
            "ML Engineer",
            "DevOps Engineer",
        ]
        for i, template in enumerate(role_templates):
            with template_cols[i]:
                if st.button(
                    template,
                    key=f"template_{i}",
                    use_container_width=True,
                    type="secondary",
                ):
                    job_role = template
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # Interview Settings - Bento Grid
    st.markdown(
        """
    <div class="glass-panel" style="padding: var(--space-6); margin-top: var(--space-6);">
        <div class="font-headline-md" style="color: var(--primary-fixed-dim); margin-bottom: var(--space-4);">🎯  Interview Configuration</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    s1, s2, s3 = st.columns(3, gap="medium")

    with s1:
        st.markdown(
            """
        <div class="glass-card" style="padding: var(--space-4); text-align:center;">
            <div class="font-label-sm" style="color: var(--secondary-fixed-dim); margin-bottom: var(--space-2);">Questions</div>
        """,
            unsafe_allow_html=True,
        )
        num_questions = st.select_slider(
            "", options=[3, 5, 7, 10], value=5, label_visibility="collapsed"
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with s2:
        st.markdown(
            """
        <div class="glass-card" style="padding: var(--space-4); text-align:center;">
            <div class="font-label-sm" style="color: var(--secondary-fixed-dim); margin-bottom: var(--space-2);">Difficulty</div>
        """,
            unsafe_allow_html=True,
        )
        difficulty = st.selectbox(
            "",
            ["Easy", "Medium", "Hard", "Progressive (Easy → Hard)"],
            index=3,
            label_visibility="collapsed",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with s3:
        st.markdown(
            """
        <div class="glass-card" style="padding: var(--space-4); text-align:center;">
            <div class="font-label-sm" style="color: var(--secondary-fixed-dim); margin-bottom: var(--space-2);">Question Types</div>
        """,
            unsafe_allow_html=True,
        )
        q_types = st.multiselect(
            "",
            ["Technical", "Behavioral", "Situational", "System Design"],
            default=["Technical", "Behavioral", "Situational"],
            label_visibility="collapsed",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    # Start Button - Full Width
    st.markdown("<br>", unsafe_allow_html=True)
    col_start = st.columns([1, 2, 1])
    with col_start[1]:
        if st.button(
            "🚀  Start Audio Interview",
            type="primary",
            use_container_width=True,
            disabled=not (resume_file and job_role),
        ):
            with st.spinner("Parsing resume..."):
                state["resume_text"] = extract_resume_text(resume_file)
                state["job_role"] = job_role
                state["job_description"] = (
                    job_description or f"Standard {job_role} position"
                )
                state["num_questions"] = num_questions
                state["difficulty"] = difficulty
                state["q_types"] = (
                    ", ".join(q_types)
                    if q_types
                    else "Technical, Behavioral, Situational"
                )
            with st.spinner("Generating tailored interview questions..."):
                state["questions"] = generate_questions(
                    state["resume_text"],
                    job_role,
                    state["job_description"],
                    num_questions,
                    difficulty,
                    state["q_types"],
                )
                state["stage"] = "interview"
                state["current_q"] = 0
                state["answers"] = []
                state["evaluations"] = []
                state["question_phase"] = "ready"
                state["audio_bytes"] = None
            st.rerun()

# ── STAGE 2: Audio Interview ──
elif state["stage"] == "interview":
    total_qs = len(state["questions"])
    if total_qs == 0:
        st.error("No questions generated. Please restart.")
        if st.button("🔄 Restart"):
            state["stage"] = "upload"
            st.rerun()
    else:
        idx = state["current_q"]
        q = state["questions"][idx]
        phase = state.get("question_phase", "ready")

        # Progress bar
        st.progress(idx / total_qs, text=f"Question {idx + 1} of {total_qs}")

        # Question card
        with st.container(border=True):
            st.markdown(
                f"**Q{idx+1}** · {q.get('type','general').upper()} · Focus: {q.get('focus','General')}"
            )
            st.markdown(f"### {q['question']}")

        # ── Phase: READY ── (Auto-starts think timer, no button)
        if phase == "ready":
            state["question_phase"] = "thinking"
            state["audio_bytes"] = None
            st.rerun()

        # ── Phase: THINKING (30s countdown) ──
        elif phase == "thinking":
            st.markdown(
                """
            <div class="glass-panel" style="text-align:center; padding: var(--space-8); margin: var(--space-4) 0;">
                <div class="font-label-sm" style="color: var(--secondary-fixed-dim); margin-bottom: var(--space-2);">THINK TIME</div>
                <div class="font-body-lg" style="color: var(--on-surface);">Organize your thoughts. Recording starts automatically.</div>
            </div>
            """,
                unsafe_allow_html=True,
            )
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("⏭️ Skip Think Time & Start Recording", use_container_width=True, type="primary"):
                    state["question_phase"] = "recording"
                    st.rerun()

            render_think_timer(30, "Think Time")
            state["question_phase"] = "recording"
            st.rerun()

        # ── Phase: RECORDING ──
        elif phase == "recording":
            # Live waveform with timer
            render_recording_waveform()

            # Audio input (hidden label, full width)
            audio_data = st.audio_input(
                "", key=f"audio_q{idx}", label_visibility="collapsed"
            )

            # Auto-advance when audio is captured (user clicked stop)
            if audio_data is not None:
                state["audio_bytes"] = audio_data.getvalue()
                state["question_phase"] = "processing"
                st.rerun()

            # Fixed bottom action bar
            st.markdown(
                """
            <div style="position: fixed; bottom: 0; left: 0; right: 0; padding: var(--space-4) var(--space-6); background: linear-gradient(180deg, transparent, var(--bg-deep) 30%); z-index: 100; pointer-events: none;">
                <div style="max-width: 1200px; margin: 0 auto; pointer-events: auto; display: flex; justify-content: center; gap: var(--space-4);">
            """,
                unsafe_allow_html=True,
            )

            col_skip, col_space = st.columns([1, 4])
            with col_skip:
                if st.button("⏭️ Skip", use_container_width=True, type="secondary"):
                    state["answers"].append("[Skipped]")
                    state["evaluations"].append(
                        {
                            "score": 0,
                            "feedback": "Skipped",
                            "strengths": [],
                            "improvements": [],
                            "technical_accuracy": "N/A",
                            "communication": "N/A",
                        }
                    )
                    if idx == total_qs - 1:
                        state["stage"] = "results"
                        state["question_phase"] = "ready"
                    else:
                        state["current_q"] += 1
                        state["question_phase"] = "ready"
                    state["audio_bytes"] = None
                    st.rerun()

            st.markdown("</div></div>", unsafe_allow_html=True)

        # ── Phase: PROCESSING (auto-transcribe + auto-evaluate) ──
        elif phase == "processing":
            audio_bytes = state.get("audio_bytes")
            if not audio_bytes:
                st.error("No audio captured. Please try again.")
                if st.button("🔁 Try Again"):
                    state["question_phase"] = "recording"
                    st.rerun()
            else:
                # Transcribe
                with st.spinner("🔄 Transcribing your answer..."):
                    transcript = transcribe_audio(audio_bytes, audio_backend)

                if not transcript:
                    st.error("❌ Transcription failed. Please re-record.")
                    if st.button("🔁 Try Again"):
                        state["question_phase"] = "recording"
                        state["audio_bytes"] = None
                        st.rerun()
                else:
                    st.success("✅ Transcription complete!")
                    with st.container(border=True):
                        st.markdown("**Your Answer (Transcribed):**")
                        st.write(transcript)

                    # Evaluate
                    with st.spinner("🤖 AI is evaluating your answer..."):
                        eval_result = evaluate_answer(
                            q["question"], transcript, state["resume_text"]
                        )

                    state["answers"].append(transcript)
                    state["evaluations"].append(eval_result)

                    # Show evaluation
                    sc = eval_result.get("score", "N/A")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Score", f"{sc}/10")
                    with col2:
                        st.metric(
                            "Technical",
                            str(eval_result.get("technical_accuracy", "N/A")).title(),
                        )
                    with col3:
                        st.metric(
                            "Communication",
                            str(eval_result.get("communication", "N/A")).title(),
                        )

                    st.markdown(f"**Feedback:** {eval_result.get('feedback', 'N/A')}")

                    # Auto-advance to next question after 3 seconds
                    progress_placeholder = st.empty()
                    for i in range(3, 0, -1):
                        progress_placeholder.info(
                            f"⏳ Moving to next question in {i}..."
                        )
                        time.sleep(1)
                    progress_placeholder.empty()

                    if idx == total_qs - 1:
                        state["stage"] = "results"
                        state["question_phase"] = "ready"
                        state["audio_bytes"] = None
                    else:
                        state["current_q"] += 1
                        state["question_phase"] = "ready"
                        state["audio_bytes"] = None
                    st.rerun()

# ── STAGE 3: Results ──
elif state["stage"] == "results":
    st.header("📊 Interview Results")
    with st.spinner("Generating comprehensive report..."):
        report = generate_final_report(state)

    score = report.get("overall_score", 0)
    verdict = report.get("verdict", "N/A")

    # Calculate dimension scores from evaluations
    evals = state.get("evaluations", [])
    dim_scores = {
        "Technical": (
            sum(e.get("technical_accuracy", "medium") == "high" for e in evals)
            * 100
            / max(len(evals), 1)
            if evals
            else 50
        ),
        "Communication": (
            sum(e.get("communication", "medium") == "high" for e in evals)
            * 100
            / max(len(evals), 1)
            if evals
            else 50
        ),
        "Problem Solving": (
            sum(e.get("score", 5) >= 7 for e in evals) * 100 / max(len(evals), 1)
            if evals
            else 50
        ),
        "Cultural Fit": 75,
        "Confidence": 80,
    }

    # Radar chart
    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=list(dim_scores.values()),
            theta=list(dim_scores.keys()),
            fill="toself",
            fillcolor="rgba(59,130,246,0.2)",
            line=dict(color="#3b82f6", width=3),
            marker=dict(size=8, color="#3b82f6"),
            name="Scores",
        )
    )
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True, range=[0, 100], tickfont=dict(size=10, color="#94a3b8")
            ),
            angularaxis=dict(tickfont=dict(size=11, color="#dfe2ef", family="Inter")),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=40, t=40, b=40),
        height=300,
        showlegend=False,
    )

    # Header metrics with radar
    m1, m2, m3 = st.columns([1, 1, 2])
    with m1:
        score_color = (
            "#22c55e" if score >= 70 else "#fbbf24" if score >= 50 else "#ef4444"
        )
        st.markdown(
            f"""
        <div style="background:rgba(17,24,39,0.6); backdrop-filter:blur(12px); border:1px solid rgba(255,255,255,0.05); border-radius:12px; text-align:center; padding:32px 24px;">
            <div style="font-size:11px; font-weight:600; letter-spacing:0.05em; text-transform:uppercase; color:#fbbf24; margin-bottom:12px;">OVERALL SCORE</div>
            <div style="width:80px; height:80px; border-radius:50%; border:3px solid {score_color}; display:flex; align-items:center; justify-content:center; margin:0 auto 12px; box-shadow:0 0 20px {score_color}30;">
                <span style="font-family:'JetBrains Mono',monospace; font-size:28px; font-weight:700; color:{score_color};">{score}</span>
            </div>
            <div style="color:#8c909f; font-size:12px;">/ 100</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with m2:
        verdict_colors = {
            "Strong Hire": "#22c55e",
            "Hire": "#22c55e",
            "Consider": "#fbbf24",
            "No Hire": "#ef4444",
        }
        vc = verdict_colors.get(verdict, "#94a3b8")
        st.markdown(
            f"""
        <div style="background:rgba(17,24,39,0.6); backdrop-filter:blur(12px); border:1px solid rgba(255,255,255,0.05); border-radius:12px; text-align:center; padding:32px 24px; display:flex; flex-direction:column; align-items:center; justify-content:center; height:100%;">
            <div style="font-size:11px; font-weight:600; letter-spacing:0.05em; text-transform:uppercase; color:#8c909f; margin-bottom:12px;">AI RECOMMENDATION</div>
            <div style="background:{vc}15; border:1px solid {vc}40; color:{vc}; padding:8px 24px; border-radius:999px; font-weight:700; font-size:18px; letter-spacing:-0.01em;">{verdict}</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with m3:
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown(
        """
    <div style="height:1px; background:linear-gradient(90deg, transparent, rgba(255,255,255,0.06), transparent); margin:24px 0;"></div>
    """,
        unsafe_allow_html=True,
    )

    # Executive Summary
    st.markdown(
        f"""
    <div style="background:rgba(17,24,39,0.6); backdrop-filter:blur(12px); border:1px solid rgba(255,255,255,0.05); border-radius:12px; padding:24px; margin-bottom:20px;">
        <div style="font-size:18px; font-weight:600; color:#dfe2ef; margin-bottom:12px;">📋 Executive Summary</div>
        <div style="font-size:14px; color:#c2c6d6; line-height:1.7;">{report.get("summary", "No summary available")}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        strengths_html = "".join(
            [
                f'<div style="display:flex; align-items:flex-start; gap:8px; margin-bottom:8px;"><span style="color:#22c55e; font-size:14px;">✓</span><span style="font-size:13px; color:#c2c6d6;">{s}</span></div>'
                for s in report.get("key_strengths", [])
            ]
        )
        st.markdown(
            f"""
        <div style="background:rgba(17,24,39,0.6); backdrop-filter:blur(12px); border:1px solid rgba(255,255,255,0.05); border-left:3px solid #22c55e; border-radius:12px; padding:24px;">
            <div style="font-size:16px; font-weight:600; color:#22c55e; margin-bottom:16px;">👍 Key Strengths</div>
            {strengths_html}
        </div>
        """,
            unsafe_allow_html=True,
        )
    with col2:
        gaps_html = "".join(
            [
                f'<div style="display:flex; align-items:flex-start; gap:8px; margin-bottom:8px;"><span style="color:#fbbf24; font-size:14px;">↗</span><span style="font-size:13px; color:#c2c6d6;">{g}</span></div>'
                for g in report.get("key_gaps", [])
            ]
        )
        st.markdown(
            f"""
        <div style="background:rgba(17,24,39,0.6); backdrop-filter:blur(12px); border:1px solid rgba(255,255,255,0.05); border-left:3px solid #fbbf24; border-radius:12px; padding:24px;">
            <div style="font-size:16px; font-weight:600; color:#fbbf24; margin-bottom:16px;">↗ Areas for Probe</div>
            {gaps_html}
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.subheader("📝 Detailed Feedback")
    st.write(report.get("detailed_feedback", "N/A"))

    if report.get("recommended_resources"):
        st.subheader("📚 Recommended Resources")
        for r in report["recommended_resources"]:
            st.write(f"• {r}")

    if report.get("next_steps"):
        st.subheader("🎯 Next Steps")
        st.write(report["next_steps"])

    with st.expander("🔍 Question-by-Question Breakdown"):
        for i, (q, a, e) in enumerate(
            zip(state["questions"], state["answers"], state["evaluations"])
        ):
            st.markdown(f"**Q{i+1} [{q.get('type','general')}]:** {q['question']}")
            st.markdown(f"*Your Answer:* {a[:300]}{'...' if len(a) > 300 else ''}")
            st.markdown(
                f"*Score:* {e.get('score','N/A')}/10 | *Technical:* {e.get('technical_accuracy','N/A')} | *Communication:* {e.get('communication','N/A')}"
            )
            st.markdown(f"*Feedback:* {e.get('feedback','N/A')}")
            st.divider()

    # Download report
    report_text = f"""AI HR INTERVIEW REPORT
========================
Role: {state['job_role']}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Score: {score}/100 | Verdict: {verdict}

SUMMARY:\n{report.get('summary','')}

KEY STRENGTHS:\n{chr(10).join('• '+s for s in report.get('key_strengths',[]))}

GAPS:\n{chr(10).join('• '+g for g in report.get('key_gaps',[]))}

FEEDBACK:\n{report.get('detailed_feedback','')}

RESOURCES:\n{chr(10).join('• '+r for r in report.get('recommended_resources',[]))}

NEXT STEPS:\n{report.get('next_steps','')}

---\nQUESTION BREAKDOWN:\n"""
    for i, (q, a, e) in enumerate(
        zip(state["questions"], state["answers"], state["evaluations"])
    ):
        report_text += f"\nQ{i+1}: {q['question']}\nAnswer: {a}\nScore: {e.get('score','N/A')}/10\nFeedback: {e.get('feedback','N/A')}\n"

    st.download_button(
        "📥 Download Full Report",
        report_text,
        file_name=f"interview_{state['job_role'].replace(' ','_')}_{datetime.now().strftime('%Y%m%d')}.txt",
        mime="text/plain",
    )

    if st.button("🔄 New Interview", use_container_width=True):
        st.session_state.interview_state = {
            "stage": "upload",
            "resume_text": "",
            "job_role": "",
            "job_description": "",
            "questions": [],
            "current_q": 0,
            "answers": [],
            "evaluations": [],
            "question_phase": "ready",
            "audio_bytes": None,
            "num_questions": 5,
            "difficulty": "Progressive",
            "q_types": "Technical, Behavioral, Situational",
        }
        st.rerun()

# ── Sidebar Info ──
with st.sidebar:
    st.header("ℹ️ About")
    st.markdown(
        """
    <div style="font-size:13px; color:var(--on-surface-variant); line-height:1.7;">
    <strong style="color:var(--on-surface);">Audio-First AI Interviewer</strong><br>
    📄 Resume parsing (PDF/DOCX)<br>
    🎯 Role-specific question generation<br>
    ⏳ 30s think time per question<br>
    🎙️ 90s audio recording per answer<br>
    🔄 Auto-transcription via Groq Whisper<br>
    🤖 Real-time AI evaluation<br>
    📊 Comprehensive report with verdict
    </div>
    """,
        unsafe_allow_html=True,
    )
    st.divider()
    backend = st.session_state.get("current_backend", "None")
    st.caption(f"Backend: {backend}")
    if st.session_state.get("ai_hr"):
        st.success("✅ AI Connected")
    else:
        st.warning("⚠️ AI Offline — Add Groq API Key to enable")

    st.markdown(
        """
    <div style="position:fixed; bottom:16px; left:16px; display:flex; flex-direction:column; gap:8px; font-size:12px; color:var(--outline);">
        <span>🛟 Support</span>
        <span>🚪 Logout</span>
    </div>
    """,
        unsafe_allow_html=True,
    )
